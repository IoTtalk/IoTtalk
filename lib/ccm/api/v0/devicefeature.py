"""
DeviceFeature Module.

    _search_device_feature
    _get_device_feature
    _delete_device_feature
    _crate_df_parameters

    create
    list_
    get
    get_by_name
    update
    delete
    delete_by_name
"""
import datetime
import logging

import db

from flask import g, request

from ccm.api.utils import (blueprint, invalid_input,
                           json_data, json_error, record_parser)

api = blueprint(__name__, __file__)
log = logging.getLogger("ccm.api.v0.api")
DF_FORMAT = {
    'required': {
        'df_type': str,
        'df_name': str,
        'df_parameter': list},
    'optional': {
        'comment': str,
        'df_category': str,
    },
}


def _search_device_feature(df_name):
    """
    Seach Device Feature by name.

    If in use, return df_id, else return None.

    :param df_name: <DeviceFeature.df_name>
    :type df_name: str

    :return:
        <DeviceFeature.df_id> / None
    """
    df_record = (g.session.query(db.DeviceFeature)
                          .filter(db.DeviceFeature.df_name == df_name)
                          .first())
    return (df_record.df_id if df_record else None)


def _get_device_feature(df_id):
    session = g.session

    # query DeviceFeature
    df_record = (session.query(db.DeviceFeature)
                        .filter(db.DeviceFeature.df_id == df_id)
                        .first())

    if not df_record:
        return json_error('Device Feature id {} not found'.format(df_id))

    df_info = record_parser(df_record)
    df_info['df_parameter'] = []

    # query DF_parameter
    dfp_records = (session.query(db.DF_Parameter)
                          .filter(db.DF_Parameter.mf_id.is_(None),
                                  db.DF_Parameter.df_id == df_id,
                                  db.DF_Parameter.u_id.is_(None))
                          .order_by(db.DF_Parameter.param_i)
                          .all())

    for dfp in dfp_records:
        df_info['df_parameter'].append(record_parser(dfp))

    return json_data(data=df_info)


def _delete_device_feature(df_id):
    session = g.session

    # check DeviceFeature is exist.
    df_record = (session.query(db.DeviceFeature)
                        .filter(db.DeviceFeature.df_id == df_id)
                        .first())
    if df_record is None:
        return json_error('Device Feature not found')

    # check in use
    mf_records = (session.query(db.DM_DF)
                         .filter(db.DM_DF.df_id == df_id)
                         .all())
    dfo_records = (session.query(db.DFObject)
                          .filter(db.DFObject.df_id == df_id)
                          .all())

    if mf_records or dfo_records:
        return json_error('Device Feature is in use.')

    # delete DF_Parameter
    (session.query(db.DF_Parameter)
            .filter(db.DF_Parameter.df_id == df_id)
            .delete())

    # delete FunctionSDF
    (session.query(db.FunctionSDF)
            .filter(db.FunctionSDF.df_id == df_id)
            .delete())

    # delete DeviceFeature
    (session.query(db.DeviceFeature)
            .filter(db.DeviceFeature.df_id == df_id)
            .delete())
    session.commit()

    return json_data(df_id=df_id)


def _crate_df_parameters(df_id, df_type, dfps):
    session = g.session
    for idx, dfp in enumerate(dfps):
        new_dfp = db.DF_Parameter(
            df_id=df_id,
            mf_id=None,
            param_i=idx,
            param_type=dfp.get('param_type', 'int'),
            u_id=None,
            idf_type=dfp.get('idf_type', 'sample'),
            fn_id=dfp.get('fn_id', None),
            min=dfp.get('min', 0),
            max=dfp.get('max', 0),
            unit_id=dfp.get('unit_id', 1),  # 1 for None
            normalization=dfp.get('normalization', 0),
        )
        session.add(new_dfp)
        session.commit()

        # set odf data mapping, only in v1
        if df_type == 'output':
            # checkout function "x<i>"
            fn_name = 'x{}'.format(idx + 1)
            fn_record = (session.query(db.Function)
                                .filter(db.Function.fn_name == fn_name)
                                .first())

            if fn_record is None:
                # 1. insert new entry into Function
                new_function = db.Function(fn_name=fn_name)
                session.add(new_function)
                session.commit()

                # 2. insert relevant info into FunctionVersion
                code = 'def run(*args):\n    return args[{}]'.format(idx)
                function_version = db.FunctionVersion(
                    fn_id=new_function.fn_id,
                    completeness=1,
                    date=datetime.date.today(),
                    code=code,
                    is_switch=0,
                    non_df_args='')
                session.add(function_version)
                session.commit()

                fn_id = new_function.fn_id
            else:
                fn_id = fn_record.fn_id

            # save FuntionSDF fo odf
            new_fsdf = db.FunctionSDF(
                fn_id=fn_id,
                df_id=df_id,
                u_id=1,
                display=1
            )
            session.add(new_fsdf)
            session.commit()


@api.route('/', methods=['PUT'], strict_slashes=False)
def create():
    """
    Create a new DeviceFeature.

    Request:

        {
            "sta"
            "df_type": "input|output",
            "df_name": "Foo",
            "df_parameter": [
                {
                    "max": 1.0,  // optional
                    "min": 0.0,  // optional
                    "param_type": "float",
                },
                ...
            ],
            "comment": "42",  // optional
            "df_category": "other",  // optional
        }

    Response:

        {
            'state': 'ok',
            'df_id': 42,
        }
    """
    err = invalid_input(request.json, **DF_FORMAT)
    if err:
        return json_error(err), 400

    session = g.session

    df_name = request.json.get('df_name').strip()
    df_type = request.json.get('df_type')
    df_parameters = request.json.get('df_parameter', [])

    df_comment = request.json.get('comment', '')
    df_category = request.json.get('df_category', 'other')

    if not df_name:
        return json_error('df_name is required.')

    df_record = (session.query(db.DeviceFeature)
                        .filter(db.DeviceFeature.df_name == df_name)
                        .first())
    if df_record is not None:
        return json_error('Device Feature "{}" already exists'.format(df_name))

    if df_type not in ('input', 'output'):
        return json_error('Invalid feature type "{}"'.format(df_type))

    # create new DeviceFeature
    new_df = db.DeviceFeature(
        df_name=df_name,
        df_type=df_type,
        df_category=df_category,
        param_no=len(df_parameters),
        comment=df_comment)
    session.add(new_df)
    session.commit()

    df_id = new_df.df_id

    # save dfp
    _crate_df_parameters(df_id, df_type, df_parameters)

    return json_data(df_id=df_id)


@api.route('/', methods=['GET'], strict_slashes=False)
def list_():
    """
    List all DeviceFeautre.

    Response:

        {
            'state': 'ok',
            'input': [...],
            'output': [...],
        }
    """
    df_records = (g.session
                   .query(db.DeviceFeature)
                   .order_by(db.DeviceFeature.df_name)
                   .all())

    result = {
        'input': [],
        'output': []
    }
    for df_record in df_records:
        result[df_record.df_type].append(record_parser(df_record))

    return json_data(**result)


@api.route('/<int:df_id>', methods=['GET'], strict_slashes=False)
def get(df_id):
    """
    Get detailed information about DeviceFeature by df_id.

    Response:

        {
            'state': 'ok',
            'data': {
                ...
            },
        }
    """
    return _get_device_feature(df_id)


@api.route('/<string:df_name>', methods=['GET'], strict_slashes=False)
def get_by_name(df_name):
    """
    Get detailed information about DeviceFeature by df_name.

    Response:

        {
            'state': 'ok',
            'data': {
                ...
            },
        }
    """
    return _get_device_feature(_search_device_feature(df_name))


@api.route('/<int:id_>', methods=['POST'], strict_slashes=False)
def update(df_id):
    """
    Request format is same as ``create``.

    Response:

        {
            'state': 'ok',
            'df_id': 42,
        }

    Response if the id not found:

        {
            'state': 'error',
            'reason': 'Device Feature not found',
        }
    """
    err = invalid_input(request.json, **DF_FORMAT)
    if err:
        return json_error(err), 400

    session = g.session

    df_name = request.json.get('df_name').strip()
    df_type = request.json.get('df_type')
    df_parameters = request.json.get('df_parameter', [])

    df_comment = request.json.get('comment', '')
    df_category = request.json.get('df_category', 'other')

    if not df_name:
        return json_error('df_name is required.')

    df_record = (session.query(db.DeviceFeature)
                        .filter(db.DeviceFeature.df_name == df_name,
                                db.DeviceFeature.df_type == df_type)
                        .first())
    if df_record is None:
        return json_error('Device Feature not found.'.format(df_name))

    # update DeviceFeature
    df_record.df_category = df_category
    df_record.comment = df_comment
    session.commit()

    # delete old entries in DF_Parameter
    (session.query(db.DF_Parameter)
            .filter(db.DF_Parameter.u_id.is_(None),
                    db.DF_Parameter.mf_id.is_(None),
                    db.DF_Parameter.df_id == df_id)
            .delete())
    (session.query(db.FunctionSDF)
            .filter(db.FunctionSDF.df_id == df_id)
            .delete())
    session.commit()

    # save dfp
    _crate_df_parameters(df_id, df_type, df_parameters)

    return json_data(df_id=df_id)


@api.route('/<int:df_id>', methods=['DELETE'], strict_slashes=False)
def delete(df_id):
    """
    Delete a DeviceFeature by df_id.

    Response:

        {
            'state': 'ok',
            'df_id': 42,
        }
    """
    return _delete_device_feature(df_id)


@api.route('/<string:df_name>', methods=['DELETE'], strict_slashes=False)
def delete_by_name(df_name):
    """
    Delete a DeviceFeature by df_name.

    Response:

        {
            'state': 'ok',
            'df_id': 42,
        }
    """
    return _delete_device_feature(_search_device_feature(df_name))
