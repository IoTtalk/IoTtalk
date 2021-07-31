"""
DeviceObject Module.

    _generate_do_idx
    _create_do
    _create_dfo
    _delete_do
    _delete_dfo
    _classificate_df
    _classificate_df_by_name

    create
    get
    update
    delete
"""
import json
import logging

import ControlChannel
import db

from flask import g, request
from sqlalchemy import func

from ccm.api.utils import blueprint, invalid_input, json_data, json_error
from .devicemodel import _get_device_model
from .networkapplication import adjust_na, set_link_color
from .project import reopen_project

api = blueprint(__name__, __file__)
log = logging.getLogger("ccm.api.v0.api")


def _generate_do_idx(p_id, df_type):
    """TODO: May cause race condition."""
    session = g.session

    # generate new do_idx, the show order on the GUI in v1
    do_idx = None
    if df_type == 'input':
        # input DeviceObject do_idx
        do_idx = (session.query(func.max(db.DeviceObject.do_idx))
                         .filter(db.DeviceObject.p_id == p_id)
                         .first()[0])

        if do_idx is not None and do_idx > 0:
            do_idx += 1
        else:
            do_idx = 1
    elif df_type == 'output':
        # output DeviceObject do_idx
        do_idx = (session.query(func.min(db.DeviceObject.do_idx))
                         .filter(db.DeviceObject.p_id == p_id)
                         .first()[0])
        if do_idx is not None and do_idx < 0:
            do_idx -= 1
        else:
            do_idx = -1

    return do_idx


def _create_do(p_id, dm_id, do_idx, df_list):
    session = g.session

    # create new DeviceObject
    new_do = db.DeviceObject(
        p_id=p_id,
        dm_id=dm_id,
        d_id=None,
        do_idx=do_idx,
    )
    session.add(new_do)
    session.commit()

    # save DFObject
    _create_dfo(new_do.do_id, df_list)

    return new_do.do_id


def _create_dfo(do_id, df_list):
    session = g.session

    # save DFObject
    for df in df_list:
        new_dfo = db.DFObject(
            do_id=do_id,
            df_id=df.df_id,
            alias_name=df.df_name,
        )
        session.add(new_dfo)

    session.commit()


def _delete_do(do_id, p_id):
    session = g.session

    # turn other NetworkApplications black
    set_link_color(p_id=p_id)

    # get all DFObject
    dfo_records = (session.query(db.DFObject)
                          .filter(db.DFObject.do_id == do_id)
                          .all())

    # delete DFObject and DF_Module
    _delete_dfo(dfo_records)

    # delete DeviceObject
    (session.query(db.DeviceObject)
            .filter(db.DeviceObject.do_id == do_id)
            .delete())
    session.commit()


def _delete_dfo(dfo_list):
    session = g.session

    for dfo in dfo_list:
        # get all NetworkApplication which connected
        na_records = (session.query(db.NetworkApplication)
                             .select_from(db.NetworkApplication)
                             .join(db.DF_Module)
                             .join(db.DFObject)
                             .filter(db.DFObject.dfo_id == dfo.dfo_id)
                             .group_by(db.NetworkApplication.na_id)
                             .all())

        # delete DF_Module
        (session.query(db.DF_Module)
                .filter(db.DF_Module.dfo_id == dfo.dfo_id)
                .delete())
        session.commit()

        # delete MultipleJoin_Module
        (session.query(db.MultipleJoin_Module)
                .filter(db.MultipleJoin_Module.dfo_id == dfo.dfo_id)
                .delete())
        session.commit()

        # delete DFObject
        session.delete(dfo)
        session.commit()

        # check na still has at least one input and output
        for na in na_records:
            adjust_na(na.na_id)


def _classificate_df(df_list):
    session = g.session

    idf_list = []
    odf_list = []
    for df_id in df_list:
        # check df exist
        df_record = (session.query(db.DeviceFeature)
                            .filter(db.DeviceFeature.df_id == df_id)
                            .first())
        if df_record and df_record.df_type == 'input':
            idf_list.append(df_record)
        elif df_record and df_record.df_type == 'output':
            odf_list.append(df_record)

    return idf_list, odf_list


def _classificate_df_by_name(df_name_list):
    session = g.session

    idf_list = []
    odf_list = []
    for df_name in df_name_list:
        # check df exist
        df_record = (session.query(db.DeviceFeature)
                            .filter(db.DeviceFeature.df_name == df_name)
                            .first())
        if df_record and df_record.df_type == 'input':
            idf_list.append(df_record)
        elif df_record and df_record.df_type == 'output':
            odf_list.append(df_record)

    return idf_list, odf_list


@api.route('/', methods=['PUT'], strict_slashes=False)
def create(p_id):
    """
    Create a new DeviceObject.

    Note: V1 will separate the input and output DeviceFeature into two DeviceObjects.

    Request:

        {
            'dm_id': 42,  // Device Model id
            'df': [  // list of Device Feature id
                123,
                ...
            ],
        }

    Response:

        {
            'state': 'ok',
            'do_id': [42, 57]
        }

    Response error if Device Model or Device Feature not found:

        {
            'state': 'error',
            'reason': '... not found',
        }
    """
    err = invalid_input(request.json, {'dm_id': int, 'df': list})
    if err:
        return json_error(err)

    session = g.session

    dm_id = request.json.get('dm_id')
    df_list = request.json.get('df', [])

    # check exist
    dm_record = (session.query(db.DeviceModel)
                        .filter(db.DeviceModel.dm_id == dm_id)
                        .first())
    if not dm_record:
        return json_error('DeviceModel not found.')

    if not df_list:
        return json_error('DeviceFeature list (df) can\'t be empty.')

    do_id_list = []

    # classification df
    idf_list, odf_list = _classificate_df(df_list)

    # input DeviceObject
    if idf_list:
        # generate new do_idx, the show order on the GUI in v1
        do_idx = _generate_do_idx(p_id, 'input')

        # save new DeviceObject
        do_id_list.append(_create_do(p_id, dm_id, do_idx, idf_list))

    # odf
    if odf_list:
        # generate new do_idx, the show order on the GUI in v1
        do_idx = _generate_do_idx(p_id, 'output')

        # save new DeviceObject
        do_id_list.append(_create_do(p_id, dm_id, do_idx, odf_list))

    return json_data(do_id=do_id_list)


@api.route('/<int:do_id>/', methods=['GET'], strict_slashes=False)
def get(p_id, do_id):
    """
    Get detailed information about DeviceObject by do_id.

    Response:

        {
            'state': 'ok',
            'data': {
                'do': {
                    'do_id': 24,
                    'dfo': [...],
                },
                'dm_id': 42,
                'dm_name': 'FooModel',
                'dm_type': 'other',
                'df_list': [...],
            },
        }
    """
    session = g.session

    # check Device Object is exist
    do_record = (session.query(db.DeviceObject)
                        .filter(db.DeviceObject.do_id == do_id)
                        .first())

    if not do_record:
        return json_error('DeviceObject not found.')

    # get basic Deivce Model info
    result = json.loads(get_device_model(do_record.dm_id))
    result['do'] = {'do_id': do_id, 'dfo': []}

    # query DeviceFeatureObject's df_name
    df_records = (session.query(db.DeviceFeature)
                         .select_from(db.DeviceObject)
                         .join(db.DFObject)
                         .join(db.DeviceFeature)
                         .filter(db.DeviceObject.do_id == do_id)
                         .all())
    for df_record in df_records:
        result['do']['dfo'].append(df_record.df_name)

    # turn other NetworkApplications black
    set_link_color(p_id=p_id)

    return json_data(data=result)


@api.route('/<int:do_id>/', methods=['POST'], strict_slashes=False)
def update(p_id, do_id):
    """
    Update Device Object feature list.

    Note: In the V1, if the DeviceObject contains only input DeviceFeature,
          and updated list includes input and output DeviceFeature,
          then this function will update input list to this DeviceObject,
          and create a new DeviceObject contains output DeviceFeaute.
          The DeviceObject contains only output DeviceFeature is the same.

    Request:

        {
            'df': [
                ...  // list of Device Feature names
            ]
        }

    Response:

        {
            'state': 'ok',
            'do_id': 42,
        }
    """
    err = invalid_input(request.json, {'df': list})
    if err:
        return json_error(err)

    session = g.session
    df_name_list = request.json.get('df', [])

    # check Device Object is exist
    do_record = (
        session.query(db.DeviceObject)
        .filter(db.DeviceObject.do_id == do_id)
        .first()
    )
    if not do_record:
        return json_error('DeviceObject not found.')

    do_idx = do_record.do_idx

    # classification df
    idf_list, odf_list = _classificate_df_by_name(df_name_list)

    # check model type (input / output)
    if do_idx > 0:
        # input DeviceObject
        update_df_list = idf_list
        new_df_list = odf_list
        new_df_type = 'output'
    else:
        # output DeviceObject
        update_df_list = odf_list
        new_df_list = idf_list
        new_df_type = 'input'

    # query original DeviceFeature
    ori_df_list = (session.query(db.DeviceFeature)
                          .select_from(db.DFObject)
                          .join(db.DeviceFeature)
                          .filter(db.DFObject.do_id == do_id)
                          .all())

    # create new DeviceFeatureObject
    add_df_list = list(set(update_df_list).difference(set(ori_df_list)))
    _create_dfo(do_id, add_df_list)

    # delete DeviceFeatureObject
    delete_df_list = list(set(ori_df_list).difference(set(update_df_list)))
    _delete_dfo_list = [(session.query(db.DFObject)
                                .filter(db.DFObject.do_id == do_id,
                                        db.DFObject.df_id == df.df_id)
                                .first()) for df in delete_df_list]
    _delete_dfo(_delete_dfo_list)

    # if all device features deleted, remove the device Object
    if not add_df_list and len(delete_df_list) == len(ori_df_list):
        _delete_do(do_id, p_id)

    # Create new  DeviceObject for other df_type
    if new_df_list:
        do_idx = _generate_do_idx(p_id, new_df_type)
        _create_do(p_id, do_record.dm_id, do_idx, new_df_list)


    # turn other NetworkApplications black
    set_link_color(p_id=p_id)

    reopen_project(p_id)

    ControlChannel.SET_DF_STATUS(db, do_id)

    return json_data(do_id=do_id)


@api.route('/<int:do_id>/', methods=['DELETE'], strict_slashes=False)
def delete(p_id, do_id):
    """
    Delete an exist DeviceObject.

    Response:

        {
            'state': 'ok',
            'do_id': 42,
        }

    Response error if not found:

        {
            'state': 'error',
            'reason': 'Device Object 42 not found',
        }
    """
    _delete_do(do_id, p_id)
    reopen_project(p_id)

    return json_data(do_id=do_id)
