#!/usr/bin/env python3
import json
import os
import threading
import time

from copy import deepcopy
from datetime import datetime
from datetime import timedelta
from functools import update_wrapper
from urllib.parse import quote
from uuid import uuid4

from flask import current_app
from flask import jsonify
from flask import make_response
from flask import redirect
from flask import request
from flask import url_for
from flask import Flask
from flask import send_from_directory
from flask import render_template
from flask import abort
from os.path import exists, join, isdir
from flask_httpauth import HTTPBasicAuth

import ec_config
ec_config.ESM_CSM_PASS = str(uuid4())
f = open('passwd', 'w+')
f.write(ec_config.ESM_CSM_PASS)
f.close()

app = Flask(__name__)

import db
import PanelGenerator
import MsgManager
import deviceMgr

db.connect(ec_config.DB_NAME)

if ec_config.ESM_UMOUNT_ALL_ON_START: 
    deviceMgr.flush_device_table(db)
else:    
    boundDevices = deviceMgr.query_binding_devices(db)
    deviceMgr.fluash_unbound_devices_in_device_table(db, boundDevices)

auth = HTTPBasicAuth()
@auth.get_password
def get_pw(username):
    if username in ec_config.users:
        return ec_config.users.get(username)
    return None

auth_da = HTTPBasicAuth()
@auth_da.get_password
def get_pw(username):
    if username in ec_config.daUsers:
        return ec_config.daUsers.get(username)
    return None

def restore_binding_devices(boundDevices):
    time.sleep(2)
    deviceMgr.restore_device(db, boundDevices)

restore_devices_thx = None
if (not ec_config.ESM_UMOUNT_ALL_ON_START) and (not restore_devices_thx): 
    restore_devices_thx = threading.Thread(target = restore_binding_devices, args=(boundDevices,))
    restore_devices_thx.daemon = True
    restore_devices_thx.start()

################################################################################
#####                                 utils                                #####
################################################################################

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    '''Ref: http://flask.pocoo.org/snippets/56/ '''
    # Python 3 compatibility
    try:
        basestring
    except NameError:
        basestring = str

    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = '*' #origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


def is_number(value):
    return isinstance(value, (int, float, complex))


def update_min_max(target_list, data):
    '''update target_list with data **inline**.'''

    # extend target_list if len(target_list) < len(data)
    while len(target_list) < len(data): target_list.append(None)

    # check every dimension of data.
    for idx in range(len(data)):

        # target_list only available if it is number.
        if is_number(data[idx]):

            # use data this time to init.
            if target_list[idx] is None:
                target_list[idx] = [data[idx], data[idx]]

            target_list[idx][0] = min(target_list[idx][0], data[idx])
            target_list[idx][1] = max(target_list[idx][1], data[idx])


def stage_cmp(x):
    mapping = {'input': 1, 'type': 2, 'function': 3, 'normalization': 4, 'scaling': 5}
    return mapping[x]


################################################################################
#####                      device relative routes                          #####
################################################################################
devices = {}
'''
devices[mac_address]['password'] = (str)

devices[mac_addr][df_name] = [<sample>(latest), <sample>(last time)]
<sample> = [<timestamp>, <data>]

devices[mac_addr]['profile'] = <profile>
<profile> = {
    d_name: (str),
    dm_name: (str),
    u_name: (str, None),
    df_list: [df_name1(str), df_name2(str), ...]

    min_max: {
        df_name1: [[min, max], ...],
        df_name2: [[min, max], ...],
        ...
    }
}
'''
device_names = []
'''
device_names = [ d_name, ... ]
'''

'''
    This route is for showing web da
    (2016.04.10, pi314)
    (2016.08.01, ksoy)
'''
@app.route('/')
def show_web_da_list():
    js_da_list = sorted(
        f
        for f in os.listdir(ec_config.WEB_DA_DIR_PATH)
        if isdir(join(ec_config.WEB_DA_DIR_PATH, f))
            and f not in ('vp')
            and 'index.html' in os.listdir(join(ec_config.WEB_DA_DIR_PATH, f))
    )
    vp_da_list = sorted(
        f.replace('.py', '')
        for f in os.listdir(join(os.path.dirname(__file__), '../da/vp/py'))
        if f.endswith('.py')
    )

    return render_template('web_da_index.html', vp_da_list=vp_da_list, js_da_list=js_da_list)

'''
    This route is for web da
    (2016.04.10, pi314)
'''
#@app.route('/da/<path:path>')
def web_da(path):
    fullpath = join(ec_config.WEB_DA_DIR_PATH, path)
    no_cache_headers = {
        'Cache-Control': ('no-store, no-cache, must-revalidate, '
                          'post-check=0, pre-check=0, max-age=0'),
        'Pragma': 'no-cache',
        'Expires': '-1',
    }

    if exists(fullpath) and isdir(fullpath):
        if not fullpath.endswith('/'):
            
            response = make_response(redirect(join('/da', path) + '/'))   #for Werkzeug  0.15.2 and later
            for key, val in no_cache_headers.items():
                response.headers[key] = val
            return response

        if exists(join(fullpath, 'index.html')):
            
            if path == 'Remote_control/': PanelGenerator.PanelGen()
            response = send_from_directory(fullpath, 'index.html')
            for key, val in no_cache_headers.items():
                response.headers[key] = val
            return response
    
    return send_from_directory(ec_config.WEB_DA_DIR_PATH, path)


@app.route('/favicon.ico')
def icon():
    return send_from_directory(ec_config.EASYCONNECT_ROOT_PATH+'/lib/static/', 'favicon.ico')


def get_d_id_from_MAC_addr(db, mac_addr):
    session = db.get_session()
    d_id = (session.query(db.Device.d_id)
                .select_from(db.Device)
                .filter(db.Device.mac_addr == mac_addr)
                .first()
               )
    session.close()
    if d_id: 
        d_id = d_id[0]
        return d_id

def get_do_id_from_MAC_addr(db, mac_addr):
    session = db.get_session()
    do_id = (session.query(db.DeviceObject.do_id)
                .select_from(db.DeviceObject)
                .join(db.Device)
                .filter(db.Device.d_id == db.DeviceObject.d_id)
                .filter(db.Device.mac_addr == mac_addr)
                .first()
               )
    session.close()
    if do_id: 
        do_id = do_id[0] 
        return do_id

def get_dfo_ids_from_df_name(db, mac_addr, df_name):
    session = db.get_session()
    try:
        dfo_ids  = (session.query(db.DFObject.dfo_id, db.DeviceObject.p_id)
                .select_from(db.DFObject)
                .join(db.DeviceObject)
                .join(db.Device)
                .join(db.DeviceModel)
                .join(db.DM_DF)
                .join(db.DeviceFeature)
                .filter(db.DFObject.do_id == db.DeviceObject.do_id)
                .filter(db.Device.mac_addr == mac_addr)
                .filter(db.Device.d_id == db.DeviceObject.d_id)
                .filter(db.DeviceObject.dm_id == db.DeviceModel.dm_id)
                .filter(db.DeviceModel.dm_id == db.DM_DF.dm_id)
                .filter(db.DM_DF.df_id == db.DeviceFeature.df_id)
                .filter(db.DeviceFeature.df_id == db.DFObject.df_id)
                .filter(db.DeviceFeature.df_name == df_name)
                .all()
               )
        print(dfo_ids)
    except Exception as e:
        print (e)
        session.close()
        return None
    else:
        session.close()
        return dfo_ids

def get_alias_from_df_name(db, mac_addr, df_name):  #From a specific device object, not from the default DeviceFeature table.
    session = db.get_session()
    try:
        alias_name = (session.query(db.DFObject.alias_name)
                .select_from(db.DFObject)
                .join(db.DeviceObject)
                .join(db.Device)
                .join(db.DeviceModel)
                .join(db.DM_DF)
                .join(db.DeviceFeature)
                .filter(db.DFObject.do_id == db.DeviceObject.do_id)
                .filter(db.Device.mac_addr == mac_addr)
                .filter(db.Device.d_id == db.DeviceObject.d_id)
                .filter(db.DeviceObject.dm_id == db.DeviceModel.dm_id)
                .filter(db.DeviceModel.dm_id == db.DM_DF.dm_id)
                .filter(db.DM_DF.df_id == db.DeviceFeature.df_id)
                .filter(db.DeviceFeature.df_id == db.DFObject.df_id)
                .filter(db.DeviceFeature.df_name == df_name)
                .all()
               )
        alias_name = [a[0] for a in alias_name]
    except Exception:
        session.close()
        return None
    else:
        session.close()
        return alias_name


'''
    These routes are used for static Remote Control generator
    (2019.10.30, Jyneda)
'''
import csmapi

@app.route('/RemoteControl/<device_id>', methods=['GET'])
def remote_control_generator(device_id):
    
    sync = request.args.get('sync')
    if sync != 'True': sync = False

    def register_remote_control(device_id):
        profile = {
            'd_name': device_id,
            'dm_name': 'Remote_control',
            'u_name': 'yb',
            'df_list': [],
        }
        for i in range(1,26):
            profile['df_list'].append("Keypad%d" % i)
            profile['df_list'].append("Button%d" % i)
            profile['df_list'].append("Switch%d" % i)
            profile['df_list'].append("Knob%d" % i)
            profile['df_list'].append("Color-I%d" % i)
            profile['df_list'].append("Toggle%d" % i)
            profile['df_list'].append("Slider%d" % i)
        try:        
            result = csmapi.register(device_id, profile)
            if result: print('Remote control generator: Remote Control successfully registered.')
            return result
        except Exception as e:
            print('Remote control generator: ', e)

    profile = None
    try:    
        profile = csmapi.pull(device_id, 'profile')
    except Exception as e:
        print('Remote control generator: ', e)
        if str(e).find('mac_addr not found:') != -1:
            print('Remote control generator: Register Remote Control...')
            result = register_remote_control(device_id)
            return 'Remote control "'+device_id+'" successfully registered. <br> Please bind it in the IoTtalk GUI.', 200
        else:
            print('Remote control generator: I dont know how to handel this error. Sorry...pass.')
            abort(404)

    if profile:
        try:
            Ctl_O = csmapi.pull(device_id, '__Ctl_O__')
        except Exception as e:
            print('Remote control generator: ', e)
            abort(404)

        if Ctl_O != []:
            selected_df_flags = Ctl_O[0][1][1]['cmd_params'][0]
            
            df_list = profile['df_list']
            df_dict = {'Butt': 0, 'Colo': 0, 'Keyp': 0, 'Knob': 0, 'Swit': 0, 'Togg':0, 'Slid':0}

            for index, element in list(enumerate(selected_df_flags)):
                if element == '1': df_dict[df_list[index][:4]] += 1

            return make_response(render_template('remotecontrol.html', device_id=device_id, df_dict=df_dict, sync=sync))
            
        else:
            print('Remote control generator: Ctl_O is empty.')
            return 'Please bind this remote control "'+device_id+'" in the IoTtalk GUI.', 200

    else:  
        print('Remote control generator: Profile is empty.')
        abort(404)


'''
    These routes are used for static SwitchSet
    (2018.7.9, Jyneda)
'''
#@app.route('/SwitchSetV2/<mac_addr>/<count>/', methods=['GET', 'POST'])
#def SwitchSetiV2(mac_addr, count):
#    username = request.args.get('username')
#    if not username: return 'ID information is required.', 404 
#    #print(username)
#    return make_response(render_template('SwitchSet_id.html', mac_addr=mac_addr, count=int(count), username=username))

#@app.route('/SWV/<mac_addr>/<count>/', methods=['GET', 'POST'])
#def SWV(mac_addr, count):
#    username = request.args.get('username')
#    field = request.args.get('field')
#    if not username or not field: return 'Lack necessary Information.', 404
#    return make_response(render_template('SW_video.html', mac_addr=mac_addr, count=int(count), username=username, field=field))


#@app.route('/SwitchSet/<mac_addr>/<count>/', methods=['GET', 'POST'])
#def SwitchSet(mac_addr, count):
#    return make_response(render_template('SwitchSet.html', mac_addr=mac_addr, count=int(count)))


'''
    These routes are used for Message
    (2016.10.30, Jyneda)
'''
@app.route('/msg/')
def msg():
    return make_response(render_template('msg_index.html', count=int(MsgManager.MsgNameCount())))

@app.route('/save_msg_info', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['accept', 'content-type'])
def save_msg_info():
    if not request.json:
        return 'argument is not in JSON format', 400
    MsgManager.SaveMsgContact(request.json)
    return 'ok', 200

@app.route('/load_msg_info', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['accept', 'content-type'])
def load_msg_info():
    return jsonify(MsgManager.LoadMsgContact())

@app.route('/get_alias/<mac_addr>/<df_name>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*', headers=['accept', 'content-type'])
def get_alias(mac_addr, df_name):
    alias =  get_alias_from_df_name(db, mac_addr, df_name)
    if alias == None: return 'Error: Device may be not existed or not mounted.', 400
    else: return  jsonify(alias_name=alias)


@app.route('/set_alias/<mac_addr>/<df_name>/alias', methods=['GET', 'POST'])
@crossdomain(origin='*', headers=['accept', 'content-type'])
def set_alias(mac_addr, df_name):
    alias = request.args.get('name')
    dfo_ids = get_dfo_ids_from_df_name (db, mac_addr, df_name)
    if dfo_ids == []:  return 'Error: Device may be not existed or not mounted.', 400
    else:
        session = db.get_session()
        for dfo_id, p_id in dfo_ids:
            (session.query(db.DFObject)
                    .filter(db.DFObject.dfo_id == dfo_id)
                    .update({'alias_name' : alias}))
            (session.query(db.Project)
                    .filter(db.Project.p_id == p_id)
                    .update({'exception' : '[anno] reload'}))
            session.commit()
        session.close()
        return  jsonify(alias_name=alias)

'''
    Routes for Message end.
'''


@app.route('/<mac_addr>', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*', headers=['accept', 'content-type'])
def create(mac_addr):
    if not request.json:
        return 'argument is not in JSON format', 400
    if 'profile' not in request.json:
        return 'profile dictionary is not given', 400

    profile = request.json['profile']

    if 'dm_name' not in profile:    return 'dm_name not in profile', 400
#    if 'u_name' not in profile:     return 'u_name not in profile', 400
    if 'df_list' not in profile:    return 'df_list not in profile', 400

    if 'd_name' in profile and not isinstance(profile['d_name'], str):      return 'd_name format error', 400
    if not isinstance(profile['dm_name'], str):     return 'dm_name format error', 400
#    if not isinstance(profile['u_name'], (str, type(None))): return 'u_name format error', 400
    if not isinstance(profile['df_list'], list):    return 'df_list format error', 400
    for df_name in profile['df_list']:
        if not isinstance(df_name, str):    return 'df_list format error', 400

    # check and generate d_name
    if 'd_name' not in profile:
        for i in range(100):
            d_name = '{0:02d}.{1}'.format(i, profile['dm_name'])
            if d_name not in device_names:
                profile['d_name'] = d_name
                device_names.append(d_name)
                break

        if 'd_name' not in profile:
            return 'd_name pool is full', 400
    else:
        # WARRING! it may duplicate
        device_names.append(profile['d_name'])

    # cerate device record first.
    # If mac_addr is already exists in db, switch 'status' to online.
    # And change d_name.
    session = db.get_session()
    dev = session.query(db.Device).filter(db.Device.mac_addr==mac_addr).first()
    if dev:
        dev.status = 'online'
        dev.d_name = profile['d_name']

    # Create new record in Device.
    else:
#        if profile['u_name']:
#            user = session.query(db.User).filter(db.User.u_name==profile['u_name']).first()
#            if not user:
#                return 'u_name not found: ' + profile['u_name'], 400
#        else:
#            user = None

        dm = session.query(db.DeviceModel).filter(db.DeviceModel.dm_name==profile['dm_name']).first()
        if not dm:
            session.close()
            return 'dm_name not found: ' + profile['dm_name'], 400

        session.add(db.Device(
            d_name = profile['d_name'],
            dm_id = dm.dm_id,
            mac_addr = mac_addr,
            status = 'online',
            monitor = 'NOT_USE',
            #u_id = user.u_id if user else None,
        ))
    session.commit()
    session.close()


    # prepare device dictionary
    devices[mac_addr] = {}
    devices[mac_addr]['password'] = str(uuid4())
    devices[mac_addr]['profile'] = profile
    devices[mac_addr]['profile']['min_max'] = {}

    for df_name in profile['df_list']:
        devices[mac_addr][df_name] = []

        # prepare min_max in profile
        devices[mac_addr]['profile']['min_max'][df_name] = []

    devices[mac_addr]['__Ctl_I__']=[]
    devices[mac_addr]['__Ctl_O__']=[]

    # return d_name
    return jsonify({'d_name': profile['d_name'], 'password': devices[mac_addr]['password']})


@app.route('/<mac_addr>', methods=['DELETE', 'OPTIONS'])
@crossdomain(origin='*')
def delete(mac_addr):
    if mac_addr not in devices:
        return 'mac_addr not found: ' + mac_addr, 400

    devices.pop(mac_addr)

    session = db.get_session()

    # set the device status to offline.
    dev = session.query(db.Device).filter(db.Device.mac_addr==mac_addr).first()
    dev.status = 'offline'

    # set some exception to the project (for GUI to refresh)
    prjs = (
        session.query(db.Project)
        .join(db.DeviceObject)
        .filter(db.DeviceObject.d_id == dev.d_id)
        .group_by(db.Project.p_id)
    )

    for prj in prjs:
        if mac_addr[:6] != 'SimDev':
            prj.exception = 'The device is offline: {}({})'.format(
                dev.d_name, mac_addr
            )

    # umount the device
    session.query(db.DeviceObject)\
        .filter(db.DeviceObject.d_id == dev.d_id)\
        .update({'d_id': None})

    session.commit()

    # remove d_name
    if dev.d_name in device_names:
        device_names.remove(dev.d_name)

    # delete device
    session.query(db.Device).filter(db.Device.d_id == dev.d_id).delete()
    session.commit()

    session.close()

    return ''


@app.route('/<mac_addr>/<df_name>', methods=['PUT', 'OPTIONS'])
@crossdomain(origin='*', headers=['accept', 'content-type', 'password-key'])
def push(mac_addr, df_name):
    if df_name == 'profile': return 'profile cannot be modified', 400

    if not request.json:
        return 'argument is not in JSON format', 400
    if 'data' not in request.json:
        return 'data is not given', 400

    data = request.json['data']
    sample = [str(datetime.today()), data]

    if not isinstance(data, list):
        return 'data should be an array', 400

    if mac_addr not in devices:
        return 'mac_addr not found: ' + mac_addr, 400
    if df_name not in devices[mac_addr]:
        return 'df_name not found: ' + df_name, 400
    if ec_config.DEVICE_AUTH is True:
        if not request.headers.get('password-key'):
            return 'password-key should be in header', 401
        if request.headers.get('password-key') != devices[mac_addr]['password'] and request.headers.get('password-key') != ec_config.ESM_CSM_PASS:
            return 'password-key error', 401

    devices[mac_addr][df_name].insert(0, sample)
    if len(devices[mac_addr][df_name]) > ec_config.CSM_PULL_SAMPLE_LEN:
        devices[mac_addr][df_name].pop()

    # update min_max in profile

    if ( (df_name != '__Ctl_O__') and (df_name != '__Ctl_I__') ):
        update_min_max(devices[mac_addr]['profile']['min_max'][df_name], data)

    #app.logger.info('{}/{}: {}'.format(mac_addr, df_name, sample))
    return ''

@app.route('/<mac_addr>/<df_name>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def pull(mac_addr, df_name):
    if mac_addr not in devices:
        return 'mac_addr not found: ' + mac_addr, 400
    df_dir = devices[mac_addr]
    if df_name not in df_dir:
        print('Check df:', df_name)
        print('df_list:', str(df_dir.items()))

        #errorlog = open('error_df_name_not_found', mode='a')
        #msg = str(datetime.now())+ ': ' + df_name + ' --- ' +  str(df_dir.items()) + '\n\n\n' 
        #errorlog.write(msg) 
        #errorlog.close()

        return 'df_name not found: ' + df_name, 400

    if ec_config.DEVICE_AUTH is True:
        if not request.headers.get('password-key'):
            return 'password-key should be in header', 401
        if request.headers.get('password-key') != devices[mac_addr]['password'] and request.headers.get('password-key') != ec_config.ESM_CSM_PASS:
            return 'password-key error', 401

    if df_name == 'profile':
        return jsonify(samples=devices[mac_addr][df_name])
    else:
        return jsonify(samples=devices[mac_addr][df_name][0:ec_config.CSM_PULL_SAMPLE_LEN])


@app.route('/tree')
@crossdomain(origin='*')
def tree():
    ret = {k:list(v.keys()) for k,v in devices.items()}
    return jsonify(**ret)


################################################################################
#####                       DF-module relative routes                      #####
################################################################################

# DF-module use (na_id, dfo_id) to identicate a half-line.
dfm_logs = {}
'''
dfm_logs[(na_id, dfo_id)] = {
    # for IDF
    input: <logs>
    type: <logs>
    function: <logs>
    normalization: <logs>

    # for Join
    function: <logs>

    # for ODF
    function: <logs>
    scaling: <logs>
}

<logs> = {
    samples: [<sample>(newest), ..., <sample>(oldest)],
    min_max: <min_max>,
}

<sample> = [<timestamp>, <data>]
<min_max> = [[min, max], ...]

e.g., <Acceleration input logs> = {
    samples: [
        ['2015-09-08 17:56:44.957997', [0, 0, 10]],
        ['2015-09-08 17:56:45.829405', [0, -1, 9]],
        ...
    ],
    min_max: [[0, 0], [-1, 0], [9, 10]],   # len(min_max) == dimension
}

e.g., <Acceleration function logs> = {
    samples: [
        ['2015-09-08 17:56:44.957997', [10]],
        ['2015-09-08 17:56:45.829405', [9.05]],
        ...
    ],
    min_max: [[9.05, 10]],      # len(min_max) = dimension
}


================ ========================================= ========= =========
API functions overview
------------------------------------------------------------------------------
API name         HTTP request                              argument  return
================ ========================================= ========= =========
dfm_push         PUT /dfm/<na_id>/<dfo_id>/<stage>         <data>    -
dfm_pull         GET /dfm/<na_id>/<dfo_id>/<stage>         -         <samples>
dfm_push_min_max PUT /dfm/<na_id>/<dfo_id>/<stage>/min_max <min_max> -
dfm_pull_min_max GET /dfm/<na_id>/<dfo_id>/<stage>/min_max -         <min_max>
dfm_reset        DELETE /dfm/<na_id>/<dfo_id>              -         -
dfm_reset_all    DELETE /dfm/                              -         -
================ ========================================= ========= =========
'''

EMPTY_LOGS_DICT = {'samples': [], 'min_max': []}


@app.route('/dfm/<na_id>/<dfo_id>/<stage>', methods=['PUT', 'OPTIONS'])
@crossdomain(origin='*', headers=['content-type'])
def dfm_push(na_id, dfo_id, stage):
    if not request.json:
        return 'argument is not in JSON format', 400
    if 'data' not in request.json:
        return 'data is not given', 400

    data = request.json['data']
    sample = [str(datetime.today()), data]

    if not isinstance(data, list):
        return 'data should be an array', 400

    # if no (na_id, dfo_id) exists, create one.
    if (na_id, dfo_id) not in dfm_logs:
        dfm_logs[(na_id, dfo_id)] = {}

    # if stage not exists, create one.
    if stage not in dfm_logs[(na_id, dfo_id)]:
        dfm_logs[(na_id, dfo_id)][stage] = deepcopy(EMPTY_LOGS_DICT)

    logs_dict = dfm_logs[(na_id, dfo_id)][stage]

    # insert sample into samples
    logs_dict['samples'].insert(0, sample)
    if len(logs_dict['samples']) > ec_config.CSM_SAMPLE_THRESHOLD:
        logs_dict['samples'].pop()

    # update min_max.
    update_min_max(logs_dict['min_max'], data)

    return ''


@app.route('/dfm/<na_id>/<dfo_id>/<stage>', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def dfm_pull(na_id, dfo_id, stage):
    # return empty data if (na_id, dfo_id) not exists.
    if (na_id, dfo_id) not in dfm_logs:
        return jsonify(samples=EMPTY_LOGS_DICT['samples'])

    if stage not in dfm_logs[(na_id, dfo_id)]:
        return jsonify(samples=EMPTY_LOGS_DICT['samples'])

    return jsonify(samples=dfm_logs[(na_id, dfo_id)][stage]['samples'])


@app.route('/dfm/<na_id>/<dfo_id>/<stage>/min_max', methods=['PUT', 'OPTIONS'])
@crossdomain(origin='*', headers=['content-type'])
def dfm_push_min_max(na_id, dfo_id, stage):
    if not request.json:
        return 'argument is not in JSON format', 400
    if 'min_max' not in request.json:
        return 'min_max is not given', 400

    min_max = request.json['min_max']

    if not isinstance(min_max, list):
        return 'min_max should be an array', 400

    for i in range(len(min_max)):
        if not isinstance(min_max[i], list):
            return 'min_max[{}] should be an array'.format(i), 400
        if len(min_max[i]) != 2:
            return 'the length of min_max[{}] should be 2'.format(i), 400
        if not is_number(min_max[i][0]):
            return 'min_max[{}][0] (min) shoud be a number'.format(i), 400
        if not is_number(min_max[i][1]):
            return 'min_max[{}][1] (max) shoud be a number'.format(i), 400
        if min_max[i][0] > min_max[i][1]:
            return 'min should not larger than max at min_max[{}]'.format(i), 400

    # if no (na_id, dfo_id) exists, create one.
    if (na_id, dfo_id) not in dfm_logs:
        dfm_logs[(na_id, dfo_id)] = {}

    # if stage not exists, create one.
    if stage not in dfm_logs[(na_id, dfo_id)]:
        dfm_logs[(na_id, dfo_id)][stage] = deepcopy(EMPTY_LOGS_DICT)

    # force to update min_max.
    dfm_logs[(na_id, dfo_id)][stage]['min_max'] = min_max

    return ''


@app.route('/dfm/<na_id>/<dfo_id>/<stage>/min_max', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def dfm_pull_min_max(na_id, dfo_id, stage):
    # return empty data if (na_id, dfo_id) not exists.
    if (na_id, dfo_id) not in dfm_logs:
        return jsonify(min_max=EMPTY_LOGS_DICT['min_max'])

    if stage not in dfm_logs[(na_id, dfo_id)]:
        return jsonify(min_max=EMPTY_LOGS_DICT['min_max'])

    return jsonify(min_max=dfm_logs[(na_id, dfo_id)][stage]['min_max'])


@app.route('/dfm/<na_id>/<dfo_id>', methods=['DELETE', 'OPTIONS'])
@crossdomain(origin='*')
def dfm_reset(na_id, dfo_id):
    # just delete it.
    dfm_logs.pop((na_id, dfo_id), None)
    return ''


@app.route('/dfm/', methods=['DELETE', 'OPTIONS'])
@crossdomain(origin='*')
def dfm_reset_all():
    global dfm_logs
    dfm_logs = {}
    return ''


################################################################################
#####                      device relative routes                          #####
################################################################################

#auth = HTTPBasicAuth()
#@auth.get_password
#def get_pw(username):
#    if username in ec_config.users:
#        return ec_config.users.get(username)
#    return None


#@app.route('/list_all')
def list_all():

    title_css = 'font-weight: bold; font-size: 1.3em;'
    head_ret = '''
    <meta charset="utf-8">
    <link rel="stylesheet" href="/static/font.css">
    <script src="https://code.jquery.com/jquery-3.3.1.min.js" crossorigin="anonymous"></script>
    <script type="text/javascript">
    function send_delete(url) {
        $.ajax({
            url: url,
            type: 'DELETE',
            success: function(result) {
                location.reload();
            }
        });
    }

    function open_project(p_name) {
        var url = 'http://' + window.location.hostname + ':7788/connection#' + p_name;
        window.open(url, '_blank');

    }
    </script>
    '''

    ##### device part #####
    device_ret = [(
        '<span style="{}">========== device part ==========</span>'
    ).format(title_css)]

    session = db.get_session()
    for mac_addr in sorted(devices):

        p_names = (session.query(db.Project.p_name)
                .select_from(db.Project)
                .join(db.DeviceObject)
                .join(db.Device)
                .filter(db.Device.mac_addr == mac_addr)
                .all())

        # title and delete short-cut
        device_ret += [(
            '{0} <a href="#" onclick="send_delete(\'/{0}\')">Delete</a>'
        ).format(mac_addr)]

        # profile
        device_ret += ['    <a href="/{}/profile">profile</a>:'.format(mac_addr)]
        for key in sorted(devices[mac_addr]['profile']):
            if key == 'min_max': continue
            device_ret += ['        {}: {}'.format(
                key,
                devices[mac_addr]['profile'][key],
            )]

        #involed project
        device_ret += ['        project: ']
        for p_name in p_names:
            device_ret += ['            <a href="#" onclick="open_project(\'{}\')">{}</a>'.format(p_name.p_name, p_name.p_name)]

        # min_max
        device_ret += ['        min_max:']
        for df_name in sorted(devices[mac_addr]['profile']['min_max']):
            device_ret += ['            {}: {}'.format(
                df_name,
                devices[mac_addr]['profile']['min_max'][df_name],
            )]

        # featues
        for df_name in sorted(devices[mac_addr]):
            if df_name == 'profile': continue
            device_ret += ['    <a href="/{0}/{1}">{1}</a>: {2}'.format(
                mac_addr,
                df_name,
                devices[mac_addr][df_name],
            )]
        device_ret += ['']


    ##### dfm_log part #####
    dfm_ret = [(
        '<span style="{}">========== DF-module part ==========</span>'
    ).format(title_css)]

    dfm_ret += ['<a href="#" onclick="send_delete(\'/dfm/\')">Reset All</a>']
    dfm_ret += ['']

    for na_id, dfo_id in sorted(dfm_logs):

        # title and delete short-cut
        dfm_ret += [ ('(na_id={0}, dfo_id={1}) '
                      '<a href="#" onclick="send_delete(\'/dfm/{0}/{1}\')">'
                      'Reset (delete)</a>'
                      ).format(na_id, dfo_id) ]

        # dfm logs
        for stage in sorted(dfm_logs[(na_id, dfo_id)], key=stage_cmp):
            dfm_ret += [(
                '    <a href="/dfm/{0}/{1}/{2}">{2}</a>: '
                '<a href="/dfm/{0}/{1}/{2}/min_max">min_max</a> = {3}'
            ).format(
                na_id,
                dfo_id,
                stage,
                dfm_logs[(na_id, dfo_id)][stage]['min_max'],
            )]

        dfm_ret += ['']


    ret = '''<html>
        <head>{}</head>
        <body><pre>{}<hr>{}<hr></pre></body>
    </html>'''.format(
        head_ret,
        '\n'.join(device_ret),
        '\n'.join(dfm_ret),
    )
    return ret, 200, {'Content-Type': 'text/html'}


if ec_config.manager_auth_required:
    list_all = auth.login_required(list_all)
    list_all = app.route('/list_all', methods=['GET'])(list_all)
else:
    list_all = app.route('/list_all', methods=['GET'])(list_all)

if ec_config.cyber_auth_required:
    web_da  = auth_da.login_required(web_da)
    web_da  = app.route('/da/<path:path>', methods=['GET'])(web_da)
    #SwitchSet = auth_da.login_required(SwitchSet)
    #SwitchSet = app.route('/SwitchSet/<mac_addr>/<count>/', methods=['GET', 'POST'])(SwitchSet)
else:
    web_da  = app.route('/da/<path:path>', methods=['GET'])(web_da)
    #SwitchSet = app.route('/SwitchSet/<mac_addr>/<count>/', methods=['GET', 'POST'])(SwitchSet)


if __name__ == '__main__':
    app.config['SESSION_REFRESH_EACH_REQUEST'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.run(
        host = ec_config.CSM_HOST,
        port = ec_config.CSM_PORT,
        threaded = True,
        debug = ec_config.CSM_DEBUG,
    )

