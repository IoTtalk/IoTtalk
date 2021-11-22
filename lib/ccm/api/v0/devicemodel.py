"""
DeviceModel Module.

    _search_device_model
    _check_dm_format
    _check_dm_inuse
    _get_device_model
    _delete_device_model
    _save_df_parameters

    create
    list_
    get
    get_by_name
    update
    delete
    delete_by_name
"""
import logging

import db

from flask import g, request

from ccm.api.utils import (blueprint, invalid_input,
                           json_data, json_error, record_parser)

api = blueprint(__name__, __file__)
log = logging.getLogger("ccm.api.v0.api")


def _search_device_model(dm_name):
    """
    Check DeviceModel name is in use.

    :param dm_name: <DeviceModel.dm_name>
    :return:
        <DeviceModel.dm_id> / None
    """
    dm_record = (g.session
                  .query(db.DeviceModel)
                  .filter(db.DeviceModel.dm_name == dm_name)
                  .first())
    return (dm_record.dm_id if dm_record else None)


def _check_dm_format(data):
    """Check device model format."""
    err = invalid_input(data,
                        {'dm_name': str, 'df_list': list},
                        {'dm_type': str})
    if err:
        return json_error(err)

    for x in data['df_list']:
        err = invalid_input(
            x,
            {'df_id': int, 'df_parameter': list},
            {'tags': list, 'df_category': str,
             'df_name': str, 'df_type': str,
             'comment': str, 'param_no': int})
        if err:
            return json_error(err)

    # correct df_id in df_parameter
    for x in data['df_list']:
        df_id = x['df_id']
        for y in x['df_parameter']:
            y['df_id'] = df_id

    return None


def _check_dm_inuse(dm_id):
    session = g.session
    do_records = (session.query(db.DeviceObject.dm_id)
                         .filter(db.DeviceObject.dm_id == dm_id)
                         .all())
    d_records = (session.query(db.Device.dm_id)
                        .filter(db.Device.dm_id == dm_id)
                        .all())
    return do_records or d_records


def _get_device_model(dm_id):
    session = g.session

    dm_record = (session.query(db.DeviceModel)
                        .filter(db.DeviceModel.dm_id == dm_id)
                        .first())

    if not dm_record:
        return json_error('Device Model not found.')

    dm_info = record_parser(dm_record)
    dm_info['df_list'] = []

    df_records = (session.query(db.DeviceFeature)
                         .select_from(db.DM_DF)
                         .join(db.DeviceFeature,
                               db.DeviceFeature.df_id == db.DM_DF.df_id)
                         .filter(db.DM_DF.dm_id == dm_id)
                         .order_by(db.DeviceFeature.df_name)
                         .all())

    for df in df_records:
        dm_info['df_list'].append(record_parser(df))

    return json_data(data=dm_info)


def _delete_device_model(dm_id):
    session = g.session

    # check exist
    dm_record = (session.query(db.DeviceModel)
                        .filter(db.DeviceModel.dm_id == dm_id)
                        .first())
    if not dm_record:
        return json_error('Device Model not found')

    # check in use
    if _check_dm_inuse(dm_id):
        return json_error('Device Model is in use.')

    # query DM_DF records
    mf_records = (session.query(db.DM_DF)
                         .filter(db.DM_DF.dm_id == dm_id)
                         .all())

    for mf_record in mf_records:
        # delete DF_Parameter
        (session.query(db.DF_Parameter)
                .filter(db.DF_Parameter.mf_id == mf_record.mf_id)
                .delete())
        session.commit()

        # delete DM_DF
        session.delete(mf_record)
        session.commit()

    # delete DeviceModel
    session.delete(dm_record)
    session.commit()

    return json_data(dm_id=dm_id)


def _save_df_parameters(df_id, mf_id, dfps):
    session = g.session
    ori_dfps = (session.query(db.DF_Parameter)
                       .filter(db.DF_Parameter.df_id == df_id)
                       .order_by(db.DF_Parameter.param_i.asc())
                       .all())

    while len(ori_dfps) > len(dfps):
        dfps.append({})

    # update/create device feature parameter
    for idx, (ori_dfp, dfp) in enumerate(zip(ori_dfps, dfps)):
        # try update first
        update_dfp = (session.query(db.DF_Parameter)
                             .filter(db.DF_Parameter.mf_id == mf_id,
                                     db.DF_Parameter.param_i == idx)
                             .update(dfp))

        session.commit()

        # if return value is 0 means update 0 rows, so create new one
        if update_dfp == 0:
            new_dfp = db.DF_Parameter(
                df_id=None,
                mf_id=mf_id,
                param_i=idx,
                param_type=dfp.get('param_type', ori_dfp.param_type),
                u_id=None,
                idf_type=dfp.get('idf_type', ori_dfp.idf_type),
                min=dfp.get('min', ori_dfp.min),
                max=dfp.get('max', ori_dfp.max),
                unit_id=dfp.get('unit_id', ori_dfp.unit_id),
                normalization=dfp.get('normalization', ori_dfp.normalization)
            )
            session.add(new_dfp)
            session.commit()

    # delete other parameter,
    # which param_i larger then number of given parameters
    (session.query(db.DF_Parameter)
            .filter(db.DF_Parameter.mf_id == mf_id,
                    db.DF_Parameter.param_i >= len(dfps))
            .delete())
    session.commit()


@api.route('/', methods=['PUT'], strict_slashes=False)
def create():
    """
    Create a new DeviceModel.

    Request:

        {
            'dm_name': 'Foo',
            'df_list': [
                {
                    'df_id': 12,  // required
                    'df_parameter': [{}, ...]  // required
                    'tags': [],  // optional
                },
                ...
            ],
            'dm_type': 'other',  // optional
        }

    Response:

        {
            'state': 'ok',
            'dm_id': 42,
        }

    Response if name already exists with HTTP code 400:

        {
            'state': 'error',
            'reason': 'Device Model "..." already exists',
        }

    Example:

        {
            "dm_name": "FooModel",
            "df_list": [
                {
                    "df_id": 12,
                    "df_parameter": [{}]
                }
            ]
        }
    """
    err = _check_dm_format(request.json)
    if err:
        return err

    session = g.session

    dm_name = request.json.get('dm_name').strip()
    df_list = request.json.get('df_list')
    dm_type = request.json.get('dm_type', 'other')

    # check dm_name
    if not dm_name:
        return json_error('dm_name is required.')

    if _search_device_model(dm_name):
        return json_error('Device Model "{}" already exists'.format(dm_name))

    # check df_list not empty
    if not df_list:
        return json_error('Feature list cannot be empty')

    # create new DeviceModel
    new_dm = db.DeviceModel(
        dm_name=dm_name,
        dm_type=dm_type
    )
    session.add(new_dm)
    session.commit()

    # create new DM_DF and DF_Parameter
    for df in df_list:
        df_id = df['df_id']
        # create new DM_DF
        new_mf = db.DM_DF(
            dm_id=new_dm.dm_id,
            df_id=df_id)
        session.add(new_mf)
        session.commit()

        # save DF_Parameter
        _save_df_parameters(df_id, new_mf.mf_id, df['df_parameter'])

    return json_data(dm_id=new_dm.dm_id)


@api.route('/', methods=['GET'], strict_slashes=False)
def list_():
    """
    Get all DeviceModel.

    Response:

        {
            'state': 'ok',
            'date': [
                {
                    // Device Model without Device Feature info
                },
                ...
            ],
        }
    """
    session = g.session
    dm_records = (session.query(db.DeviceModel)
                         .order_by(db.DeviceModel.dm_name)
                         .all())

    return json_data(data=[record_parser(dm) for dm in dm_records])


@api.route('/<int:dm_id>', methods=['GET'], strict_slashes=False)
def get(dm_id):
    """
    Get detailed information about DeviceModel by dm_id.

    Response:

        {
            'state': 'ok',
            'data': {
                'dm_id': 42,
                'dm_name': 'FooModel',
                'df_list': [...]
                'dm_type': 'other',
            },
        }

    Response if id not found with HTTP code 404:

        {
            'state': 'error',
            'reason': 'Device Model id "42" not found',
        }
    """
    return _get_device_model(dm_id)


@api.route('/<string:dm_name>', methods=['GET'], strict_slashes=False)
def get_by_name(dm_name):
    """
    Get detailed information about DeviceModel by dm_name.

    Response:

        {
            'state': 'ok',
            'data': {
                'dm_id': 42,
                'dm_name': 'FooModel',
                'df_list': [...]
                'dm_type': 'other',
            },
        }

    Response if id not found with HTTP code 404:

        {
            'state': 'error',
            'reason': 'Device Model id "42" not found',
        }
    """
    return _get_device_model(_search_device_model(dm_name))


# save_device_model
@api.route('/<int:dm_id>', methods=['POST'], strict_slashes=False)
def update(dm_id):
    """
    Request format is same as ``create``.

    Request:

        {
            'dm_name': 'name',  // immutable, only for verifying
            'df_list': [...],
            'dm_type': 'other',  // optional
            'plural': False, // optional
            'device_only': False //optional
        }

    Response:

        {
            'state': 'ok',
            'dm_id': 42,
        }
    """
    err = _check_dm_format(request.json)
    if err:
        return err

    session = g.session

    dm_name = request.json.get('dm_name').strip()
    df_list = request.json.get('df_list')
    dm_type = request.json.get('dm_type', 'other')

    # check exist
    dm_record = (session.query(db.DeviceModel)
                        .filter(db.DeviceModel.dm_id == dm_id,
                                db.DeviceModel.dm_name == dm_name)
                        .first())
    if not dm_record:
        return json_error('Device Model not found')

    # check in use
    if _check_dm_inuse(dm_id):
        return json_error('Device Model is in use.')

    # update DeviceModel
    dm_record.dm_type = dm_type
    session.commit()

    # query original DM_DF records
    ori_mf_records = (session.query(db.DM_DF)
                             .filter(db.DM_DF.dm_id == dm_id))
    ori_mf_records = {mf.df_id: mf for mf in ori_mf_records}

    # create/update DM_DF and DF_Parameter
    for df in df_list:
        df_id = int(df['df_id'])
        if df_id in ori_mf_records:
            # update DM_DF
            mf = ori_mf_records.pop(df_id)  # remove keeped df in original records
        else:
            # create new DM_DF
            mf = db.DM_DF(
                dm_id=dm_id,
                df_id=df_id)
            session.add(mf)
            session.commit()

        # save DF_Parameter
        _save_df_parameters(df_id, mf.mf_id, df['df_parameter'])

    # delete not use DF_Parameter, DM_DF from remaining original records
    for mf in ori_mf_records.values():
        (session.query(db.DF_Parameter)
                .filter(db.DF_Parameter.mf_id == mf.mf_id)
                .delete())
        session.delete(mf)
        session.commit()

    return json_data(dm_id=dm_id)


@api.route('/<int:dm_id>', methods=['DELETE'], strict_slashes=False)
def delete(dm_id):
    """
    Delete an exist DeviceModel by given dm_id.

    Response:

        {
            'state': 'ok',
            'dm_id': 42,
        }
    """
    return _delete_device_model(dm_id)


# check_device_model_name_is_exist
@api.route('/<string:dm_name>', methods=['DELETE'], strict_slashes=False)
def delete_by_name(dm_name):
    """
    Delete an exist DeviceModel by given dm_name.

    Response:

        {
            'state': 'ok',
            'dm_id': 42,
        }
    """
    return _delete_device_model(_search_device_model(dm_name))
