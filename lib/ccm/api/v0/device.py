"""
Device module.

    list_
    bind
    unbind
"""
import logging

import ControlChannel
import db

from flask import g

from ccm.api.utils import blueprint, json_data, json_error, record_parser
from .project import reopen_project

api = blueprint(__name__, __file__)
log = logging.getLogger("ccm.api.v0.api")


@api.route('/', methods=['GET'], strict_slashes=False)
def list_(p_id, do_id):
    """
    List all devices mapped to the DeviceModel through the given DeviceObject.

    Response:

        {
            'state': 'ok',
            'do_id': 42,
            'device_list': [
                {
                    'd_id': 24,
                    'd_name': 'FooDevice',
                    'dm_id': 5,
                    'mac_addr': '...',
                    'register_time': '...',
                    'status': 'online',
                    'u_id': 123,
                },
                ...
            ],
        }
    """
    session = g.session

    if not do_id:
        return json_error('unknown do_id'), 404

    # get DeviceModel by DeviceObject
    do_record = (session.query(db.DeviceObject)
                        .filter(db.DeviceObject.do_id == do_id)
                        .first())
    dm_id = do_record.dm_id

    query = (session.query(db.Device)
                    .filter(db.Device.dm_id == dm_id)
                    .order_by(db.Device.d_id)
                    .all())

    return json_data(data=[record_parser(device) for device in query],
                     do_id=do_id)


@api.route('/bind/<int:d_id>/', methods=['POST'], strict_slashes=False)
def bind(p_id, do_id, d_id):
    """
    Bind the Device to the DeviceObject.

    Response:

        {
            'state': 'ok',
            'd_name': 'FooDevice',
        }
    """
    session = g.session

    # check Device
    device_record = (session.query(db.Device)
                            .filter(db.Device.d_id == d_id)
                            .first())

    if not device_record:
        return json_error('Device id {} not found'.format(d_id)), 404

    # set Control Channel
    ControlChannel.SET_DF_STATUS(db, do_id, d_id)

    # get DeviceObject record
    do_record = (session.query(db.DeviceObject)
                        .filter(db.DeviceObject.do_id == do_id)
                        .first())

    do_record.d_id = d_id
    session.commit()

    reopen_project(p_id)

    return json_data(d_name=device_record.d_name)


@api.route('/unbind/', methods=['POST'], strict_slashes=False)
def unbind(p_id, do_id):
    """
    Unbind the Device to the DeviceObject.

    Response:

        {
            'state': 'ok',
            'do_id': 42,
        }
    """
    session = g.session

    # set Control Channel
    ControlChannel.SUSPEND_device(db, do_id)

    # check is binding
    device_record = (session.query(db.Device)
                            .select_from(db.DeviceObject)
                            .outerjoin(db.Device,
                                       db.Device.d_id == db.DeviceObject.d_id)
                            .filter(db.DeviceObject.do_id == do_id)
                            .first())

    if device_record:
        # get DeviceObject record
        do_record = (session.query(db.DeviceObject)
                            .filter(db.DeviceObject.do_id == do_id)
                            .first())

        # unbind
        do_record.d_id = None
        session.commit()

        # restart project
        reopen_project(p_id)

    return json_data(do_id=do_id)
