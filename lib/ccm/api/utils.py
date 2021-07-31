import datetime
import logging
import os

from flask import Blueprint, jsonify

log = logging.getLogger("ccm.api.utils")


def invalid_input(x: 'request.json', required: dict, optional: dict ={}):
    """
    Check the required field in the given json input.

    If invalid, returns the error message.
    If valid, returns empty string.

    :param required: a dictionary contains the required field and its type::

        {
            'field1': str,
            'field2': int,
            'field3': (int, type(None)),  // tuple only, list is not allowed
            ...
        }

    :param optional: the optional field
    """
    if x is None:
        return ('Content-type should be `application/json` and '
                'body should not be empty')

    # field existence
    for k in required:
        if k not in x:
            return 'field `{}` is required'.format(k)

    # check unknown keys
    keyset = set(required.keys()).union(optional.keys())
    for k in x.keys():
        if k not in keyset:
            return 'field `{}` unknown'.format(k)

    # check type
    for y in (required, optional):
        for k, types in y.items():
            if k not in x:
                continue

            types = (types,) if not isinstance(types, tuple) else types
            for typ in types:
                if isinstance(x[k], typ):
                    break
            else:
                return 'field `{}` should be type `{}`'.format(k, typ)

    # check str non-empty
    for k, v in x.items():
        if k not in required:  # skip check for optional fields
            continue
        if isinstance(v, str) and not v:
            return 'field `{}` should not be empty'.format(k)

    return ''  # ok


def blueprint(name: __name__, filename: __file__):
    """Simple wrapper for creating Blueprint of CCM HTTP APIs."""
    ver = os.path.split(os.path.dirname(filename))[-1]
    bname = '{}_api_{}'.format(name, ver)
    log.debug('create Blueprint %s', bname)
    return Blueprint(bname, name)


def json_error(msg: str, **other) -> jsonify:
    obj = {
        'state': 'error',
        'reason': msg,
    }
    obj.update(other)
    return jsonify(obj)


def json_data(**params):
    """Wrap a dictionary into field ``data``."""
    obj = {'state': 'ok'}
    obj.update(params)
    return jsonify(obj)


def record_parser(row, str_datetime=True):
    """Convert query object by sqlalchemy to dictionary object."""
    if not row:
        return None

    d = {}
    if hasattr(row, '__table__'):
        for column in row.__table__.columns:
            d[column.name] = getattr(row, column.name)
            if str_datetime and isinstance(d[column.name], datetime.datetime):
                d[column.name] = str(d[column.name])
    if hasattr(row, '_fields'):
        for column_name in row._fields:
            d[column_name] = getattr(row, column_name)
            if str_datetime and isinstance(d[column_name], datetime.datetime):
                d[column_name] = str(d[column_name])
    return d
