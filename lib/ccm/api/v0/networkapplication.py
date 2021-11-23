"""
NetworkApplication Module.

    _refresh_multiple_join_module

    adjust_na
    set_link_color

    create
    list_
    get
    update
    delete
"""
import logging

import db

from flask import g, request

import csmapi

from ccm.api.utils import invalid_input, blueprint
from ccm.api.utils import json_data, json_error, record_parser

api = blueprint(__name__, __file__)
log = logging.getLogger("ccm.api.v0.api")

def _refresh_multiple_join_module(na_id):
    session = g.session

    # delete MultipleJoin_Module and reset DF_Module normalization to 0
    mjm_records = (session.query(db.MultipleJoin_Module)
                          .filter(db.MultipleJoin_Module.na_id == na_id)
                          .all())
    for mjm in mjm_records:
        (session.query(db.DF_Module)
                .filter(db.DF_Module.dfo_id == mjm.dfo_id,
                        db.DF_Module.na_id == na_id)
                .update({'normalization': 0}))
        session.delete(mjm)
        session.commit()

    # Check the number of remaining input DF_Module
    idfm_records = (session.query(db.DF_Module)
                           .select_from(db.DF_Module)
                           .join(db.DFObject)
                           .join(db.DeviceObject)
                           .join(db.DeviceFeature)
                           .filter(db.DeviceFeature.df_type == 'input',
                                   db.DF_Module.na_id == na_id)
                           .group_by(db.DF_Module.dfo_id)
                           .order_by(db.DeviceObject.do_idx,
                                     db.DeviceFeature.df_name)
                           .all())

    if len(idfm_records) > 1:
        # more then one input DF_Module, rebuild new MultipleJoin_Module
        for idx, idfm in enumerate(idfm_records):
            new_mjm = db.MultipleJoin_Module(
                na_id=na_id,
                param_i=idx,
                dfo_id=idfm.dfo_id
            )
            session.add(new_mjm)
            session.commit()


def adjust_na(na_id):
    """
    Check if NetworkApplication is valid.

    This function will check NetworkApplication contains at least one
    input DeviceFeature and an output DeviceFeature.

    """
    session = g.session

    # update MultipleJoin_Module
    _refresh_multiple_join_module(na_id)

    # check if IDF # connected with the circle > 0, and delete single circles
    idfo_records = (session.query(db.DF_Module)
                           .select_from(db.DF_Module)
                           .join(db.DFObject)
                           .join(db.DeviceFeature)
                           .filter(db.DeviceFeature.df_type == 'input',
                                   db.DF_Module.na_id == na_id)
                           .group_by(db.DF_Module.dfo_id)
                           .all())
    odfo_records = (session.query(db.DF_Module)
                           .select_from(db.DF_Module)
                           .join(db.DFObject)
                           .join(db.DeviceFeature)
                           .filter(db.DeviceFeature.df_type == 'output',
                                   db.DF_Module.na_id == na_id)
                           .group_by(db.DF_Module.dfo_id)
                           .all())

    # remove the circle and all lines connected with it
    if idfo_records == 0 or odfo_records == 0:
        (session.query(db.DF_Module)
                .filter(db.DF_Module.na_id == na_id)
                .delete())
        session.commit()

        (session.query(db.MultipleJoin_Module)
                .filter(db.MultipleJoin_Module.na_id == na_id)
                .delete())
        session.commit()

        (session.query(db.NetworkApplication)
                .filter(db.NetworkApplication.na_id == na_id)
                .delete())
        session.commit()

        csmapi.dfm_reset(na_id, 0)


def set_link_color(color='black', p_id=None, na_id=None):
    """
    Set link's color in project(s) or join.

    :param color: 'black' / 'red',
    :param p_id: <Project.p_id>, optional
    :param na_id: '<NetworkApplication.na_id>, optional
    :type color: str
    :type p_id: int
    :type na_id: int
    """
    session = g.session

    if p_id:
        nas = (session.query(db.NetworkApplication.na_id)
                      .filter(db.NetworkApplication.p_id == p_id)
                      .subquery())
        (session.query(db.DF_Module)
                .filter(db.DF_Module.na_id.in_(nas))
                .update({'color': color},
                        synchronize_session=False))
    elif na_id:
        (session.query(db.DF_Module)
                .filter(db.DF_Module.na_id == na_id)
                .update({'color': color}))

    session.commit()


@api.route('/', methods=['PUT'], strict_slashes=False)
def create(p_id):
    """
    Create a new NetworkApplication.

    Request:

        {
            'na_name': 'JoinFoo',
            'na_idx': 0,  // for GUI displaying, starting from 0
            'dfo_ids': [
                ... // can be found in project info
            ]
        }

    Response:

        {
            'state': 'ok',
            'na_id': 42,
        }
    """
    err = invalid_input(request.json,
                        {'na_name': str, 'na_idx': int, 'dfo_ids': list})
    if err:
        return json_error(err)

    session = g.session
    na_name = request.json.get('na_name')
    na_idx = request.json.get('na_idx')
    dfo_ids = request.json.get('dfo_ids')

    # check na_idx
    na_record = (session.query(db.NetworkApplication)
                        .filter(db.NetworkApplication.na_idx == na_idx,
                                db.NetworkApplication.p_id == p_id)
                        .first())
    if na_record:
        return json_error('NetworkApplication\'s idx is already exist.')

    if len(dfo_ids) < 2:
        return json_error('NetworkApplication requires more then two dfo_id.')

    # create NetworkApplication
    new_na = db.NetworkApplication(
        na_name=na_name,
        p_id=p_id,
        na_idx=na_idx)

    session.add(new_na)
    session.commit()

    na_id = new_na.na_id

    # create DF_Modules by dfo_id
    for dfo_id in dfo_ids:
        # get some info
        (dm_id, df_id) = (session.query(db.DeviceObject.dm_id,
                                        db.DFObject.df_id)
                                 .select_from(db.DFObject)
                                 .join(db.DeviceObject)
                                 .filter(db.DFObject.dfo_id == dfo_id)
                                 .first())

        df_type, = (session.query(db.DeviceFeature.df_type)
                           .select_from(db.DeviceFeature)
                           .join(db.DFObject)
                           .filter(db.DFObject.dfo_id == dfo_id)
                           .first())

        # get basic DF_Parameter info
        dfp_records = (session.query(db.DF_Parameter)
                              .select_from(db.DM_DF)
                              .join(db.DF_Parameter)
                              .filter(db.DM_DF.dm_id == dm_id,
                                      db.DM_DF.df_id == df_id)
                              .all())

        # create DF_Modules
        for dfp_record in dfp_records:
            new_dfm = db.DF_Module(
                na_id=na_id,
                idf_type=dfp_record.idf_type,
                normalization=0 if df_type == 'input' else dfp_record.normalization,
                param_i=dfp_record.param_i,
                dfo_id=dfo_id,
                color='red',
                min=dfp_record.min,
                max=dfp_record.max)
            session.add(new_dfm)
            session.commit()

    # turn other connections black
    set_link_color(p_id=p_id)
    set_link_color(color='red', na_id=na_id)

    return json_data(na_id=na_id)


@api.route('/', methods=['GET'], strict_slashes=False)
def list_(p_id):
    """
    List all NetworkApplications in the specific Project.

    Response:

        {
            'state': 'ok',
            'p_id': 42,
            'data': [
                {
                    'na_id': '<NetworkApplication.na_id>',
                    'na_name': '<NetworkApplication.na_name>',
                    'na_idx': '<NetworkApplication.na_idx>',
                    'input': [ <dfm_info>, ...],
                    'output': [ <dfm_info>, ...],
                },
                ...
            ]
        }

        <dfm_info>: {
            'dfo_id': '<DFObject.dfo_id>',
            'color': 'black' / 'red', # line color
            'df_type': '<DeviceFeature.df_type>'
        }
    """
    session = g.session

    data = []

    # query NetworkApplication info
    na_records = (session.query(db.NetworkApplication)
                         .select_from(db.NetworkApplication)
                         .filter(db.NetworkApplication.p_id == p_id)
                         .all())

    for na_record in na_records:
        na = record_parser(na_record)
        na['input'] = []
        na['output'] = []

        # query DF_Module info
        dfm_records = (session.query(db.DF_Module.dfo_id,
                                     db.DF_Module.color,
                                     db.DeviceFeature.df_type)
                              .select_from(db.DF_Module)
                              .join(db.DFObject)
                              .join(db.DeviceFeature)
                              .filter(db.DF_Module.na_id == na_record.na_id)
                              .group_by(db.DF_Module.dfo_id)
                              .all())

        for dfm_record in dfm_records:
            na[dfm_record.df_type].append(record_parser(dfm_record))

        data.append(na)

    return json_data(p_id=p_id, data=data)


@api.route('/<int:na_id>', methods=['GET'], strict_slashes=False)
def get(p_id, na_id):
    """
    Get detailed information about NetworkApplication by na_id.

    Response:

        {
            'state': 'ok',
            'data':{
                'na_id': 42,
                'na_name': 'FooJoin',
                'na_idx': '0',
                'input': [ <dfm_info>, ...],
                'output': [ <dfm_info>, ...],
                'multiple': [ <multiplejion_info>, ...]
            }
        }

        <dfm_info>:
            {
                'dm_name': '<DeviceModel.dm_name>',
                'dfo_id': '<DFObject.dfo_id>',
                'alias_name': '<DFObject.alias_name>',
                'dfmp': [ <DF_Module>, ...],
            }

        <multiplejion_info>:
            {
                'dfo_id': '<DFObject.dfo_id>',
                'na_id': '<NetworkApplication.na_id>',
                'param_i': 'integer'
            }
    """
    session = g.session

    # check NetworkApplication is exist
    na_record = (session.query(db.NetworkApplication)
                        .filter(db.NetworkApplication.na_id == na_id,
                                db.NetworkApplication.p_id == p_id)
                        .first())

    if not na_record:
        return json_error('NetworkApplication not found.')

    result = record_parser(na_record)
    result['input'] = []
    result['output'] = []

    # get DF_Module info
    dfo_records = (
        session.query(db.DFObject.dfo_id,
                      db.DFObject.alias_name,
                      db.DFObject.df_id,
                      db.DeviceFeature.df_type,
                      db.DeviceFeature.df_name,
                      db.DeviceModel.dm_name,
                      db.Device.mac_addr,)
               .select_from(db.DF_Module)
               .join(db.DFObject)
               .join(db.DeviceFeature)
               .join(db.DeviceObject)
               .join(db.DeviceModel)
               .outerjoin(db.Device, db.Device.d_id == db.DeviceObject.d_id)
               .filter(db.DF_Module.na_id == na_id)
               .group_by(db.DFObject.dfo_id)
               .order_by(db.DFObject.do_id,
                         db.DeviceFeature.df_name)
               .all())

    for dfo_record in dfo_records:
        dfm_records = (session.query(db.DF_Module)
                              .filter(db.DF_Module.dfo_id == dfo_record.dfo_id,
                                      db.DF_Module.na_id == na_id)
                              .order_by(db.DF_Module.param_i)
                              .all())

        dfm_tmp = record_parser(dfo_record)
        dfm_tmp['dfmp'] = [record_parser(r) for r in dfm_records]

        result[dfo_record.df_type].append(dfm_tmp)

    # get MultipleJoin_Module info
    multiplejoin_records = (session.query(db.MultipleJoin_Module)
                                   .select_from(db.MultipleJoin_Module)
                                   .filter(db.MultipleJoin_Module.na_id == na_id)
                                   .order_by(db.MultipleJoin_Module.param_i)
                                   .all())
    result['multiple'] = [record_parser(r) for r in multiplejoin_records]

    # set gui link color
    set_link_color(color='black', p_id=p_id)
    set_link_color(color='red', na_id=na_id)

    return json_data(data=result)


@api.route('/<int:na_id>', methods=['POST'], strict_slashes=False)
def update(p_id, na_id):
    """
    Update NetworkApplication.

    Request:

        {
            'na_name': 'new name',  // optional
            'dfm_list': [  // optional, a list of `dfm_info`
                {
                    'dfo_id': 123,
                    'dfmp_list': [
                        ...,  // an instance of this list can be obtained
                              // from the return of the API
                              // `GET ../na/<na_id>/`.
                              // There are fields named `output[n].dfmp` and
                              // `input[n].dfmp`
                    ]
                },
                ...
            ],
        }

    Response:

        {
            'state': 'ok',
            'na_id': 42
        }
    """
    err = invalid_input(request.json, {}, {
        'na_name': str,
        'dfm_list': list})
    if err:
        return json_error(err)

    for x in request.json.get('dfm_list', []):
        err = invalid_input(x, {'dfo_id': int, 'dfmp_list': list}, {})
        if err:
            return json_error(err)

    session = g.session
    na_name = request.json.get('na_name')
    dfm_list = request.json.get('dfm_list')

    # check NetworkApplication is exist
    na_record = (session.query(db.NetworkApplication)
                        .filter(db.NetworkApplication.na_id == na_id,
                                db.NetworkApplication.p_id == p_id)
                        .first())

    if not na_record:
        return json_error('NetworkApplication not found.')

    # update na_name
    if na_name:
        na_record.na_name = na_name
        session.commit()

    # update dfm
    for dfm in dfm_list:
        for dfmp in dfm.get('dfmp_list', []):
            (session.query(db.DF_Module)
                    .filter(db.DF_Module.na_id == na_id,
                            db.DF_Module.dfo_id == dfm.get('dfo_id'),
                            db.DF_Module.param_i == dfmp.get('param_i'))
                    .update(dfmp))
            session.commit()

        csmapi.dfm_reset(na_id, dfm.get('dfo_id'))

    session.commit()

    # turn other NetworkApplications black
    set_link_color(p_id=p_id)
    set_link_color(color='red', na_id=na_id)

    return json_data(na_id=na_id)


@api.route('/<int:na_id>', methods=['DELETE'], strict_slashes=False)
def delete(p_id, na_id):
    """
    Delete an exist NetworkApplication.

    Response:

        {
            'state': 'ok',
            'na_id': 42,
        }
    """
    session = g.session

    # delete MultipleJoin_Module
    session.query(db.MultipleJoin_Module).filter(db.MultipleJoin_Module.na_id == na_id).delete()
    session.commit()

    # delete DF_Module
    session.query(db.DF_Module).filter(db.DF_Module.na_id == na_id).delete()
    session.commit()

    # delete NetworkApplication
    session.query(db.NetworkApplication).filter(db.NetworkApplication.na_id == na_id).delete()
    session.commit()

    return json_data(na_id=na_id)
