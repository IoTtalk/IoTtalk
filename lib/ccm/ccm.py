#!/usr/bin/env python3
import datetime
import json
import os
import os.path
import subprocess
import time
import random
import uuid
import hashlib

from flask import Flask, g, redirect, render_template, request, send_from_directory, url_for, make_response
app = Flask(__name__) # Note that app is ccm_app in the thesis

from sqlalchemy import and_, asc, desc, not_, or_, func, Integer
from sqlalchemy.sql.expression import cast
from cloudant.client import Cloudant

from operator import itemgetter
import ec_config
import db

db.connect(ec_config.DB_NAME)

import csmapi
import ControlChannel

import SpecialModel

from os import listdir
from os.path import isfile, join

from flask_httpauth import HTTPBasicAuth

'''In order to fix cross domain problem'''
from datetime import timedelta
from flask import current_app
from functools import update_wrapper

selected_models_in_prj_need_to_update = {}

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
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

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/favicon.ico')
def icon():
    return send_from_directory(ec_config.EASYCONNECT_ROOT_PATH+'/lib/static/', 'favicon.ico')


#from ini_parser import ini_parser

# logger shortcut
debug = app.logger.debug
warn = app.logger.warning
error = app.logger.error


#################### settings ####################
UPLOAD_DIR = '/static/images/upload_icon/'
ALLOWED_EXTENSIONS = set(['png'])
ALL_CATEGORY = ['Sight', 'Hearing', 'Feeling', 'Motion', 'Other', ]
#################### utils ####################

# SMS Setting #
SMS_SERVER_IP = ''
SMS_SERVER_LOGIN = ''
SMS_SERVER_PWD = ''

def send_SMS(msg, tel):
    current_path = os.path.dirname(__file__)

    subprocess.Popen([
        os.path.join(current_path, os.path.join('SMS')),
        SMS_SERVER_IP,
        SMS_SERVER_LOGIN,
        SMS_SERVER_PWD,
        tel,
        msg
    ])
############### utility functions ####################
def get_prj_status(p_id):
    s = db.get_session()
    project_status = None
    for status, in (
        s.query(db.Project.status)
        .filter(db.Project.p_id == p_id)
    ):
        project_status = status
    s.close()
    return project_status


def get_simulation_status(p_id):
    s = db.get_session()
    sim_status = None
    for sim, in (
        s.query(db.Project.sim)
        .filter(db.Project.p_id == p_id)
    ):
        sim_status = sim
    s.close()    
    return sim_status


def get_all_idf_module_info(na_id):
    session = g.session

    all_idfo_id = []
    range_info = []
    return_info = {
        'idf_name': [],
        'idfo_id': [],
        'idf_module_title': [],
        'norm_enable': [],
        'idf_fn_id': [],
        'idf_info': [],
        'alias_name': []
    }

    # query all idf _id connected with na_id
    idfo_id_list = (
        session.query(db.DF_Module.dfo_id,)
        .select_from(db.DF_Module)
        .join(db.DFObject)
        .join(db.DeviceFeature)
        .join(db.DeviceObject)
        .filter(db.DeviceFeature.df_type == 'input', db.DF_Module.na_id == na_id)
        .group_by(db.DF_Module.dfo_id)
        .order_by(db.DeviceObject.do_idx, db.DeviceFeature.df_name)
        .all()
    )
    for data in idfo_id_list:
        all_idfo_id.append(data[0])
    return_info['idfo_id'] = all_idfo_id

    # get relevant mf_id from df_id & dm_id for all idfo_id
    for _id in all_idfo_id:
        (dm_id, df_id, d_id) = (
            session.query(db.DeviceObject.dm_id, db.DFObject.df_id, db.DeviceObject.d_id)
            .join(db.DFObject)
            .filter(db.DFObject.dfo_id == _id)
            .first()
        )
        mf_id = (
            session.query(db.DM_DF.mf_id)
            .filter(db.DM_DF.dm_id == dm_id, db.DM_DF.df_id == df_id)
            .first()
        )
        if mf_id: mf_id = mf_id[0]
        # get idf module info
        idf_module_info = get_df_module_info(na_id, _id, mf_id)
        return_info['idf_name'].append(idf_module_info[0])
        return_info['alias_name'].append(idf_module_info[1])
        return_info['idf_module_title'].append(get_df_module_title(dm_id, d_id))
        return_info['norm_enable'].append(idf_module_info[2]['normalization'])

        for i in range(2, len(idf_module_info)):
            range_info.append(
                idf_module_info[i]['idf_type']
            )
        return_info['idf_info'].append(range_info.copy())
        range_info = []
    
    return return_info

def get_df_module_info(na_id, dfo_id, mf_id):
    '''
    input value:
        na_id
        dfo_id
        mf_id
    output value:
        df_module_info = [
            df_name,
            alias_name,
            {
                'param_i': 1,
                'fn_id': 2,
                'normalization': 1/0,
            {
                'param_i': 1,
                'fn_id': 2,
                'normalization': 1/0,
            ...
        ]
    '''
    u_id = 1
    session = g.session

    df_module_info = []
    df_content = {
        'param_i': None,
        'idf_type': None,
        'fn_id': None,
        'normalization': None,
        'min': None,
        'max': None
    }

    dfo_info = (
        session.query(db.DeviceFeature.df_id, db.DeviceFeature.df_name, db.DFObject.alias_name)
        .join(db.DFObject)
        .filter(db.DFObject.dfo_id == dfo_id)
        .first()
    )
    df_module_info.append(dfo_info[1])
    df_module_info.append(dfo_info[2])

    #is_set(?)
    query_result = (
        session.query(db.DF_Module.param_i, db.DF_Module.normalization,
                      db.DF_Module.idf_type, 
                      db.DF_Module.min, db.DF_Module.max)
        .filter(db.DF_Module.dfo_id == dfo_id, db.DF_Module.na_id == na_id)
        .all()
    )

    #customize_range
    if len(query_result) == 0:
        query_result = (
            session.query(db.DF_Parameter.param_i, db.DF_Parameter.normalization,
                          db.DF_Parameter.idf_type,
                          db.DF_Parameter.min, db.DF_Parameter.max)
            .filter(db.DF_Parameter.mf_id == mf_id, db.DF_Parameter.u_id == u_id)
            .all()
        ) 

    #company_range
    if len(query_result) == 0:
       query_result = (
            session.query(db.DF_Parameter.param_i, db.DF_Parameter.normalization,
                          db.DF_Parameter.idf_type,
                          db.DF_Parameter.min, db.DF_Parameter.max)
            .filter(db.DF_Parameter.mf_id == mf_id, db.DF_Parameter.u_id == None)
            .all()
        )

    #service_range
    if len(query_result) == 0:
        query_result = (
            session.query(db.DF_Parameter.param_i, db.DF_Parameter.normalization,
                          db.DF_Parameter.idf_type,
                          db.DF_Parameter.min, db.DF_Parameter.max)
            .filter(db.DF_Parameter.mf_id == None, db.DF_Parameter.u_id == None, 
                    db.DF_Parameter.df_id == dfo_info[0])
            .all()
        ) 

    for row in query_result:
        df_content['param_i'] = row[0]
        df_content['normalization'] = row[1]
        df_content['idf_type'] = row[2]
        df_content['min'] = row[3]
        df_content['max'] = row[4]
        df_module_info.append(df_content.copy())

    
    return df_module_info

def get_df_module_title(dm_id, d_id):

    session = g.session

    if d_id == None:
        title = (
            session.query(db.DeviceModel.dm_name)
            .filter(db.DeviceModel.dm_id == dm_id)
            .first()
        )
        if title: title = title[0]
    else:
        title = (
            session.query(db.Device.d_name)
            .filter(db.Device.d_id == d_id)
            .first()
        )
        if title: title = title[0]

    
    return title

def get_sorted_idf_id_list(na_id):
    session = g.session

    sorted_id_list = (
        session.query(db.DF_Module.dfo_id)
        .join(db.DFObject, db.DeviceFeature)
        .filter(db.DeviceFeature.df_type == 'input', db.DF_Module.na_id == na_id)
        .group_by(db.DF_Module.dfo_id)
        .order_by(db.DF_Module.dfo_id)
        .all()
    )

    id_list = []
    for i in sorted_id_list:
        id_list.append(i[0])

    
    return id_list

def get_none_positive_list(all_func_list, positive_list):
    '''
    input value:
        all_func_list = [[fn_name, fn_id], ...]
        positive_list = [[fn_name, fn_id], ...]
    output value:
        rest_function_list = [[fn_name, fn_id], ...]
    '''
    diff = lambda l1, l2: [x for x in l1 if x not in l2]
    return diff(all_func_list, positive_list)

def remove_disabled(li):
    return remove_df_function(li, 'disabled')

def remove_df_functions(li, fn_name_list):
    for fn_name in fn_name_list:
        li = remove_df_function(li, fn_name)
    return li

# for sorting based on the completeness flag
def get_completeness(input_list):
    return input_list[2]


def refresh_join_module(na_id):
    remove_join_module(na_id)
    build_join_module(na_id)


def remove_join_module(na_id):
    session = g.session
    for dfo_id, in (
        session.query(db.MultipleJoin_Module.dfo_id)
        .filter(db.MultipleJoin_Module.na_id == na_id)
        .all()
    ):
        for entry in (
            session.query(db.DF_Module)
            .filter(db.DF_Module.dfo_id == dfo_id, db.DF_Module.na_id == na_id)
            .all()
        ):
            entry.normalization = 0
            session.commit()

    (
        session.query(db.MultipleJoin_Module)
        .filter(db.MultipleJoin_Module.na_id == na_id)
        .delete()
    )
    session.commit()
    

def build_join_module(na_id):
    session = g.session
    idf_count = len(
        session.query(db.DF_Module.dfo_id)
        .join(db.DFObject, db.DeviceFeature)
        .filter(db.DeviceFeature.df_type == 'input', db.DF_Module.na_id == na_id)
        .group_by(db.DF_Module.dfo_id)
        .all()
    )
    if idf_count > 1:
        idfo_id_list = [ dfo_id for (dfo_id, ) in(
            session.query(db.DF_Module.dfo_id)
            .join(db.DFObject, db.DeviceFeature)
            .filter(db.DeviceFeature.df_type == 'input', db.DF_Module.na_id == na_id)
            .group_by(db.DF_Module.dfo_id)
            .all()
        )]
        idfo_id_list.sort()
        ordered_idfo_id_list = [ dfo_id for (dfo_id, ) in(
            session.query(db.DFObject.dfo_id)
            .join((db.DeviceObject,
                   db.DeviceObject.do_id == db.DFObject.do_id))
            .join(db.DeviceFeature)
            .filter(db.DFObject.dfo_id.in_(idfo_id_list))
            .order_by(db.DeviceObject.do_idx, db.DeviceFeature.df_name)
            .all()
        )]
        
        fn_id = -1
        for i in range(0, idf_count):
            for entry in (
                session.query(db.DF_Module)
                .filter(db.DF_Module.dfo_id == ordered_idfo_id_list[i], db.DF_Module.na_id == na_id)
                .all()
            ):
                entry.normalization = 0
                session.commit()
            join_data = db.MultipleJoin_Module(
                na_id = na_id, param_i = i,
                fn_id = fn_id,
                dfo_id = ordered_idfo_id_list[i]
            )
            session.add(join_data)
            session.commit()
    else:
        for dfo_id, in (
            session.query(db.MultipleJoin_Module.dfo_id)
            .filter(db.MultipleJoin_Module.na_id == na_id)
            .all()
        ):
            DF_Module = (
                session.query(db.DF_Module)
                .filter(db.DF_Module.dfo_id == dfo_id, db.DF_Module.na_id == na_id)
                .first()
            )
            DF_Module.normalization = 0
            session.commit()
        print('no join')
    

def remove_device_model_icon(do_id, p_id):
    session = g.session
    # turn other NetworkApplications black
    for i in (
        session.query(db.DF_Module)
        .join(db.NetworkApplication)
        .filter(db.NetworkApplication.p_id == p_id)
        .all()
    ):
        i.color = 'black'
        session.commit()

    # get all dfo_id under the given model
    dfo_id_list = []
    dfo_id_tuple_list= (
        session.query(db.DFObject.dfo_id)
        .filter(db.DFObject.do_id == do_id)
        .all()
    )
    for _id in dfo_id_tuple_list:
        dfo_id_list.append(_id[0])


    # get all na_id connected by the dfo_ids
    na_id_list = []
    if dfo_id_list == []:
        na_id_tuple_list = []
    else:
        na_id_tuple_list = (
            session.query(db.DF_Module.na_id)
            .filter(db.DF_Module.dfo_id.in_(dfo_id_list))
            .group_by(db.DF_Module.na_id)
            .all()
        )
    for _id in na_id_tuple_list:
        na_id_list.append(_id[0])
    # check if all NetworkApplications are disabled
    total_connected_line = 0
    for dfo_id in dfo_id_list:
        total_connected_line += len(
            session.query(func.count(db.DF_Module.dfo_id))
            .filter(db.DF_Module.dfo_id == dfo_id, db.DF_Module.na_id.in_(na_id_list))
            .group_by(db.DF_Module.dfo_id)
            .all()
        )
    if total_connected_line == 0:
        # delete DFObject
        for dfo_id in dfo_id_list:
            (
                session.query(db.DFObject)
                .filter(db.DFObject.dfo_id == dfo_id)
                .delete()
            )
            session.commit()

        # delete the model block
        (
            session.query(db.DeviceObject)
            .filter(db.DeviceObject.do_id == do_id)
            .delete()
        )
        session.commit()
        return 'ok'

    # delete the NetworkApplication lines
    for dfo_id in dfo_id_list:
        (
            session.query(db.DF_Module)
            .filter(db.DF_Module.dfo_id == dfo_id)
            .delete()
        )
        session.commit()

    # delete join modules
    for na_id in na_id_list:
        refresh_join_module(na_id)
        #(
        #    session.query(db.MultipleJoin_Module)
        #    .filter(db.MultipleJoin_Module.na_id == na_id)
        #    .delete()
        #)
        #session.commit()

    # check if IDF # connected with the circle > 0, and delete single circles
    for na_id in na_id_list:
        idf_count = len(
            session.query(func.count(db.DF_Module.dfo_id))
            .join(db.DFObject, db.DeviceFeature)
            .filter(db.DeviceFeature.df_type == 'input', db.DF_Module.na_id == na_id)
            .group_by(db.DF_Module.dfo_id)
            .all()
        )
        odf_count = len(
            session.query(func.count(db.DF_Module.dfo_id))
           .join(db.DFObject, db.DeviceFeature)
           .filter(db.DeviceFeature.df_type == 'output', db.DF_Module.na_id == na_id)
           .group_by(db.DF_Module.dfo_id)
           .all()
        )
        # remove the circle and all lines connected with it
        if idf_count == 0 or odf_count == 0:
            (
                session.query(db.DF_Module)
                .filter(db.DF_Module.na_id == na_id)
                .delete()
            )
            session.commit()
            (
                session.query(db.MultipleJoin_Module)
                .filter(db.MultipleJoin_Module.na_id == na_id)
                .delete()
            )
            session.commit()
            (
                session.query(db.NetworkApplication)
                .filter(db.NetworkApplication.na_id == na_id)
                .delete()
            )
            session.commit()

    # delete DFObject
    for dfo_id in dfo_id_list:
        (
            session.query(db.DFObject)
            .filter(db.DFObject.dfo_id == dfo_id)
            .delete()
        )
        session.commit()

    # delete the model block
    (
        session.query(db.DeviceObject)
        .filter(db.DeviceObject.do_id == do_id)
        .delete()
    )
    session.commit()
    
    return 'ok'


def create_new_device_object(model_info, p_id):
    session = g.session
#    return_model_info = {
#        'p_odf_list': [],
#        'p_idf_list': [],
#        'p_dm_name': [model_info['model_name'], None],
#        'in_do_id': None,
#        'out_do_id': None,
#        'dm_type': None,
#    }

    in_do_idx = 1
    out_do_idx = -1

    model_id = (
        session.query(db.DeviceModel.dm_id)
        .filter(db.DeviceModel.dm_name == model_info['model_name'])
        .first()
    )
    if model_id: model_id = model_id[0]
    else: return
    (max_idx, min_idx) = (
        session.query(func.max(db.DeviceObject.do_idx),
                      func.min(db.DeviceObject.do_idx))
        .filter(db.DeviceObject.p_id == p_id)
        .first()
    )

    # this block tries to determine the next do_idx for the db insertion
    if max_idx != None:
        if max_idx > 0:
            in_do_idx = max_idx + 1
        else:
            in_do_idx = 1
    if min_idx != None:
        if min_idx < 0:
            out_do_idx = min_idx - 1
        else:
            out_do_idx = -1

    idf_length = len(model_info['idf_list'])
    odf_length = len(model_info['odf_list'])

    # draw new idf models
    if idf_length > 0:
        DeviceObject_data = db.DeviceObject(p_id=p_id, dm_id=model_id, do_idx=in_do_idx, d_id=None)
        session.add(DeviceObject_data)
        session.commit()

        do_id = DeviceObject_data.do_id

        for i in range(idf_length):
            DFObject_data = db.DFObject(
                do_id=do_id,
                df_id=model_info['idf_list'][i][1],
                alias_name=model_info['idf_list'][i][0]
            )
            session.add(DFObject_data)
            session.commit()

    # draw new odf model
    if odf_length > 0:
        DeviceObject_data = db.DeviceObject(p_id=p_id, dm_id=model_id,do_idx=out_do_idx, d_id=None)
        session.add(DeviceObject_data)
        session.commit()

        do_id = DeviceObject_data.do_id

        for i in range(odf_length):
            DFObject_data = db.DFObject(
                do_id=do_id,
                df_id=model_info['odf_list'][i][1],
                alias_name=model_info['odf_list'][i][0]
            )
            session.add(DFObject_data)
            session.commit()
    
    return 'ok'

def modify_NetworkApplication_relationship(dfo_id, p_id):
    session = g.session
    # lock project
    #current_prj_status = (
    #    session.query(db.Project.status)
    #    .filter(db.Project.p_id == p_id)
    #    .first()[0]
    #)
    #close_project(p_id)

    all_connected_na_id = (
        session.query(db.DF_Module.na_id)
        .filter(db.DF_Module.dfo_id == dfo_id)
        .group_by(db.DF_Module.na_id)
        .all()
    )
    # remove the device feature
    (
        session.query(db.DF_Module)
        .filter(db.DF_Module.dfo_id == dfo_id)
        .delete()
    )
    session.commit()
    (
        session.query(db.MultipleJoin_Module)
        .filter(db.MultipleJoin_Module.dfo_id == dfo_id)
        .delete()
    )
    session.commit()
    # if one IDF left, remove the join module
    for na_id in all_connected_na_id:
        refresh_join_module(na_id[0])
        df_number = len(
            session.query(db.DF_Module.dfo_id)
            .filter(db.DF_Module.na_id == na_id[0])
            .group_by(db.DF_Module.dfo_id)
            .all()
        )
        if df_number == 0:
            (
                session.query(db.DF_Module)
                .filter(db.DF_Module.na_id == na_id[0])
                .delete()
            )
            session.commit()
            (
                session.query(db.NetworkApplication)
                .filter(db.NetworkApplication.na_id == na_id[0])
                .delete()
            )
            session.commit()
    p_id = (
        session.query(db.DeviceObject.p_id)
        .select_from(db.DeviceObject)
        .join(db.DFObject)
        .filter(db.DFObject.dfo_id == dfo_id)
        .first()
    )
    if p_id: p_id = p_id[0]
    for na_id, in (
        session.query(db.NetworkApplication.na_id)
        .filter(db.NetworkApplication.p_id == p_id)
    ):
        adjust_half_line(na_id)
    #if current_prj_status == 'on':
    #    open_project(p_id)
    reopen_project(p_id)
    
    return 'ok'


def pull_data(mac_addr=None, df_name=None, stage='Input', na_id=None, dfo_id=None):
    log_list = []
    #try:
    log = []
    print('******* ',stage.lower())
    if (stage == 'Output' or stage == 'Input') and mac_addr != None and df_name != None:
        log = csmapi.pull(mac_addr, df_name)
    else:
        log = csmapi.dfm_pull(na_id, dfo_id, stage.lower())
    if log == []:
        return log
    log = [log[0]]
    log_list = []
    for sample in log:
        time_format = time.strptime(sample[0], "%Y-%m-%d %H:%M:%S.%f")
        time_in_second = time.strftime('%H:%M:%S', time_format)
        round_sample = []
        for param_i in sample[1]:
            if isinstance(param_i, (int, float, complex)):
                round_sample.append('{0:.2f}'.format(param_i))
            else:
                round_sample.append(str(param_i))
        round_sample.insert(0, time_in_second)
        log_list.append(round_sample)
    #except:
    #    log_list = []
    return log_list[::-1]


def gen_data(df_range, df_type):
    '''type: int, float, boolean, void, string, json'''
    data = []
    for range_, type_ in zip(df_range, df_type):
        if type_ == 'int':
            val = random.randint(range_[0], range_[1])
        elif type_ == 'float':
            val = random.uniform(range_[0], range_[1])
        elif type_ == 'boolean':
            val = random.randint([True, False])
        elif type_ == 'void':
            val = None
        elif type_ == 'string':
            val = ''
        elif type_ == 'json':
            val = '{}'
        else:
            raise Exception('DF type not support: ' + type_)
        data.append(val)
    return data


def build_company_range_from_service(df_id, mf_id):
    session = g.session
    para_info = (
        session.query(db.DF_Parameter)
        .filter(db.DF_Parameter.df_id == df_id)
        .all()
    )
    for idx in range(len(para_info)):
        new_company_info = db.DF_Parameter(
            df_id = None,
            mf_id = mf_id,
            param_i = para_info[idx].param_i,
            param_type = para_info[idx].param_type,
            u_id = None,
            idf_type = para_info[idx].idf_type,
            fn_id = para_info[idx].fn_id,
            min = para_info[idx].min,
            max = para_info[idx].max,
            unit_id = para_info[idx].unit_id,
            normalization = para_info[idx].normalization
        )
        session.add(new_company_info)
        session.commit()
    
    return 'ok'


def get_icon_path(df_name):
    img_type = '.png'
    current_path = os.path.dirname(__file__)
    upload_img_path = os.path.join('static',
                                   'images',
                                   'upload_icon',
                                   df_name+img_type)
    default_img_path = os.path.join('static',
                                    'images',
                                    'ec_icon',
                                    df_name[0].upper()+img_type)
    # check if the uploaded icon exists
    if os.path.exists(os.path.join(current_path, upload_img_path)):
        return '/'+upload_img_path
    else:
    # check if the default icon exists
        if os.path.exists(os.path.join(current_path, default_img_path)):
            return '/'+default_img_path
    return ''


def adjust_half_line(na_id):
    session = g.session
    input_line = (
        session.query(db.DF_Module.dfo_id)
        .select_from(db.DF_Module)
        .join(db.DFObject, db.DeviceFeature)
        .filter(db.DF_Module.na_id == na_id, db.DeviceFeature.df_type == 'input')
        .group_by(db.DF_Module.dfo_id)
        .all()
    )

    output_line = (
        session.query(db.DF_Module.dfo_id)
        .select_from(db.DF_Module)
        .join(db.DFObject, db.DeviceFeature)
        .filter(db.DF_Module.na_id == na_id, db.DeviceFeature.df_type == 'output')
        .group_by(db.DF_Module.dfo_id)
        .all()
    )

    if len(input_line) == 0 or len(output_line) == 0:
        (
            session.query(db.MultipleJoin_Module)
            .filter(db.MultipleJoin_Module.na_id == na_id)
            .delete()
        )
        session.commit()
        (
            session.query(db.DF_Module)
            .filter(db.DF_Module.na_id == na_id)
            .delete()
        )
        session.commit()
        (
            session.query(db.NetworkApplication)
            .filter(db.NetworkApplication.na_id == na_id)
            .delete()
        )
        session.commit()
        for dfo_id, in (
            session.query(db.DF_Module.dfo_id)
            .filter(db.DF_Module.na_id == na_id)
            .group_by(db.DF_Module.dfo_id)
            .all()
        ):
            csmapi.dfm_reset(na_id, dfo_id)

        csmapi.dfm_reset(na_id, 0)
        
        return 1
    else:
        
        return 0


def open_project(p_id):
    session = g.session
    project = (
        session.query(db.Project)
        .filter(db.Project.p_id == p_id)
        .first()
    )
    project.status = 'on'
    session.commit()
    


def close_project(p_id):
    session = g.session
    project = (
        session.query(db.Project)
        .filter(db.Project.p_id == p_id)
        .first()
    )
    project.status = 'off'
    session.commit()
    


def reopen_project(p_id):
    session = g.session
    project = (
        session.query(db.Project)
        .filter(db.Project.p_id == p_id)
        .first()
    )
    project.restart = 1
    session.commit()
    
    print('*\n*\n reopen')

def process_monitor_data(log, param_no):
    if len(log) == 0:
        tmp = []
        for i in range(param_no+1):
            tmp.append(None)
        return [tmp]
    else:
        return log
############# end of utility function ########
def update_device_feature_object_for_device_object(p_id, dm_name):
    session = g.session
    device_info = {}
    ms_d_id = []
    df_name_id = {}
    res = False
    for d_id, mac_addr in(
        session.query(db.Device.d_id, db.Device.mac_addr)
        .select_from(db.Device)
        .join(db.DeviceModel)
        .join(db.DeviceObject)
        .join(db.Project)
        .filter(db.DeviceModel.dm_name == dm_name,
                db.Device.status == 'online',
                db.Project.p_id == p_id)
    ):
        device_info[d_id] = mac_addr
        ms_d_id.append(d_id)
        print(device_info)
    # retrieve the df_name and the df_id relationship
    for df_name, df_id in (
        session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id)
        .select_from(db.DM_DF)
        .join(db.DeviceFeature, db.DeviceModel, db.DeviceObject, db.Project)
        .filter(db.DeviceModel.dm_name == dm_name,
                db.Project.p_id == p_id)
    ):
        df_name_id[df_name] = df_id

    # hot plugin
    if ms_d_id == []:
        res = False
        return res

    device_objects = (
        session.query(db.DeviceObject)
        .filter(db.DeviceObject.d_id.in_(ms_d_id))
    )
    for do in device_objects:
        # lock project

        current_df_list = set([ df_name for (df_name,) in (
            session.query(db.DeviceFeature.df_name)
            .select_from(db.DFObject)
            .join(db.DeviceFeature)
            .filter(db.DFObject.do_id == do.do_id))
        ])
        csm_df_list = set(csmapi.pull(device_info[do.d_id], 'profile')['df_list'])

        if (csmapi.pull(device_info[do.d_id],'__Ctl_O__') == []):
            ControlChannel.SET_DF_STATUS(db,do.do_id)

        # add new one
        for df_name in list(csm_df_list - current_df_list):
            dfo_record = db.DFObject(
                do_id = do.do_id,
                df_id = df_name_id[df_name],
                alias_name = df_name,
            )
            session.add(dfo_record)
            res = True
            #ControlChannel.SET_DF_STATUS(db,do.do_id)
        session.commit()

        for df_name in list(current_df_list - csm_df_list):
            p_id = do.p_id
            #current_prj_status = (
            #    session.query(db.Project.status)
            #    .filter(db.Project.p_id == p_id)
            #    .first()[0]
            #)
            #close_project(p_id)

            dfo_id = (
                session.query(db.DFObject.dfo_id)
                .filter(db.DFObject.do_id == do.do_id,
                        db.DFObject.df_id == df_name_id[df_name])
                .first())
            if dfo_id:  dfo_id = dfo_id[0]
            else: break

            modify_NetworkApplication_relationship(dfo_id, p_id)
            (
                session.query(db.DFObject)
                .filter(db.DFObject.do_id == do.do_id,
                        db.DFObject.df_id == df_name_id[df_name])
                .delete()
            )
            session.commit()
            print('-----')
            res = True
            #ControlChannel.SET_DF_STATUS(db,do.do_id)
            #if current_prj_status == 'on':
            #    open_project(p_id)
            reopen_project(p_id)

#    if exception_status['redraw'] == True:
#        ControlChannel.SET_DF_STATUS(db,do.do_id)
    
    return res


def get_projects_info():
    session = g.session
    projects_info = (session.query(db.Project.p_id, db.Project.p_name, db.Project.status, db.Project.sim, db.Project.exception)
                     .select_from(db.Project)
                     .order_by(db.Project.p_name)
                     .all()
                    )
    
    return projects_info

#@app.route('/projectMgr', methods=['GET', 'POST'])
def projectMgr():
    projects_info = get_projects_info()
    return make_response(render_template('projectMgr.html', projects_info=projects_info))


@app.route('/get_file_info', methods=['POST'])
def get_file_info():
    '''
    input value:
        NULL
    return value:
        file_info = ['File_1', ...]
    '''
    #session = g.session

    onlyfiles = [f for f in listdir(os.getcwd() + "/da/Folder/files/") if isfile(join(os.getcwd() + "/da/Folder/files/", f)) if f[0] is not '.']
    return json.dumps(onlyfiles)

selected_Special_DM_in_prj = {}
def update_Special_DM_in_prj(p_id):
    global selected_Special_DM_in_prj
  
    if selected_models_in_prj_need_to_update.get(p_id) != False:
        session = g.session
        DM_in_project = (session.query(db.DeviceModel.dm_name)
            .select_from(db.DeviceModel)
            .join(db.DeviceObject)
            .join(db.Project)
            .filter(db.Project.p_id == p_id)
            .all())
        session.close()

        DM_list_in_prj = []
        if DM_in_project != []:
            for item in DM_in_project:
                DM_list_in_prj.append(item[0])
        
        Special_DM_in_prj = list(set(DM_list_in_prj).intersection(set(SpecialModel.dynamic_change_device_feature_list)))
        selected_Special_DM_in_prj[p_id] = Special_DM_in_prj.copy()
        selected_models_in_prj_need_to_update[p_id] = False
        
def check_redraw(p_id):
    if selected_Special_DM_in_prj.get(p_id) == None or selected_Special_DM_in_prj.get(p_id) == []: return False
    redraw = False
    for DM in selected_Special_DM_in_prj.get(p_id):
        state_changed = update_device_feature_object_for_device_object(p_id, DM)
        if state_changed:  
            redraw = True
    return redraw


@app.route('/get_exception_status', methods=['POST'])
def get_exception_status():
    '''
    input value:
        p_id
    return value:
        exception_status = {
            'exception_msg': 'msg',
            'btn_status': 'Exec'/'Stop'
        }
    '''
    session = g.session
    p_id = request.form['p_id']
    #print('\nget_exception_status:\n', p_id)
    exception_status = {
        'exception_msg': '',
        'btn_status': '',
        'redraw': False,
    }
    if (session.query(db.Project).filter(db.Project.p_id == p_id).first()) == None:
        exception_status['btn_status'] = 'Stop'
        return json.dumps(exception_status)

    (status, msg) = (
        session.query(db.Project.status, db.Project.exception)
        .filter(db.Project.p_id == p_id)
        .first()
    )
    #if msg != '':
    #    exception_msg = (
    #        session.query(db.Project)
    #        .filter(db.Project.p_id == p_id)
    #        .first()
    #    )
    #    exception_msg.exception = ''
    #    session.commit()
    #    open_project(p_id)
    #    #time.sleep(4)
    #    time.sleep(1.5)
    #    session = db.get_session()
    #    (status, msg) = (
    #        session.query(db.Project.status, db.Project.exception)
    #        .filter(db.Project.p_id == p_id)
    #        .first()
    #    )
    if msg != '' and status == 'on':
        exception_status['redraw'] = True
        exception_msg = (
            session.query(db.Project)
            .filter(db.Project.p_id == p_id)
            .first()
        )
        exception_msg.exception = ''
        session.commit()
    

    if status == 'on':
        exception_status['btn_status'] = 'Stop'
    else:
        exception_status['btn_status'] = 'Exec'

    if not msg.startswith('[anno]'):
        exception_status['exception_msg'] = msg
    #print('exception_status:\n', exception_status)


    if SpecialModel.enable_dynamic_device_feature_change: 
        update_Special_DM_in_prj(p_id)
        exception_status['redraw'] = check_redraw(p_id)   # If Dynamic_DF_change is ON, DFs may update and need to redraw.       
        

    return json.dumps(exception_status)


@app.route('/send_da_link', methods=['POST'])
def send_da_link():
    '''
    input value:
        download_info = {
            'mail_addr': 'example@example.com',
            'phone_num': '09XXXXXXX',
            'dm_name': 'CIC-brick',
        }
    output value:
        'ok'
    '''
    download_info = json.loads(request.form['download_info'])
    print('\nsend_da_link:\n', download_info)
    dm_name = download_info['dm_name']
    mail_addr = download_info['mail_addr']
    phone_num = download_info['phone_num']

    if mail_addr != '':
        # mail content

        if (dm_name == 'Dandelion'):
            download_link = (
                '\nhttp://pcs.csie.nctu.edu.tw/da/Dandelion.zip\n'
            )
        elif (dm_name == 'Dummy_Device'):
            download_link = (
                '\nhttp://pcs.csie.nctu.edu.tw/da/Dummy_device.zip\n'
            )
        elif (dm_name == 'Skeleton'):
            download_link = (
                '\nhttp://pcs.csie.nctu.edu.tw/da/Skeleton.zip\n'
            )
        elif (dm_name == 'Painting'):
            download_link = (
                '\nhttp://pcs.csie.nctu.edu.tw/da/Painting.zip\n'
            )
        else:
            download_link = (
                '\nhttp://pcs.csie.nctu.edu.tw/da/{0}.apk\n'.format(''.join(dm_name.split()))
            )

        mail_content = (
            'Download the DA app for "{0}" from the following link:{1}'.format(dm_name, download_link)
        )
        mail_title = '[IoTtalk] "{0}" DA download'.format(dm_name)
        print('\n', mail_content, '\n')
        subprocess.call('echo \'{0}\' | mail -s \'{1}\' {2}'.format(mail_content, mail_title, mail_addr), shell=True)

    if phone_num != '':
        # mail content

        if (dm_name == 'Dandelion'):
            download_link = (
                '\nhttp://pcs.csie.nctu.edu.tw/da/Dandelion.zip\n'
            )
        elif (dm_name == 'Skeleton'):
            download_link = (
                '\nhttp://pcs.csie.nctu.edu.tw/da/Skeleton.zip\n'
            )
        elif (dm_name == 'Painting'):
            download_link = (
                '\nhttp://pcs.csie.nctu.edu.tw/da/Painting.zip\n'
            )
        else:
            download_link = (
                '\nhttp://pcs.csie.nctu.edu.tw/da/{0}.apk\n'.format(''.join(dm_name.split()))
            )

        sms_content = (
            'Download the DA app for "{0}" from the following link:{1}'.format(dm_name, download_link)
        )
        print('\n', sms_content, '\n')
        send_SMS(sms_content, phone_num)

    return 'ok'


@app.route('/send_download_link_mail', methods=['POST'])
def send_download_link_mail():
    '''
    input value:
        download_info = {
            'mail_addr': 'example@example.com',
            'dm_name': 'CIC-brick',
        }
    output value:
        'ok'
    '''
    download_info = request.form['download_info']
    download_info = json.loads(download_info)
    print('\nsend_download_link_mail:\n', download_info)
    print('*\n*\n*\n*\n')
    dm_name = download_info['dm_name']
    mail_addr = download_info['mail_addr']

    # mail content
    download_link = (
        '\nhttp://openmtc.darkgerm.com:7788/static/da/{0}.apk\n'.format(''.join(dm_name.split()))
    )
    mail_content = (
        'Download the DA app for "{0}" from the following link:{1}'.format(dm_name, download_link)
    )
    mail_title = '[EasyConnect] "{0}" DA download'.format(dm_name)
    print('\n', mail_content, '\n')
    subprocess.call('echo \'{0}\' | mail -s \'{1}\' {2}'.format(mail_content, mail_title, mail_addr), shell=True)
    return 'ok'


@app.route('/send_download_link_sms', methods=['POST'])
def send_download_link_sms():
    '''
    input value:
        download_info = {
            'tel': '0800449449',
            'dm_name': 'CIC-brick',
        }
    output value:
        'ok'
    '''
    download_info = request.form['download_info']
    download_info = json.loads(download_info)
    print('\nsend_download_link_sms:\n', download_info)
    dm_name = download_info['dm_name']
    tel = download_info['tel']

    # mail content
    download_link = (
        '\nhttp://openmtc.darkgerm.com:7788/static/da/{0}.apk\n'.format(''.join(dm_name.split()))
    )
    content = (
        'Download the DA app for "{0}" from the following link:{1}'.format(dm_name, download_link)
    )
    print('\n', content, '\n')
    send_SMS(content, tel)
    return 'ok'


@app.route('/pull_test', methods=['POST'])
def pull_test():
    try:
        log = csmapi.pull('fffffffffffa', 'G-sensor')
    except:
        log = {'timestamp_full':[''], 'data':[0]}
    timestamp_full = log['timestamp_full'][::-1]
    data = log['data']
    return_info = {
        'timestamp_full': [],
        'data': data[::-1],
    }
    return_info2 = []

    for i in range(len(timestamp_full)):
        try:
            time_format = time.strptime(timestamp_full[i], "%Y-%m-%d %H:%M:%S.%f")
            time_in_second = int(time.mktime(time_format))*1000
            return_info['timestamp_full'].append(time_in_second)
        except:
            time_format = time.strptime(str(datetime.datetime.now()), "%Y-%m-%d %H:%M:%S.%f")
            time_in_second = int(time.mktime(time_format))*1000
            return_info['timestamp_full'].append(time_in_second)
    return json.dumps(return_info)

@app.route('/create_model_without_select_feature_list', methods=['GET'])
def create_model_without_select_feature_list():
    return json.dumps(SpecialModel.create_model_without_select_feature_list)

@app.route('/plural_df_list', methods=['GET'])
def plural_df_list():
    return json.dumps(SpecialModel.plural_df_list)

@app.route('/connection_with_p_id_p_pwd', methods=['POST'])
def connection_with_p_id_p_pwd():
    
    p_id = request.form['p_id']
    p_pwd = request.form['p_pwd']
    print('p_id: ' + p_id + "\n" + 'p_pwd: ' + p_pwd);

    session = g.session
    
    project = (session.query(db.Project.p_id)
        .filter(db.Project.p_id == p_id)
        .first()
    )
    if project == None:
        return redirect('/connection')

    #check project password
    m = hashlib.md5()
    m.update(p_pwd.encode('utf-8'))
    p_pwd = m.hexdigest()
    projectPwd = (session.query(db.Project.pwd)
        .filter(db.Project.p_id == p_id)
        .first()
    )
    #get project name
    projectName = (session.query(db.Project.p_name)
        .filter(db.Project.p_id == p_id)
        .first()
    )
    p_name = projectName[0]

   

    # model_list = []
    # for data in (
    #     session.query(db.DeviceModel.dm_name)
    #     .order_by(db.DeviceModel.dm_name)
    # ):
    #     model_list.append(data[0])

    # turn other connections black
    if projectPwd[0] != p_pwd:
        
        return json.dumps({'p_id':p_id, 'p_name':p_name, 'result':False})
    else:
        for i in (
            session.query(db.DF_Module)
            .join(db.NetworkApplication)
            .filter(db.NetworkApplication.p_id == p_id).all()
        ):
            i.color = 'black'
            session.commit()
        
        return json.dumps({'p_id':p_id, 'p_name':p_name, 'result':True})


def connection():
    '''
    input value:
        None / p_id
    output value:
        None
    '''
    session = g.session
#    u_id = 1

#    p_id = (session.query(db.Project.p_id)
#        .select_from(db.Project)
#        # .outerjoin(db.DeviceObject)
#        # .filter(db.DeviceObject.do_id == None)
#        .first()
#    )
    model_list = []
#    for data in (
#        session.query(db.DeviceModel.dm_name)
#        .order_by(db.DeviceModel.dm_name)
#    ):
#        model_list.append(data[0])

    project_list = session.query(db.Project.p_name, db.Project.p_id).all()
    
    
    if len(project_list) != 0:
        project_list.insert(0, ('add project', 0))
        return render_template('index.html',
                        join_number = range(0,30),
                        model_list = model_list,
                        project_list = project_list,
                        p_id = -2,
                        p_name = "Select a project")
    else:
        return render_template('index.html',
                        join_number = range(0,30),
                        model_list = model_list,
                        project_list = project_list,
                        p_id = -1,
                        p_name = "Add new project")

# Use authentication to reset project password API - ref: IOTTALKV1-1
# @app.route('/reset_project_password', methods=['POST'])
def reset_project_password():
    p_id = request.form.get('p_id')
    p_pwd = request.form.get('p_pwd')

    m = hashlib.md5()
    m.update(p_pwd.encode('utf-8'))
    p_pwd = m.hexdigest()

    session = g.session
    session.query(db.Project).filter(db.Project.p_id == p_id).update({'pwd': p_pwd})
    session.commit()
    
    return 'ok'

@app.route('/check_project_password_is_exist', methods=['POST'])
def check_project_password_is_exist():
    p_id = request.form['p_id']
    session = g.session
    projectPwd = (session.query(db.Project.pwd)
        .filter(db.Project.p_id == p_id)
        .first()
    )
    
    m = hashlib.md5()
    m.update("".encode('utf-8'))
    return json.dumps({'status': 'ok','is_exist':(m.hexdigest() != projectPwd[0])})

@app.route('/new_project', methods=['POST'])
def new_project():
    '''
    input value:
        p_name
    output value:
        p_id
    '''
    u_id = 1
    session = g.session
    p_name = request.form['p_name']
    p_pwd = request.form['p_pwd']
    print('\nnew_project:\n', p_name)
    m = hashlib.md5()
    m.update(p_pwd.encode('utf-8'))
    p_pwd = m.hexdigest()
    new_project = db.Project(
        p_name = p_name,
        pwd = p_pwd,
        status = 'off',
        restart = 0,
        u_id = u_id,
        exception = '',
        sim = 'off'
    )
    session.add(new_project)
    session.commit()
    
    new_project.p_name += str(new_project.p_id)
    print(new_project.p_id)
    return str(new_project.p_id)


@app.route('/get_device_feature_list', methods=['POST'])
def get_device_feature_list():
    '''
    input value:
        None
    output value:
        df_list = ['G-sensor', ...]
    '''
    session = g.session
    print('\n\nget_device_feature_list:\n')
    df_list = []

    for data in (
        session.query(db.DeviceFeature.df_name)
        .order_by(db.DeviceFeature.df_name)
    ):
        df_list.append(data[0])

    df_list = json.dumps(df_list)
    print('return info:\n', df_list)
    
    return df_list

@app.route('/get_project_list', methods=['POST'])
def get_project_list():
    '''
    input value:
        None
    output value:
        project_list = [(project_name,p_id), ...]
    '''
    session = g.session
    project_list = session.query(db.Project.p_name, db.Project.p_id).order_by(db.Project.p_name).all()
    project_list.insert(0, ('add project', 0));

    project_list = json.dumps(project_list)
    print('return info:\n', project_list)
    
    return project_list

@app.route('/get_model_list', methods=['POST'])
def get_model_list():
    '''
    input value:
        None
    output value:
        model_list = ['Bulb', ...]
    '''
    session = g.session
    print('\n\nget_model_list:\n')
    model_list = session.query(db.DeviceModel.dm_name, db.DeviceModel.dm_id).order_by(db.DeviceModel.dm_name).all()
    model_list = json.dumps(model_list)
    print('return info:\n', model_list)
    
    return model_list


@app.route('/reload_connect_line', methods=['POST'])
def reload_connect_line():
    '''
    input value:
        p_id
    return value:
        connection_pair = [[na_id, dfo_id, color], ...]
    '''
    p_id = request.form['p_id']
    session = g.session
    connection_pair = []
    print('\nreload_connect_line:\n', p_id)
    for na_id, dfo_id, color in (
        session.query(db.DF_Module.na_id, db.DF_Module.dfo_id, db.DF_Module.color)
        .filter(db.NetworkApplication.p_id == p_id)
        .group_by(db.DF_Module.na_id, db.DF_Module.dfo_id)
    ):
        connection_pair.append([na_id, dfo_id, color])

    connection_pair = json.dumps(connection_pair)

    print(connection_pair)
    
    return connection_pair


@app.route('/reload_data', methods=['POST'])
def reload_data():
    '''
    input value:
        p_id
    return value:
        model_block = {
            'in_device': [
                {
                    'p_idf_list': p_idf_list,
                    'p_dm_name': p_dm_name,
                    'in_do_id': in_do_id,
                    'dm_type': dm_type,
                }, ...
            ]
            'out_device': [
                {
                    'p_odf_list': p_odf_list,
                    'p_dm_name': p_dm_name,
                    'out_do_id': out_do_id,
                    'dm_type': dm_type,
                }, ...
            ]
            'join': [
                [
                    na_id,
                    na_name,
                    na_idx
                ], ...
            ]
        }
    '''
    p_id = request.form['p_id']
    print('\nreload_data:\n', p_id)
    session = g.session
    model_block = {'in_device': [], 'out_device': [], 'join': []}

    for na_id, na_name, na_idx in (
        session.query(db.NetworkApplication.na_id,
        db.NetworkApplication.na_name, db.NetworkApplication.na_idx)
        .filter(db.NetworkApplication.p_id == p_id)
    ):
        model_block['join'].append([
            na_id,
            na_name,
            na_idx
        ])

    # get in_device_model_list
    do_id_list = (
        session.query(db.DeviceObject.do_id)
        .filter(db.DeviceObject.p_id == p_id, db.DeviceObject.do_idx > 0)
        .order_by(asc(db.DeviceObject.do_idx))
        .all()
    )

    # idf in each device model
    for do_id, in do_id_list:
        p_idf_list = []
        p_dm_name = []
        in_do_id = do_id
        feature_id_list = []
        feature_name_list = []
        (dm_name, dm_type, d_id) = (
            session.query(db.DeviceModel.dm_name, db.DeviceModel.dm_type, db.DeviceObject.d_id)
            .select_from(db.DeviceObject)
            .join(db.DeviceModel)
            .filter(db.DeviceObject.do_id == do_id)
            .first()
        )

        if d_id:
            device_info = (
                session.query(db.Device.d_name)
                .filter(db.Device.d_id == d_id)
                .first()
            )
            if device_info:
                p_dm_name.append(device_info[0])
                p_dm_name.append(d_id)
                p_dm_name.append(0) # for is_sim
            else:
                p_dm_name.append(dm_name)
                p_dm_name.append(d_id)
                p_dm_name.append(1)
        else:
            p_dm_name.append(dm_name)
            p_dm_name.append(d_id)
            p_dm_name.append(1)

        for fid, fname, alias_name in (
            session.query(db.DFObject.dfo_id, db.DeviceFeature.df_name, db.DFObject.alias_name)
            .select_from(db.DFObject)
            .join(db.DeviceFeature)
            .filter(db.DFObject.do_id == do_id)
            .order_by(db.DeviceFeature.df_name)
        ):
            p_idf_list.append([
                alias_name,
                fid,
                get_icon_path(fname)
            ])

        model_block['in_device'].append({
            'p_idf_list': p_idf_list,
            'p_dm_name': p_dm_name,
            'in_do_id': in_do_id,
            'dm_type': dm_type,
        })

    # get out_device
    do_id_list = (
        session.query(db.DeviceObject.do_id)
        .filter(db.DeviceObject.p_id == p_id, db.DeviceObject.do_idx < 0)
        .order_by(desc(db.DeviceObject.do_idx))
        .all()
    )
    # out_device
    for do_id, in do_id_list:
        p_odf_list = []
        p_dm_name = []
        out_do_id = do_id
        feature_id_list = []
        feature_name_list = []
        (dm_name, dm_type, d_id) = (
            session.query(db.DeviceModel.dm_name, db.DeviceModel.dm_type, db.DeviceObject.d_id)
            .select_from(db.DeviceObject).join(db.DeviceModel)
            .filter(db.DeviceObject.do_id == do_id)
            .first()
        )

        device_info = None
        if d_id:
            device_info = (
                session.query(db.Device.d_name)
                .filter(db.Device.d_id == d_id)
                .first()
            )

        if device_info:
            p_dm_name.append(device_info[0])
            p_dm_name.append(d_id)
            p_dm_name.append(0) # for is_sim
        else:
            p_dm_name.append(dm_name)
            p_dm_name.append(d_id)
            p_dm_name.append(1)

        for fid, fname, alias_name in (
            session.query(db.DFObject.dfo_id, db.DeviceFeature.df_name, db.DFObject.alias_name)
            .select_from(db.DFObject)
            .join(db.DeviceFeature)
            .filter(db.DFObject.do_id == do_id)
            .order_by(db.DeviceFeature.df_name)
        ):
            p_odf_list.append([
                alias_name,
                fid,
                get_icon_path(fname)
            ])

        model_block['out_device'].append({
            'p_odf_list': p_odf_list,
            'p_dm_name': p_dm_name,
            'out_do_id': out_do_id,
            'dm_type': dm_type,
        })

    model_block = json.dumps(model_block)
    print(model_block)
    
    return model_block


@app.route('/get_model_feature', methods=['POST'])
def get_model_feature():
    '''
    input value:
        dm_name = request.form['dm_name']
    return value:
        df = {
            'number_of_df': 3,
            'idf': [[df_name, df_id, comment], ...],
            'odf': [[df_name, df_id, comment], ...],
            'model_name': model_name,
            'model_id': model_id,
            'model_type': 'P'/'O'/'W',
        }
    '''
    session = g.session
    idf_info = []
    odf_info = []
    number_of_df = 0
    dm_name = request.form['dm_name']
    #model_name = 'Smartphone'
    print('\nget_model_feature:\n', dm_name)
    df_info = {
        'number_of_df': None,
        'idf': [],
        'odf': [],
        'model_name': '',
        'model_id': 0,
        'model_type': 'o'
    }
    if dm_name == '':
        return json.dumps(df_info)
    (model_id, model_type) = (
        session.query(db.DeviceModel.dm_id, db.DeviceModel.dm_type)
        .filter(db.DeviceModel.dm_name == dm_name)
        .first()
    )
    if model_type == 'smartphone':
        model_type = 'P'
    elif model_type == 'wearable':
        model_type = 'W'
    else:
        model_type = 'O'

    for df_name, df_id, comment in (
        session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id, db.DeviceFeature.comment)
        .join(db.DM_DF)
        .join(db.DeviceModel)
        .filter(db.DeviceModel.dm_name == dm_name, db.DeviceFeature.df_type == 'input')
        .order_by(db.DeviceFeature.df_name)
    ):
        idf_info.append([df_name, df_id, comment])
        number_of_df += 1
    for df_name, df_id, comment in (
        session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id, db.DeviceFeature.comment)
        .join(db.DM_DF)
        .join(db.DeviceModel)
        .filter(db.DeviceModel.dm_name == dm_name, db.DeviceFeature.df_type == 'output')
        .order_by(db.DeviceFeature.df_name)
    ):
        odf_info.append([df_name, df_id, comment])
        number_of_df += 1

    df_info['number_of_df'] = number_of_df
    df_info['idf'] = idf_info
    df_info['odf'] = odf_info
    df_info['model_name'] =  dm_name
    df_info['model_id'] = model_id
    df_info['model_type'] = model_type

    df = json.dumps(df_info)
    
    return df


@app.route('/get_model_info_for_da', methods=['POST'])
def get_model_info_for_da():
    '''
    input value:
        model_name = request.form['model_name']
    return value:
        df = {
            'number_of_df': 3,
            'idf': [[df_name, df_id, comment], ...],
            'odf': [[df_name, df_id, comment], ...],
            'model_name': model_name,
            'model_id': model_id,
            'model_type': 'P'/'O'/'W',
        }
    '''
    session = g.session
    idf_info = []
    odf_info = []
    number_of_df = 0
    model_name = request.form['model_name']
    #model_name = 'Smartphone'
    print('\nget_model_info_for_da:\n', model_name)
    df_info = {
        'number_of_df': None,
        'idf': [],
        'odf': [],
        'model_name': '',
        'model_id': 0,
        'model_type': 'o'
    }
    if model_name == '':
        return json.dumps(df_info)
    (model_id, model_type) = (
        session.query(db.DeviceModel.dm_id, db.DeviceModel.dm_type)
        .filter(db.DeviceModel.dm_name == model_name)
        .first()
    )
    if model_type == 'smartphone':
        model_type = 'P'
    elif model_type == 'wearable':
        model_type = 'W'
    else:
        model_type = 'O'

    for df_name, df_id, comment in (
        session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id, db.DeviceFeature.comment)
        .join(db.DM_DF)
        .join(db.DeviceModel)
        .filter(db.DeviceModel.dm_name == model_name, db.DeviceFeature.df_type == 'input')
    ):
        idf_info.append([df_name, df_id, comment])
        number_of_df += 1
    for df_name, df_id, comment in (
        session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id, db.DeviceFeature.comment)
        .join(db.DM_DF)
        .join(db.DeviceModel)
        .filter(db.DeviceModel.dm_name == model_name, db.DeviceFeature.df_type == 'output')
    ):
        odf_info.append([df_name, df_id, comment])
        number_of_df += 1

    df_info['number_of_df'] = number_of_df
    df_info['idf'] = idf_info
    df_info['odf'] = odf_info
    df_info['model_name'] =  model_name
    df_info['model_id'] = model_id
    df_info['model_type'] = model_type

    df = json.dumps(df_info)
    
    return df


@app.route('/get_model_info', methods=['POST'])
def get_model_info():
    '''
    input value:
        model_info = request.form['model_info']
        {
            'model_name': ...,
            'p_id': p_id,
        }
    return value:
        df = {
            'number_of_df': 3,
            'idf': [[df_name, df_id, comment], ...],
            'odf': [[df_name, df_id, comment], ...],
            'model_name': model_name,
            'model_id': model_id,
            'model_type': 'P'/'O'/'W',
        }
    '''
    session = g.session
    idf_info = []
    odf_info = []
    number_of_df = 0
    model_info = json.loads(request.form['model_info'])
    model_name = model_info['model_name']
    p_id = model_info['p_id']
    #model_name = 'Smartphone'
    print('\nget_model_info:\n', model_info)
    df_info = {
        'number_of_df': None,
        'idf': [],
        'odf': [],
        'model_name': '',
        'model_id': 0,
        'model_type': 'o'
    }
    if model_name == '':
        return json.dumps(df_info)
    (model_id, model_type) = (
        session.query(db.DeviceModel.dm_id, db.DeviceModel.dm_type)
        .filter(db.DeviceModel.dm_name == model_name)
        .first()
    )
    if model_type == 'smartphone':
        model_type = 'P'
    elif model_type == 'wearable':
        model_type = 'W'
    else:
        model_type = 'O'

    for df_name, df_id, comment in (
        session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id, db.DeviceFeature.comment)
        .join(db.DM_DF)
        .join(db.DeviceModel)
        .filter(db.DeviceModel.dm_name == model_name, db.DeviceFeature.df_type == 'input')
        .order_by(db.DeviceFeature.df_name)
    ):
        idf_info.append([df_name, df_id, comment])
        number_of_df += 1
    for df_name, df_id, comment in (
        session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id, db.DeviceFeature.comment)
        .join(db.DM_DF)
        .join(db.DeviceModel)
        .filter(db.DeviceModel.dm_name == model_name, db.DeviceFeature.df_type == 'output')
        .order_by(db.DeviceFeature.df_name)
    ):
        odf_info.append([df_name, df_id, comment])
        number_of_df += 1

    df_info['number_of_df'] = number_of_df
    df_info['idf'] = idf_info
    df_info['odf'] = odf_info
    df_info['model_name'] =  model_name
    df_info['model_id'] = model_id
    df_info['model_type'] = model_type

    df = json.dumps(df_info)

    # turn other NetworkApplications black
    for i in (
        session.query(db.DF_Module)
        .join(db.NetworkApplication)
        .filter(db.NetworkApplication.p_id == p_id)
        .all()
    ):
        i.color = 'black'
        session.commit()
    
    return df

# modify add comments
@app.route('/get_model_icon_info', methods=['POST'])
def get_model_icon_info():
    '''
    input value:
        model_icon_info = request.form['model_icon_info']
        {
            'do_id': do_id,
            'p_id': p_id,
        }
    return value:
        df = {
            'number_of_df': 3,
            'idf': [[df_name, df_id, '0'/'1', comment], ...],
            'odf': [[df_name, df_id, '0'/'1', comment], ...],
                 - '1': selected
            'model_name': model_name,
            'do_id': do_id,
        }
    '''
    session = g.session
    idf_info = []
    odf_info = []
    number_of_df = 0
    selected_idf = []
    selected_odf = []

    model_icon_info = json.loads(request.form['model_icon_info'])
    do_id = model_icon_info['do_id']
    p_id = model_icon_info['p_id']
    print('\n\nget_model_icon_info:\n', model_icon_info)
    dm_id = (
        session.query(db.DeviceObject.dm_id)
        .filter(db.DeviceObject.do_id == do_id)
        .first()
    )
    if dm_id: dm_id = dm_id[0]
    model_name = (
        session.query(db.DeviceModel.dm_name)
        .filter(db.DeviceModel.dm_id == dm_id)
        .first()
    )
    if model_name: model_name = model_name[0]
    for df_id in (
        session.query(db.DeviceFeature.df_id)
        .select_from(db.DFObject)
        .join(db.DeviceFeature)
        .filter(db.DFObject.do_id == do_id, db.DeviceFeature.df_type == 'input')
    ):
        selected_idf.append(df_id[0])

    for df_id in (
        session.query(db.DeviceFeature.df_id)
        .select_from(db.DFObject)
        .join(db.DeviceFeature)
        .filter(db.DFObject.do_id == do_id, db.DeviceFeature.df_type == 'output')
    ):
        selected_odf.append(df_id[0])

    for df_name, df_id, comment in (
        session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id, db.DeviceFeature.comment)
        .join(db.DM_DF, db.DeviceModel)
        .filter(db.DeviceModel.dm_id == dm_id, db.DeviceFeature.df_type == 'input')
        .order_by(db.DeviceFeature.df_name)
    ):
        if df_id in selected_idf:
            idf_info.append([df_name, df_id, 1, comment])
        else:
            idf_info.append([df_name, df_id, 0, comment])
        number_of_df += 1

    for df_name, df_id, comment in (
        session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id, db.DeviceFeature.comment)
        .join(db.DM_DF, db.DeviceModel)
        .filter(db.DeviceModel.dm_id == dm_id, db.DeviceFeature.df_type == 'output')
        .order_by(db.DeviceFeature.df_name)
    ):
        if df_id in selected_odf:
            odf_info.append([df_name, df_id, 1, comment])
        else:
            odf_info.append([df_name, df_id, 0, comment])
        number_of_df += 1

    df_info = {
        'number_of_df': number_of_df,
        'idf': idf_info,
        'odf': odf_info,
        'model_name': model_name,
        'do_id': do_id
    }
    df = json.dumps(df_info)

    print('return_info:\n', df)

    # turn other NetworkApplications black
    for i in (
        session.query(db.DF_Module)
        .join(db.NetworkApplication)
        .filter(db.NetworkApplication.p_id == p_id)
        .all()
    ):
        i.color = 'black'
        session.commit()
    
    return df


@app.route('/create_device_object', methods=['POST'])
def create_device_object():
    '''
    input value:
        dm_info = {
            'p_id': 1,
            'dm_name': 'Acceleration',
            'idf_list': ['A', 'B', ...],
            'odf_list': ['A', 'B', ...]
        }
    output value:
        res = {
            'ido_id': None,
            'odo_id': None,
            'idfo_id_list': [],
            'odfo_id_list': [],
        }
    '''

    dm_info = json.loads(request.form['dm_info'])
    session = g.session
    print('create_device_object:\n', dm_info)
    p_id = dm_info['p_id']
    dm_name = dm_info['dm_name']
    idf_list = dm_info['idf_list']
    odf_list = dm_info['odf_list']

    dm_id = (
        session.query(db.DeviceModel.dm_id)
        .filter(db.DeviceModel.dm_name == dm_name)
        .first()
    )
    if dm_id: dm_id = dm_id[0]
    result = {
        'ido_id': None,
        'odo_id': None,
        'idfo_id_list': [],
        'odfo_id_list': [],
    }

    if idf_list != []:
        max_do_idx = (session.query(func.max(db.DeviceObject.do_idx))
            .filter(db.DeviceObject.p_id == p_id)
            .first()[0]
        )

        if max_do_idx != None and max_do_idx > 0:
            max_do_idx = max_do_idx + 1
        else:
            max_do_idx = 1

        do = db.DeviceObject(
            p_id = p_id,
            dm_id = dm_id,
            d_id = None,
            do_idx = max_do_idx,
        )
        session.add(do)
        session.commit()
        result['ido_id'] = do.do_id

#        for df_name in idf_list:
        index = 0
        while index < len(idf_list):
            df_id = (
                session.query(db.DeviceFeature.df_id)
#                .filter(db.DeviceFeature.df_name == df_name)
                .filter(db.DeviceFeature.df_name == idf_list[index])
                .first()
            )
            if df_id: df_id = df_id[0]
            if dm_name == "Folder_I":
                index += 1

            dfo = db.DFObject(
                do_id = do.do_id,
                df_id = df_id,
#                alias_name = df_name,
                alias_name = idf_list[index],
            )
            session.add(dfo)
            session.commit()
            result['idfo_id_list'].append(dfo.dfo_id)
            index += 1

    if odf_list != []:
        min_do_idx = (session.query(func.min(db.DeviceObject.do_idx))
            .filter(db.DeviceObject.p_id == p_id)
            .first()
        )
        if min_do_idx: min_do_idx = min_do_idx[0]
        if min_do_idx != None and min_do_idx < 0:
            min_do_idx = min_do_idx - 1
        else:
            min_do_idx = -1

        do = db.DeviceObject(
            p_id = p_id,
            dm_id = dm_id,
            d_id = None,
            do_idx = min_do_idx,
        )
        session.add(do)
        session.commit()
        result['odo_id'] = do.do_id

#        for df_name in odf_list:
        index = 0
        while index < len(odf_list):
            df_id = (
                session.query(db.DeviceFeature.df_id)
#                .filter(db.DeviceFeature.df_name == df_name)
                .filter(db.DeviceFeature.df_name == odf_list[index])
                .first()
            )
            if df_id: df_id = df_id[0]
            if dm_name == "Folder_O":
                index += 1

            dfo = db.DFObject(
                do_id = do.do_id,
                df_id = df_id,
#                alias_name = df_name,
                alias_name = odf_list[index],
            )
            session.add(dfo)
            session.commit()
            result['odfo_id_list'].append(dfo.dfo_id)
            index += 1

    
    global selected_models_in_prj_need_to_update
    selected_models_in_prj_need_to_update[p_id] = True

    return json.dumps(result)


@app.route('/save_device_object_info', methods=['POST'])
def save_device_object_info():
    '''
    input value:
        model_info = {
            'odf_list': [[df_name, df_id], ...],
            'idf_list': [[df_name, df_id], ...],
            'model_name': dm_name,
            'do_id': do_id,
            'p_id': p_id,
        }
    output value:
        return_model_info = {
            'p_odf_list': [[df_name, dfo_id], ...],
            'p_idf_list': [[df_name, dfo_id], ...],
            'p_dm_name': [dm_name, None],
            'in_do_id': do_id,
            'out_do_id': do_id,
            'dm_type': dm_type,
        }
    '''
    session = g.session
    model_info = json.loads(request.form['model_info'])
    print('\n\nsave_device_object_info:\n', model_info)

    p_id = model_info['p_id']
    return_model_info = {
        'p_odf_list': [],
        'p_idf_list': [],
        'p_dm_name': [model_info['model_name'], None],
        'in_do_id': None,
        'out_do_id': None,
        'dm_type': None,
    }

    do_id = int(model_info['do_id'])
    model_name = model_info['model_name']
    if do_id == 0:
        create_new_device_object(model_info, p_id)
    else:
        dm_id = (
            session.query(db.DeviceObject.dm_id)
            .filter(db.DeviceObject.do_id == do_id)
            .first()
        )
        if dm_id: dm_id = dm_id[0]
        # check the model type (input / output) first
        do_idx = (
            session.query(db.DeviceObject.do_idx)
            .filter(db.DeviceObject.do_id == do_id)
            .first()
        )
        if do_idx: do_idx = do_idx[0]
        if do_idx > 0:
            origin_df_list = model_info['idf_list']
            model_info['idf_list'] = []
            df_type = 'input'
        else:
            origin_df_list = model_info['odf_list']
            model_info['odf_list'] = []
            df_type = 'output'

        origin_df_id_list = []
        modify_df_id_list = []
        for df in origin_df_list:
            modify_df_id_list.append(int(df[1]))

        for df_id in (
            session.query(db.DeviceFeature.df_id)
            .select_from(db.DFObject)
            .join(db.DeviceFeature)
            .filter(db.DFObject.do_id == do_id, db.DeviceFeature.df_type == df_type)
        ):
            origin_df_id_list.extend(df_id)
        origin_df_id_list.sort()

        # add new device features
        new_df_id_list = list(set(modify_df_id_list).difference(set(origin_df_id_list)))
        new_df_id_list.sort()
        new_df_list = []
        for id in new_df_id_list:
            for df in origin_df_list:
                if id == int(df[1]):
                    new_df_list.append(df)
                    break;
        for df in new_df_list:
            dfo_obj = db.DFObject(
                do_id = do_id,
                df_id = df[1],
                alias_name = df[0]
            )
            session.add(dfo_obj)
            session.commit()

        # delete device features
        remove_df_id_list = list(set(origin_df_id_list).difference(set(modify_df_id_list)))
        remove_df_id_list.sort()
        remove_dfo_id = []
        for id in remove_df_id_list:
            dfo_id = (
                session.query(db.DFObject.dfo_id)
                .filter(db.DFObject.do_id == do_id, db.DFObject.df_id == id)
                .first()
            )
            if dfo_id: dfo_id = dfo_id[0]
            else: continue
            modify_NetworkApplication_relationship(dfo_id, p_id)
            (
                session.query(db.DFObject)
                .filter(db.DFObject.dfo_id == dfo_id)
                .delete()
            )
            session.commit()
        # if all device features deleted, remove the device model
        if (
            session.query(db.DFObject.do_id)
            .filter(db.DFObject.do_id == do_id)
            .first()
           ) == None:
            remove_device_model_icon(do_id, p_id)

        # add new output model
        model_info['do_id'] = 0
        create_new_device_object(model_info, p_id)
    
    global selected_models_in_prj_need_to_update
    selected_models_in_prj_need_to_update[p_id] = True


    # turn other NetworkApplications black
    for df_module in (
        session.query(db.DF_Module)
        .join(db.NetworkApplication)
        .filter(db.NetworkApplication.p_id == p_id)
        .all()
    ):
        df_module.color = 'black'
        session.commit()

    reopen_project(p_id)
  
    ControlChannel.SET_DF_STATUS(db, do_id)
    
    return 'ok'

# modify
@app.route('/get_stage1_df_info', methods=['POST'])
def get_stage1_df_info():
    '''
    input value:
        stage1_info = {
            'dfo_id': dfo_id,
            'p_id': p_id,
        }
    return value:
        return_info = {
            'df_mapping_function': [[fn_name, fn_id], ...],
            'df_id': 2,
            'df_info': [['variant', fn_id, min, max], ...],
            'df_module_title': '',
            'df_fn_id': 1,
            'alias_name': 'lightness',
        }
    '''
    u_id = 1
    session = g.session

    stage1_info = json.loads(request.form['stage1_info'])
    p_id = stage1_info['p_id']
    dfo_id = stage1_info['dfo_id']

    print("\nget_stage1_df_info()\n")
    return_info = {
        'df_id': dfo_id,
        'df_info': [],
        'alias_name': None,
        'df_fn_id': None,
        'df_module_title': None,
    }

    # turn other NetworkApplications black
    for i in (
        session.query(db.DF_Module)
        .join(db.NetworkApplication)
        .filter(db.NetworkApplication.p_id == p_id)
        .all()
    ):
        i.color = 'black'
        session.commit()

    # get relevant mf_id from df_id & dm_id for dfo_id
    (dm_id, df_id) = (
        session.query(db.DeviceObject.dm_id, db.DFObject.df_id)
        .join(db.DFObject)
        .filter(db.DFObject.dfo_id == dfo_id)
        .first()
    )
    mf_id = (
        session.query(db.DM_DF.mf_id)
        .filter(db.DM_DF.dm_id == dm_id, db.DM_DF.df_id == df_id)
        .first()
    )
    if mf_id: mf_id = mf_id[0]

    result = (
        session.query(db.DFObject.alias_name)
        .filter(db.DFObject.dfo_id == dfo_id)
        .first()
    )
    if result: return_info['alias_name'] = result[0]

    result = (
        session.query(db.DeviceModel.dm_name)
        .filter(db.DeviceModel.dm_id == dm_id)
        .first()
    )
    if result: return_info['df_module_title'] = result[0]

    #priority1 (u_id)
    customize_default = (
        session.query(db.DF_Parameter.idf_type, db.DF_Parameter.min, db.DF_Parameter.max)
        .filter(db.DF_Parameter.u_id == u_id, db.DF_Parameter.mf_id == mf_id)
        .order_by(db.DF_Parameter.param_i)
        .all()
    )
    company_default = (
        session.query(db.DF_Parameter.idf_type, db.DF_Parameter.min, db.DF_Parameter.max)
        .filter(db.DF_Parameter.u_id == None, db.DF_Parameter.mf_id == mf_id)
        .order_by(db.DF_Parameter.param_i)
        .all()
    )

    if len(customize_default) > 0:
        for i in customize_default:
            return_info['df_info'].append(i)
        return_info = json.dumps(return_info)
        print('\ncustomized_default:\n', return_info)
        return return_info

    # priority2 (mf_id)
    elif len(company_default) > 0:
        for i in company_default:
            return_info['df_info'].append(i)

        return_info = json.dumps(return_info)
        print('\ncompany_default:\n', return_info)
        return return_info

    # priority3 (u_id & mf_id = None)
    else:
        service_default = (
            session.query(db.DF_Parameter.idf_type, db.DF_Parameter.min, db.DF_Parameter.max)
            .filter(db.DF_Parameter.mf_id == None, db.DF_Parameter.df_id == df_id,
                    db.DF_Parameter.u_id == None)
            .order_by(db.DF_Parameter.param_i)
            .all()
        )
        for i in service_default:
            return_info['df_info'].append(i)

        return_info = json.dumps(return_info)
        print('\nservice_default:\n', return_info)
        return return_info

# modify
@app.route('/get_stage1_info', methods=['POST'])
def get_stage1_info():
    '''
    input value:
        stage1_info = json.loads(request.form['stage1_info'])
        {
            'id_list': [],
            'p_id': p_id,
        }
    return value:
        return_info = {
            'na_id': na_id,
            'join_function': [["larger than", 16, 1], ...],
            'all_idf_mapping_function': [["average", 10, 1], ...],
            'all_idfo_id': [1, 2, 3, ...],
            'odfo_id': 1,
            'odf_mapping_function': [],
            'all_idf_info':[['variant', ...], ...]
            'all_idf_name': ['lightness', ...],
            'all_idf_alias_name': [string, ...],
            'odf_name': 'vibration',
            'odf_alias_name': string,
            'all_idf_fn_id': [11, ...],
            'all_idf_module_title': [],
            'odf_module_title': '',
            'join_fn_id': 0,
            'join_index': []
        }
    '''
    u_id = 1
    session = g.session
    stage1_info = json.loads(request.form['stage1_info'])
    id_list = stage1_info['id_list']
    p_id = stage1_info['p_id']

    print("\nGet_Stage1_Info Input:\n", id_list)

    na_id = int(id_list['na_id'])
    odfo_id = int(id_list['odfo_id'])

    return_info = {
        'na_id': na_id,
        'join_function': [],
        'all_idfo_id': [],
        'odfo_id': None,
        'all_idf_info': [],
        'odf_info': [],
        'all_idf_name': [],
        'all_idf_alias_name': [],
        'odf_name': '',
        'odf_alias_name': '',
        'all_idf_module_title': [],
        'odf_module_title': '',
        'join_fn_id': None,
        'join_index': []
    }

    # get all idf module info
    all_idf_module_info = get_all_idf_module_info(na_id)#TODO
    return_info['all_idf_name'] = all_idf_module_info['idf_name']
    return_info['all_idf_alias_name'] = all_idf_module_info['alias_name']
    return_info['all_idfo_id'] = all_idf_module_info['idfo_id']
    return_info['all_idf_module_title'] = all_idf_module_info['idf_module_title']
    return_info['all_idf_info'] = all_idf_module_info['idf_info']

    number_of_idf = len(all_idf_module_info['idfo_id'])
    # turn other NetworkApplications black
    for i in (
        session.query(db.DF_Module)
        .join(db.NetworkApplication)
        .filter(db.NetworkApplication.p_id == p_id)
        .all()
    ):
        i.color = 'black'
        session.commit()

    # get all idf mapping function list
    for id in return_info['all_idfo_id']:
        temp_df_id = (
            session.query(db.DFObject.df_id)
            .filter(db.DFObject.dfo_id == id)
            .first()
        )
        if temp_df_id: temp_df_id = temp_df_id[0]
        else: continue
        # turn IDF lines red
        for i in (
            session.query(db.DF_Module)
            .join(db.NetworkApplication)
            .filter(db.NetworkApplication.p_id == p_id, db.DF_Module.na_id == na_id,
                    db.DF_Module.dfo_id == id)
            .all()
        ):
            i.color = 'red'
            session.commit()

    # get join module info
    if number_of_idf > 1:
        # get join info
        idf_join_list = get_sorted_idf_id_list(na_id)
        join_info = (
            session.query(db.MultipleJoin_Module.dfo_id,
                          db.MultipleJoin_Module.param_i)
            .select_from(db.MultipleJoin_Module)
            .join((db.DFObject,
                   db.DFObject.dfo_id == db.MultipleJoin_Module.dfo_id),
                  (db.DeviceObject,
                   db.DeviceObject.do_id == db.DFObject.do_id))
            .join(db.DeviceFeature)
            .filter(db.MultipleJoin_Module.na_id == na_id)
            .order_by(db.DeviceObject.do_idx, db.DeviceFeature.df_name)
            .all()
        )
        # had been set
        join_index = []
        if len(join_info) > 0:
            for i in join_info:
                join_index.append(i[2]+1)
            if join_info[0][1] == None:
                return_info['join_fn_id'] = -1
            else:
                return_info['join_fn_id'] = join_info[0][1]
            return_info['join_index'] = join_index
        else:
            for i in range(number_of_idf):
                join_index.append(i+1)
            return_info['join_fn_id'] = -1
            return_info['join_index'] = join_index

    if odfo_id != 0:
        None
    else:
        only_one_odf = (
            session.query(db.DF_Module.dfo_id)
            .join(db.DFObject, db.DeviceFeature)
            .filter(db.DF_Module.na_id == na_id, db.DeviceFeature.df_type == 'output')
            .group_by(db.DF_Module.dfo_id)
            .all()
        )
        if len(only_one_odf) == 1:
            odfo_id = int(only_one_odf[0][0])
        else:
            odfo_id = 0

    if odfo_id != 0:
        # turn the ODF line red
        for i in (
            session.query(db.DF_Module)
            .join(db.NetworkApplication)
            .filter(db.NetworkApplication.p_id == p_id, db.DF_Module.na_id == na_id,
                    db.DF_Module.dfo_id == odfo_id)
            .all()
        ):
            i.color = 'red'
            session.commit()

        # get relevant mf_id from df_id & dm_id for odfo_id
        (dm_id, df_id, d_id) = (
            session.query(db.DeviceObject.dm_id, db.DFObject.df_id,
                          db.DeviceObject.d_id)
            .join(db.DFObject)
            .filter(db.DFObject.dfo_id == odfo_id)
            .first()
        )
        mf_id = (
            session.query(db.DM_DF.mf_id)
            .filter(db.DM_DF.dm_id == dm_id, db.DM_DF.df_id == df_id)
            .first()
        )
        if mf_id: mf_id = mf_id[0]
        # get odf module info
        odf_module_info = get_df_module_info(na_id, odfo_id, mf_id)
        return_info['odf_name'] = odf_module_info[0]
        return_info['odf_alias_name'] = odf_module_info[1]
        return_info['odf_module_title'] = get_df_module_title(dm_id, d_id)
        for i in range(2, len(odf_module_info)):
            return_info['odf_info'].append(
                odf_module_info[i]['fn_id'],
            )

    return_info['odfo_id'] = odfo_id
    return_info = json.dumps(return_info)
    print(return_info)
    return return_info

# modify
@app.route('/save_circle_connect_setting', methods=['POST'])
def save_circle_connect_setting():
    '''
    input value:
        circle_connect_info = json.loads(request.form['circle_connect_info'])
        {
            'connect_info': [join_idx, na_id, feature_id],
            'p_id': p_id,
        }
    return value:
        'ok'
    '''
    session = g.session
    circle_connect_info = json.loads(request.form['circle_connect_info'])
    connect_info = circle_connect_info['connect_info']
    p_id = circle_connect_info['p_id']
    print('\nsave_circle_connect_setting:', circle_connect_info)
    na_id = int(connect_info[1])

    connected_line = (
        session.query(db.DF_Module)
        .filter(db.DF_Module.na_id == na_id,
                db.DF_Module.dfo_id == connect_info[2])
        .first()
    )
    odf_fn_is_set = 0
    disabled_name = 'disabled';
    #disabled_fn_id = (
    #    session.query(db.Function.fn_id)
    #    .filter(db.Function.fn_name == disabled_name)
    #    .first()[0]
    #)
    disabled_fn_id = -1

    (dm_id, df_id, d_id) = (
        session.query(db.DeviceObject.dm_id, db.DFObject.df_id, db.DeviceObject.d_id)
        .join(db.DFObject)
        .filter(db.DFObject.dfo_id == connect_info[2])
        .first()
    )
    mf_id = (
        session.query(db.DM_DF.mf_id)
        .filter(db.DM_DF.dm_id == dm_id, db.DM_DF.df_id == df_id)
        .first()
    )
    if mf_id: mf_id = mf_id[0]
    # idf/odf_info idf/odf_title
    for df_type, in (
        session.query(db.DeviceFeature.df_type)
        .select_from(db.DeviceFeature)
        .join(db.DFObject)
        .filter(db.DFObject.dfo_id == connect_info[2])
    ):
        if df_type == 'input' :
            idf = get_df_module_info(na_id, connect_info[2], mf_id)
            idfo_id = int(connect_info[2])
            for j in range(2, len(idf)):
                info = idf[j]
                connect_data = db.DF_Module(na_id=na_id, fn_id = info['fn_id'], idf_type=info['idf_type'],
                    normalization=1, param_i=info['param_i'], dfo_id=idfo_id, color='red',
                    min=info['min'], max=info['max'])
                session.add(connect_data)
                session.commit()
            refresh_join_module(na_id)
            # reset join dynamic range
            csmapi.dfm_reset(na_id, 0)
            # reset all odf dynamic range
            all_odfo_id = [ dfo_id for (dfo_id, ) in (
                session.query(db.DF_Module.dfo_id)
                .select_from(db.DF_Module)
                .join(db.DFObject, db.DeviceFeature)
                .filter(db.DeviceFeature.df_type == 'output',
                        db.DF_Module.na_id == na_id)
                .group_by(db.DF_Module.dfo_id)).all()]
            for odfo_id in all_odfo_id:
                csmapi.dfm_reset(na_id, odfo_id)
        else:
            odf = get_df_module_info(na_id, connect_info[2], mf_id)
            odfo_id = int(connect_info[2])
            for j in range(2, len(odf)):
                info = odf[j]
                if info['fn_id'] != None: #disabled_fn_id:
                    odf_fn_is_set = 1

                connect_data = db.DF_Module(na_id=na_id, fn_id=info['fn_id'], idf_type=info['idf_type'],
                    normalization=info['normalization'], param_i=info['param_i'], dfo_id=odfo_id, color='red',
                    min=info['min'], max=info['max'])
                session.add(connect_data)
                session.commit()
#    if odf_fn_is_set == 1:
#    # turn off idf function
#        idfo_id_list = (
#            session.query(db.DF_Module.dfo_id)
#            .select_from(db.DF_Module)
#            .join(db.DFObject, db.DeviceFeature)
#            .filter(db.DeviceFeature.df_type == 'input', db.DF_Module.na_id == na_id)
#            .group_by(db.DF_Module.dfo_id)
#            .all()
#        )
#        print(idfo_id_list)
#        for idfo_id in idfo_id_list:
#            for idf in (
#                session.query(db.DF_Module)
#                .filter(db.DF_Module.na_id == na_id, db.DF_Module.dfo_id == idfo_id[0])
#                .all()
#            ):
#                idf.fn_id = None #disabled_fn_id
#                session.commit()
    # turn other NetworkApplications black
    for i in (
        session.query(db.DF_Module)
        .join(db.NetworkApplication)
        .filter(db.NetworkApplication.p_id == p_id, db.DF_Module.na_id != na_id)
        .all()
    ):
        i.color = 'black'
        session.commit()

    return 'ok'

# modify
@app.route('/delete_device_object', methods=['POST'])
def delete_device_object():
    '''
    input value:
        recycle_info = {
            'do_id': do_id,
            'p_id': p_id,
        }
    output value:
        'ok'
    '''

    session = g.session
    recycle_info = json.loads(request.form['recycle_info'])
    do_id = recycle_info['do_id']
    p_id = recycle_info['p_id']

    ## lock project
    #current_prj_status = (
    #    session.query(db.Project.status)
    #    .filter(db.Project.p_id == p_id)
    #    .first()[0]
    #)
    #close_project(p_id)
    remove_device_model_icon(do_id, p_id)

    for na_id, in (
        session.query(db.NetworkApplication.na_id)
        .filter(db.NetworkApplication.p_id == p_id)
    ):
        adjust_half_line(na_id)
    #if current_prj_status == 'on':
    #    open_project(p_id)
    reopen_project(p_id)
    
    
    global selected_models_in_prj_need_to_update
    selected_models_in_prj_need_to_update[p_id] = True

    return 'ok'


@app.route('/save_feature_default', methods=['POST'])
def save_feature_default():
    '''
    input value:
       setting_list = {
           'df_info': [[type, min, max, fn_id], ...],
           'dfo_id': id,
           'alias_name' : string,
       }
    return value:
        'ok'
    '''
    u_id = 1
    session = g.session

    data = request.form['setting_list']
    setting_list = json.loads(data)

    print("\nsave_feature_default:\n", setting_list)

    (dm_id, df_id) = (
        session.query(db.DeviceObject.dm_id, db.DFObject.df_id)
        .join(db.DFObject)
        .filter(db.DFObject.dfo_id == setting_list['dfo_id'])
        .first()
    )

    mf_id = (
        session.query(db.DM_DF.mf_id)
        .filter(db.DM_DF.dm_id == dm_id, db.DM_DF.df_id == df_id)
        .first()
    )
    if mf_id: mf_id = mf_id[0]
    for i in range(len(setting_list['df_info'])):
        (
            session.query(db.DF_Parameter)
            .filter(db.DF_Parameter.mf_id == mf_id, db.DF_Parameter.param_i == i)
            .update({'idf_type' : setting_list['df_info'][i][0],
                     'min' : setting_list['df_info'][i][1],
                     'max' : setting_list['df_info'][i][2],
                     'normalization' : 1 if setting_list['df_info'][i][1] != setting_list['df_info'][i][2] else 0}
            )
        )
        session.commit()

    (
        session.query(db.DFObject)
               .filter(db.DFObject.dfo_id == setting_list['dfo_id'])
               .update({'alias_name' : setting_list['alias_name']})
    )
    session.commit()
    return 'ok'

@app.route('/update_dfo_alias_name', methods=['POST'])
@crossdomain(origin='*')
def update_dfo_alias_name():
    '''input value:
        update_info = {
           'dfo_id' : dfo_id, 
           'alias_name' : alias_name
        }
    '''
    u_id = 1
    session = g.session
    data = request.form['update_info']
    update_info = json.loads(data)

    (
        session.query(db.DFObject)
               .filter(db.DFObject.dfo_id == update_info["dfo_id"])
               .update({'alias_name' : update_info["alias_name"]})
    )
    session.commit()
    return 'ok'

# modify
@app.route('/save_connection_configuration', methods=['POST'])
def save_connection_configuration():
    '''
    input value:
       function_setting = json.loads(request.form['function_setting'])
       {
           'setting_list' = {
               'join_name': '',
               'na_id': na_id,
               'all_idf_info': [['variant'], ...],
               'all_idfo_id': [idfo_id, ...],
               'odfo_id': odfo_id,
               'odf_info': [fn_id, ...]
               'all_idf_fn_id': [fn_id, ...],
               'join_fn_id': fn_id,
               'join_index': [],
           },
           'p_id': p_id,
       }

    return value:
        'ok'
    '''
    session = g.session

    function_setting = json.loads(request.form['function_setting'])
    setting_list = function_setting['setting_list']
    p_id = function_setting['p_id']
    print("\nsave_connection_configuration:\n", function_setting)
    na_id = setting_list['na_id']
    all_idf_info = setting_list['all_idf_info']
    all_idfo_id = setting_list['all_idfo_id']
    all_idf_fn_id = setting_list['all_idf_fn_id']

    # insert join info into MultipleJoin_Module
    if len(all_idfo_id) > 1:
        join_fn_id = int(setting_list['join_fn_id'])
        if join_fn_id == -1:
            join_fn_id = None
        join_index = setting_list['join_index']
        id_list = get_sorted_idf_id_list(na_id)
        join_dfo_id_records = [dfo_id for (dfo_id, ) in
            (session.query(db.MultipleJoin_Module.dfo_id)
            .join((db.DFObject,
                   db.DFObject.dfo_id == db.MultipleJoin_Module.dfo_id),
                  (db.DeviceObject,
                   db.DeviceObject.do_id == db.DFObject.do_id))
            .join(db.DeviceFeature)
            .filter(db.MultipleJoin_Module.na_id == na_id)
            .order_by(db.DeviceObject.do_idx, db.DeviceFeature.df_name)
            .all()
        )]
        # clear old join info
        session.query(db.MultipleJoin_Module).filter(db.MultipleJoin_Module.na_id == na_id).delete()
        session.commit()

        for i in range(len(join_index)):
            join_data = db.MultipleJoin_Module(
                na_id = na_id, param_i = int(join_index[i])-1,
                fn_id = join_fn_id, dfo_id = join_dfo_id_records[i]
            )
            session.add(join_data)
            session.commit()

    # rename the NetworkApplication
    for c in (
        session.query(db.NetworkApplication)
        .filter(db.NetworkApplication.na_id == na_id)
    ):
        c.na_name = setting_list['join_name']
        session.commit()

    idf_normalization = []
    idf_min = []
    idf_max = []

    # delete old idf module setting
    for idf in range(len(all_idfo_id)):
        idfo_id = all_idfo_id[idf]
        # retrieve normalization from old idf module
        for norm_, min_, max_ in (
             session.query(db.DF_Module.normalization,
                            db.DF_Module.min, db.DF_Module.max)
             .filter(db.DF_Module.dfo_id == idfo_id, db.DF_Module.na_id == na_id)
             .order_by(db.DF_Module.param_i)
             .all()
         ):
             idf_normalization.append(norm_)
             idf_min.append(min_)
             idf_max.append(max_)

        (
            session.query(db.DF_Module)
            .filter(db.DF_Module.dfo_id == idfo_id, db.DF_Module.na_id == na_id)
            .delete()
        )
        session.commit()


    # get disabled fn_id
    #disabled_fn_id = (
    #    session.query(db.Function.fn_id)
    #    .filter(db.Function.fn_name == 'disabled')
    #    .first()[0]
    #)
    disabled_fn_id = -1

    if 'odfo_id' in setting_list.keys():
        odf_info = setting_list['odf_info']
        odfo_id = int(setting_list['odfo_id'])
        # retrieve normalization from old odf module
        odf_normalization = []
        odf_min = []
        odf_max = []
        for norm_, min_, max_ in (
            session.query(db.DF_Module.normalization,
                           db.DF_Module.min, db.DF_Module.max)
            .filter(db.DF_Module.dfo_id == odfo_id, db.DF_Module.na_id == na_id)
            .order_by(db.DF_Module.param_i)
            .all()
        ):
            odf_normalization.append(norm_)
            odf_min.append(min_)
            odf_max.append(max_)

        # delete old odf module setting
        (
            session.query(db.DF_Module)
            .filter(db.DF_Module.dfo_id == odfo_id, db.DF_Module.na_id == na_id)
            .delete()
        )
        session.commit()

        # insert new odf module setting
        for i in range(0, len(odf_info)):
            odf_fn_id = odf_info[i] if odf_info[i] != '-1' else None
            session.add(db.DF_Module(na_id = na_id, fn_id = odf_fn_id, idf_type = 'sample',
                    dfo_id = odfo_id, normalization = odf_normalization[i], param_i = i, color = 'red',
                    min = odf_min[i], max = odf_max[i]))
            session.commit()
        # reset dynamic range
        #csmapi.dfm_reset(na_id, odfo_id)

    # insert new idf module setting

    if len(all_idfo_id) > 1:
        norm_enable = 1
    else:
        norm_enable = 0

    for idf in range(len(all_idfo_id)):
        idf_type = all_idf_info[idf]
        idf_fn_id = all_idf_fn_id[idf] if all_idf_fn_id[idf] != '-1' else None
        idfo_id = all_idfo_id[idf]

        for i in range(0, len(idf_type)):
            #idf_module = db.DF_Module(na_id = na_id, fn_id = idf_fn_id, idf_type = idf_type[i],
            #    dfo_id = idfo_id, normalization = norm_enable, param_i = i, color = 'red')
            idf_module = db.DF_Module(na_id = na_id, fn_id = idf_fn_id, idf_type = idf_type[i],
                dfo_id = idfo_id, normalization = idf_normalization[i], param_i = i, color = 'red',
                min = idf_min[i], max = idf_max[i])
            session.add(idf_module)
            session.commit()
        # reset dynamic range
        csmapi.dfm_reset(na_id, idfo_id)

    # turn other NetworkApplications black
    for i in (
        session.query(db.DF_Module)
        .join(db.NetworkApplication)
        .filter(db.NetworkApplication.p_id == p_id, db.DF_Module.na_id != na_id)
        .all()
    ):
        i.color = 'black'
        session.commit()
    return 'ok'

@app.route('/delete_connection_line', methods=['POST'])
def delete_connection_line():
    '''
    input value:
        na_id = na_id
    output value:
        'ok'
    '''
    session = g.session
    na_id = int(request.form['na_id'])

    print("\ndelete_connection_line:\n", na_id)
    all_dfo_id = (
        session.query(db.DF_Module.dfo_id)
        .filter(db.DF_Module.na_id == na_id)
        .group_by(db.DF_Module.dfo_id)
        .all()
    )
    all_dfo_id = (
        session.query(db.DF_Module.dfo_id)
        .filter(db.DF_Module.na_id == na_id)
        .all()
    )
    session.query(db.MultipleJoin_Module).filter(db.MultipleJoin_Module.na_id == na_id).delete()
    session.commit()
    session.query(db.DF_Module).filter(db.DF_Module.na_id == na_id).delete()
    session.commit()
    session.query(db.NetworkApplication).filter(db.NetworkApplication.na_id == na_id).delete()
    session.commit()

    return 'ok'


@app.route('/delete_connection_line_segment', methods=['POST'])
def delete_connection_line_segment():
    '''
    input value:
        connection_pair = json.loads(request.form['id_list'])
        - wa_id_list = {
               'na_id': 1,
               'kill_dfo_id': 2,
               'odfo_id': 3,
           }
    return value:
        return_info = {
            'remove_circle': None,
            'na_id': None,
            'odfo_id': 2, # 0 means no ODF selected
        }
    '''

    session = g.session
    data = request.form['wa_id_list']
    id_list = json.loads(data)

    print("\ndelete_connection_line_segment:\n", id_list)

    na_id = id_list['na_id']
    kill_dfo_id = id_list['kill_dfo_id']
    odfo_id = id_list['odfo_id']

    return_info = {
        'remove_circle': None,
        'na_id': None,
        'odfo_id': None,
    }

    return_info['na_id'] = na_id

    if kill_dfo_id == odfo_id:
        # if there is only one ODF left after killing operation, show it automatically
        only_one_odf = (
            session.query(db.DF_Module.dfo_id)
            .join(db.DFObject, db.DeviceFeature)
            .filter(db.DF_Module.na_id == na_id, db.DeviceFeature.df_type == 'output',
                    db.DF_Module.dfo_id != odfo_id)
            .group_by(db.DF_Module.dfo_id)
            .all()
        )
        if len(only_one_odf) == 1:
            return_info['odfo_id'] = only_one_odf[0][0]
            for line in (
                session.query(db.DF_Module)
                .filter(db.DF_Module.na_id == na_id,
                        db.DF_Module.dfo_id == only_one_odf[0][0])
            ):
                line.color = 'red'
                session.commit()
        else:
            return_info['odfo_id'] = 0
    else:
        return_info['odfo_id'] = odfo_id

    for count, in (
        session.query(func.count(db.DF_Module.na_id))
        .select_from(db.DF_Module)
        .filter(db.DF_Module.dfo_id == kill_dfo_id, db.DF_Module.na_id == na_id)
    ):
        if count > 0: # duplicate connection, disable/delete this connection
            (
                session.query(db.DF_Module)
                .filter(db.DF_Module.dfo_id == kill_dfo_id, db.DF_Module.na_id == na_id)
                .delete()
            )
            session.commit()
            refresh_join_module(na_id)

    if adjust_half_line(na_id) == 1:
        return_info['remove_circle'] = 1
        return_info['odfo_id'] = 0
    else:
        csmapi.dfm_reset(na_id, kill_dfo_id)

    return_info = json.dumps(return_info)
    print('return_info',return_info)
    return return_info


@app.route('/check_dfo_is_connected', methods=['POST'])
def check_dfo_is_connected():
    '''
    input value:
        check_info = json.loads(request.form['check_info'])
        {
            'dfo_id': dfo_id,
            'p_id': p_id,
        }
    return value:
        - '0' no red lines
        - 'na_id' the circle with red lines and connected with the odf
    '''
    session = g.session
    check_info = json.loads(request.form['check_info'])
    dfo_id = check_info['dfo_id']
    p_id = check_info['p_id']
    print('\ncheck_dfo_is_connected:\n', check_info)
    connected_na_id = (
        session.query(db.DF_Module.na_id)
        .join(db.NetworkApplication)
        .filter(db.NetworkApplication.p_id == p_id, db.DF_Module.dfo_id == dfo_id)
        .group_by(db.DF_Module.na_id)
        .all()
    )

    if len(connected_na_id) == 0:
        return '0'
    else:
        for na_id in connected_na_id:
            red_idf = (
                session.query(func.count(db.DF_Module.dfo_id))
                .join(db.DFObject, db.DeviceFeature)
                .filter(db.DF_Module.na_id == na_id[0], db.DF_Module.color == 'red',
                        db.DeviceFeature.df_type == 'input')
                .first()
            )
            if red_idf: red_idf = red_idf[0]
            if red_idf > 0:
                return str(na_id[0])
        return '0'

@app.route('/check_duplicate_circle_connection', methods=['POST'])
def check_duplicate_circle_connection():
    '''
    input value:
        check_info = json.loads(request.form['check_info'])
        {
            'id_list': [na_id, dfo_id],
            'p_id': p_id,
        }
    return value:
        duplicate_info = {
            'is_duplicate': '0',
            'remove_circle': None,
            'na_id': 3,
            'color': 'red'/'black',
        }
        - '0'
        - '1' duplicate connection

    '''
    session = g.session
    check_info = json.loads(request.form['check_info'])
    connection_pair = check_info['id_list']
    p_id = check_info['p_id']
    na_id = connection_pair[0]
    print("\ncheck_duplicate_circle_connection:\n", check_info)
    duplicate_info = {
        'is_duplicate': '',
        'remove_circle': None,
        'na_id': '',
        'color': None,
    }

    for count, in (
        session.query(func.count(db.DF_Module.na_id))
        .select_from(db.DF_Module)
        .filter(db.DF_Module.dfo_id == int(connection_pair[1]), db.DF_Module.na_id == na_id)
    ):
        if count > 0: # duplicate connection, disable/delete this connection
            duplicate_info['is_duplicate'] = '1'
            duplicate_info['color'] = 'red'
        else:
            duplicate_info['is_duplicate'] = '0'
            duplicate_info['color'] = 'red'

    # turn other connections black
    for i in (
        session.query(db.DF_Module)
        .join(db.NetworkApplication)
        .filter(db.NetworkApplication.p_id == p_id, db.DF_Module.na_id != na_id)
        .all()
    ):
        i.color = 'black'
        session.commit()
    duplicate_info = json.dumps(duplicate_info)
    print('return_info', duplicate_info)
    return duplicate_info


@app.route('/check_duplicate_connection', methods=['POST'])
def check_duplicate_connection():
    '''
    input value:
        connection_pair = json.loads(request.form['feature_id_list'])
        - connection_pair = [idfo_id, odfo_id]
    return value:
        duplicate_info = {
            'is_duplicate': '0',
            'na_id': 3
        }
        - '0'
        - '1' duplicate connection
    '''

    session = g.session
    data = request.form['feature_id_list']
    connection_pair = json.loads(data)
    duplicate_info = {
        'is_duplicate': '',
        'remove_circle': None,
        'na_id': ''
    }
    stmt = (
        session.query(db.DF_Module.na_id)
        .select_from(db.DF_Module)
        .filter(db.DF_Module.dfo_id == int(connection_pair[0]))
        .subquery()
    )

    # only enter this loop once even more than 1 na_id
    for count, na_id in (
        session.query(func.count(db.DF_Module.na_id), db.DF_Module.na_id)
        .select_from(db.DF_Module)
        .filter(db.DF_Module.dfo_id == connection_pair[1], db.DF_Module.na_id.in_(stmt))
    ):
        if count > 0: # duplicate connection, disable/delete this connection
            duplicate_info['is_duplicate'] = '1'
        else:
            duplicate_info['is_duplicate'] = '0'
    duplicate_info = json.dumps(duplicate_info)
    return duplicate_info


@app.route('/get_all_connect_list', methods=['POST'])
def get_all_connect_list():
    '''
    input value:
        na_id = request.form['na_id']
    return value:
        connect_list = {
            'idf_list':[],
            'odf_list':[]
        }
    '''

    session = g.session
    na_id = int(request.form['na_id'])

    print("\nget_all_connect_list:\n", na_id)
    connect_list = {
        'idf_list': [],
        'odf_list': []
    }

    ##########################
    in_or_out = ['input', 'output']

    idfo_id_list = (
        session.query(db.DF_Module.dfo_id)
        .join(db.DFObject, db.DeviceFeature)
        .filter(db.DF_Module.na_id == 1, db.DeviceFeature.df_type == 'input')
        .group_by(db.DF_Module.dfo_id)
        .all()
    )

    odfo_id_list = (
        session.query(db.DF_Module.dfo_id)
        .join(db.DFObject, db.DeviceFeature)
        .filter(db.DF_Module.na_id == 1, db.DeviceFeature.df_type == 'output')
        .group_by(db.DF_Module.dfo_id)
        .all()
    )

    for i in in_or_out:
        corr_list = []
        relevant_line = (
            session.query(db.DeviceObject.dm_id, db.DeviceModel.dm_name, db.DeviceObject.d_id,
                          db.DeviceFeature.df_name, db.DF_Module.dfo_id)
            .select_from(db.DF_Module)
            .join(db.DFObject, db.DeviceFeature, db.DeviceObject, db.DeviceModel)
            .filter(db.DF_Module.na_id == na_id,db.DeviceFeature.df_type == i)
            .group_by(db.DF_Module.dfo_id)
            .all()
        )
        for dm_id, dm_name, d_id, df_name, dfo_id in relevant_line:
            if d_id == None:
                corr_list.append([dm_name, df_name, dfo_id])
            else:
                d_name = (
                    session.query(db.Device.d_name)
                    .filter(db.Device.d_id == d_id)
                    .first()
                )
                if d_name != None:
                    corr_list.append([d_name[0], df_name, dfo_id])
                else:
                    print("This device has no name.")

        if i == 'input':
            connect_list['idf_list'] = corr_list
        else:
            connect_list['odf_list'] = corr_list
    print(connect_list)

    connect_list = json.dumps(connect_list)
    return connect_list


@app.route('/restart_project', methods=['POST'])
def restart_project():
    '''
    input value:
        p_id = request.form['p_id']
    return value:
        'ok'
    '''

    session = g.session
    p_id = request.form['p_id']
    restart = (
        session.query(db.Project)
        .filter(db.Project.p_id == p_id)
        .first()
    )
    restart.restart = 1
    restart.exception = ''
    session.commit()

    return 'ok'


@app.route('/turn_on_project', methods=['POST'])
def turn_on_project():
    '''
    input value:
        p_id = request.form['p_id']
    return value:
        'Stop'/'Exec'
    '''

    session = g.session
    p_id = request.form['p_id']
    project = (
        session.query(db.Project)
        .filter(db.Project.p_id == p_id)
        .first()
    )
    project.status = 'on'

    ControlChannel.RESUME(db, p_id)

    session.commit()
    return ''


@app.route('/turn_off_project', methods=['POST'])
def turn_off_project():
    '''
    input value:
        p_id = request.form['p_id']
    return value:
        'Stop'/'Exec'
    '''

    session = g.session
    p_id = request.form['p_id']
    project = (
        session.query(db.Project)
        .filter(db.Project.p_id == p_id)
        .first()
    )
    project.status = 'off'

    ControlChannel.SUSPEND(db, p_id)

    session.commit()
    return ''

@app.route('/turn_on_simulation', methods=['POST'])
def turn_on_simulation():
    '''
    input value:
        p_id = request.form['p_id']
    return value:
        'Stop'/'Exec'
    '''

    session = g.session
    p_id = request.form['p_id']
    project = (
        session.query(db.Project)
        .filter(db.Project.p_id == p_id)
        .first()
    )
    project.sim = 'on'

    session.commit()
    print ('Turn_on_Sim')
    return ''

@app.route('/turn_off_simulation', methods=['POST'])
def turn_off_simulation():
    '''
    input value:
        p_id = request.form['p_id']
    return value:
        'Stop'/'Exec'
    '''

    session = g.session
    p_id = request.form['p_id']
    project = (
        session.query(db.Project)
        .filter(db.Project.p_id == p_id)
        .first()
    )
    project.sim = 'off'

    session.commit()
    print ('Turn_off_Sim')
    return ''


@app.route('/convert_project_status', methods=['POST'])
def convert_project_status():
    '''
    input value:
        p_id = request.form['p_id']
    return value:
        'Stop'/'Exec'
    '''

    session = g.session
    p_id = request.form['p_id']
    new_status = None
    status = get_prj_status(p_id)
    if status == 'on':
        close_project(p_id)
    else:
        exception_msg = (
            session.query(db.Project)
            .filter(db.Project.p_id == p_id)
            .first()
        )
        exception_msg.exception = ''
        session.commit()
        open_project(p_id)
        new_status = 'off'

    if new_status == 'off':
        return 'Stop'
    else:
        return 'Exec'


@app.route('/get_project_status', methods=['POST'])
def get_project_status():
    '''
    input value:
        p_id = request.form['p_id']
    return value:
        'Stop'/'Exec'
    '''
    p_id = request.form['p_id']
    print('\nget_project_status:\n', p_id)
    status = get_prj_status(p_id)
    if status == 'off':
        return 'Exec'
    else:
        return 'Stop'

@app.route('/get_sim_status', methods=['POST'])
def get_sim_status():
    '''
    input value:
        p_id = request.form['p_id']
    return value:
        'Stop'/'Exec'
    '''
    p_id = request.form['p_id']
    print('\nget_sim_status:\n', p_id)
    status = get_simulation_status(p_id)
    if status == 'off':
        return 'Exec'
    else:
        return 'Stop'

@app.route('/get_device_feature_object_id', methods=['POST'])
@crossdomain(origin='*')
def get_device_feature_object_id():
    '''
    input value:
        mac_addr = request.form['mac_addr']
    return value:
        {
            success: True,
            data:
                {
                    dfo_id:
                        {
                            name:'name',
                            alias:'alias'
                        }
                }
        }
    '''
    session = g.session
    mac_addr = request.form['mac_addr']
    d = (
        session.query(db.Device)
        .filter(db.Device.mac_addr == mac_addr)
        .first()
    )
    if d == None:
        return json.dumps({"success": False, "data": "mac address not found"})
    d_id = d.d_id
    do = (
        session.query(db.DeviceObject)
        .filter(db.DeviceObject.d_id == d_id)
        .first()
    )
    if do == None:
        return json.dumps({"success": False, "data": "device is not mounted"})
    do_id = do.do_id

    dfo = {}
    for device_feature_object in (
        session.query(db.DFObject)
        .filter(db.DFObject.do_id == do_id)
        .all()
    ):
        name = session.query(db.DeviceFeature).filter(db.DeviceFeature.df_id == 
            device_feature_object.df_id).first().df_name
        dfo[device_feature_object.dfo_id] = name + ":" + device_feature_object.alias_name

    res = {"success": True, "data": dfo}
    session.commit()
    return json.dumps(res)

# modify
@app.route('/save_connection_line', methods=['POST'])
def save_connection_line():
    '''
    input value:
        setting_info = json.loads(request.form['setting_info'])
        {
            'connect_info': [join_name, join_idx, feature_id, feature_id],
            'p_id': p_id,
        }
    return value:
        return_info = {
            'na_id':None,
            'idfo_id':None,
            'odfo_id':None,
        }
    '''
    session = g.session
    setting_info = json.loads(request.form['setting_info'])
    connect_info = setting_info['connect_info']
    p_id = setting_info['p_id']
    print("\nsave_connection_line:\n", setting_info)

    build_connect = db.NetworkApplication(na_name=connect_info[0], p_id=p_id, na_idx = connect_info[1])
    session.add(build_connect)
    session.commit()
    na_id = build_connect.na_id
    return_info = {
        'na_id':na_id,
        'idfo_id':None,
        'odfo_id':None,
    }
    # idf/odf_info idf/odf_title
    odf_fn_is_set = 0
    disabled_name = 'disabled';
    #disabled_fn_id = (
    #    session.query(db.Function.fn_id)
    #    .filter(db.Function.fn_name == disabled_name)
    #    .first()[0]
    #)  
    disabled_fn_id = -1

    #let idf previous than odf
    first_df_type = (
        session.query(db.DeviceFeature.df_type)
        .select_from(db.DeviceFeature).join(db.DFObject)
        .filter(db.DFObject.dfo_id == connect_info[2])
        .first()
    )
    if first_df_type: first_df_type = first_df_type[0]
    if first_df_type == 'output':
        connect_info[2], connect_info[3] = connect_info[3], connect_info[2]
    idf = []
    for i in range(2,len(connect_info)):
        (dm_id, df_id, d_id) = (
            session.query(db.DeviceObject.dm_id, db.DFObject.df_id,
                          db.DeviceObject.d_id).join(db.DFObject)
            .filter(db.DFObject.dfo_id == connect_info[i])
            .first()
        )
        mf_id = (
            session.query(db.DM_DF.mf_id)
            .filter(db.DM_DF.dm_id == dm_id, db.DM_DF.df_id == df_id)
            .first()
        )

        if mf_id: mf_id = mf_id[0]
        else:  mf_id = None

        for df_type, in (
            session.query(db.DeviceFeature.df_type)
            .select_from(db.DeviceFeature).join(db.DFObject)
            .filter(db.DFObject.dfo_id == connect_info[i])
        ):
            if df_type == 'input' :
                return_info['idfo_id'] = connect_info[i]
                idf = get_df_module_info(na_id, return_info['idfo_id'], mf_id)
                for j in range(2, len(idf)):
                    info = idf[j]
                    print('*\n*\n', info['idf_type'])
                    connect_data = db.DF_Module(na_id=na_id, idf_type=info['idf_type'],
                        normalization=0,param_i=info['param_i'], dfo_id=return_info['idfo_id'], color='red',
                        min=info['min'], max=info['max'])
                    session.add(connect_data)
                    session.commit()
            else:
                return_info['odfo_id'] = connect_info[i]
                odf = get_df_module_info(na_id, return_info['odfo_id'], mf_id)
                for j in range(2, len(odf)):
                    info = odf[j]
                    print('(\n(', info['idf_type'])
                    connect_data = db.DF_Module(na_id=na_id, idf_type=info['idf_type'],
                        normalization=info['normalization'], param_i=info['param_i'],
                        dfo_id=return_info['odfo_id'], color='red', min=info['min'], max=info['max'])
                    session.add(connect_data)
                    session.commit()

    # turn other connections black
    for i in (
        session.query(db.DF_Module)
        .join(db.NetworkApplication)
        .filter(db.NetworkApplication.p_id == p_id, db.DF_Module.na_id != na_id)
        .all()
    ):
        i.color = 'black'
        session.commit()

    return_info = json.dumps(return_info)
    print(return_info)
    return return_info

@app.route('/set_df_status', methods=['POST'])
def set_df_status():
    '''
    input value:
        info = json.loads(request.form['device_save_info'])
        - info[0] = do_id
        - info[1] = d_id
    return value:
        return_status_code = 200
    '''
    session = g.session
    data = request.form['device_save_info']
    info = json.loads(data) # info[0] = do_id, info[1] = d_id
    return ControlChannel.SET_DF_STATUS(db, info[0], info[1])

@app.route('/bind_device', methods=['POST'])
def bind_device():
    '''
    input value:
        info = json.loads(request.form['device_save_info'])
        - info[0] = do_id
        - info[1] = d_name
        - info[2] = d_id
    return value:
        return_id = '2'
    '''

    session = g.session
    data = request.form['device_save_info']
    info = json.loads(data) # info[0] = do_id, info[1] = d_name
    p_id = (
        session.query(db.DeviceObject.p_id)
        .filter(db.DeviceObject.do_id == info[0])
        .first()[0]
    )

    return_info = {
        'd_id': None,
        'p_dm_name': None,
    }
    print("\nbind_device:\n", info)

    ControlChannel.SET_DF_STATUS(db, info[0], info[2])

    p_id = (
        session.query(db.DeviceObject.p_id)
        .filter(db.DeviceObject.do_id == info[0])
        .first()[0]
    )
    data = (
        session.query(db.DeviceObject)
        .filter(db.DeviceObject.do_id == info[0])
        .first()
    )
    data.d_id = info[2]
    session.commit()
    #if current_prj_status == 'on':
    #    open_project(p_id)
    reopen_project(p_id)

    return_info = json.dumps(return_info)
    return return_info



@app.route('/unbind_device', methods=['POST'])
def unbind_device():
    '''
    input value:
        info = json.loads(request.form['device_save_info'])
        - info[0] = do_id
        - info[1] = d_name
        - info[2] = d_id
    return value:
        return_id = '2'
    '''

    session = g.session
    data = request.form['device_save_info']
    info = json.loads(data) # info[0] = do_id, info[1] = d_name

    ControlChannel.SUSPEND_device (db, info[0])

    p_id = (
        session.query(db.DeviceObject.p_id)
        .filter(db.DeviceObject.do_id == info[0])
        .first()[0]
    )
    return_info = {
        'd_id': None,
        'p_dm_name': None,
    }
    print("\nunbind_device:\n", info)
    p_id = (
        session.query(db.DeviceObject.p_id)
        .filter(db.DeviceObject.do_id == info[0])
        .first()[0]
    )
    ## lock project
    #current_prj_status = (
    #    session.query(db.Project.status)
    #    .filter(db.Project.p_id == p_id)
    #    .first()[0]
    #)
    #close_project(p_id)
    current_d_id = (
        session.query(db.DeviceObject.d_id)
        .filter(db.DeviceObject.do_id == info[0])
        .first()[0]
    )
    if current_d_id:
        dm_name = (
            session.query(db.DeviceModel.dm_name)
            .join(db.DeviceObject)
            .filter(db.DeviceObject.do_id == info[0])
            .first()[0]
        )
        data = (
            session.query(db.DeviceObject)
            .filter(db.DeviceObject.do_id == info[0])
            .first()
        )
        data.d_id = None
        session.commit()
        return_info['p_dm_name'] = dm_name
    #if current_prj_status == 'on':
    #    open_project(p_id)
    reopen_project(p_id)

    return_info = json.dumps(return_info)
    return return_info


# modify
@app.route('/get_correspond_connect_list', methods=['POST'])
def get_correspond_connect_list():
    '''
    input value:
        connection_pair = json.loads(request.form['connection_pair'])
        - connection_pair[0] = na_id
        - connection_pair[1] = dfo_id
        - connection_pair[2] = 'input' or 'output'
    return value:
        connection_node_info = {
            'id_list': [na_id, dfo_id],
            'corr_list':[['model_name/device_name', 'feature_name', dfo_id], ...]
        }
    '''

    session = g.session
    connection_pair = json.loads(request.form['connection_pair'])
    print("\nget_correspond:\n", connection_pair)
    connection_node_info = {
        'id_list':[connection_pair[0], connection_pair[1]],
        'corr_list':[]
    }
    na_id = connection_pair[0]
    in_or_out = connection_pair[2]
    corr_list = []

    # if is_input, find out all the relevant output lines, otherwise, input lines
    if in_or_out == 'input':
        in_or_out = 'output'
    else:
        in_or_out = 'input'

    relevant_line = (
        session.query(db.DeviceObject.dm_id, db.DeviceModel.dm_name, db.DeviceObject.d_id,
                      db.DeviceFeature.df_name, db.DF_Module.dfo_id)
        .select_from(db.DF_Module)
        .join(db.DFObject, db.DeviceFeature, db.DeviceObject, db.DeviceModel)
        .filter(db.DF_Module.na_id == na_id,db.DeviceFeature.df_type == in_or_out)
        .group_by(db.DF_Module.dfo_id)
        .all()
    )
    for dm_id, dm_name, d_id, df_name, dfo_id in relevant_line:
        if d_id == None:
            corr_list.append([dm_name, df_name, dfo_id])
        else:
            d_name = (
                session.query(db.Device.d_name)
                .filter(db.Device.d_id == d_id)
                .first()
            )
            if d_name != None:
                corr_list.append([d_name[0], df_name, dfo_id])
            else:
                print("This device has no name.")

    connection_node_info['corr_list'] = corr_list
    connection_node_info = json.dumps(connection_node_info)
    return connection_node_info

@app.route('/get_all_device_feature_by_dm_id', methods=['POST'])
def get_all_device_feature_by_dm_id():
    '''
    input value:
        feature_info = json.loads(request.form['feature_info'])
        {
            'dm_id': integer
        }
    return value:
        return_info = {
            'idf_list': [...],
            'odf_list': [...]
        }
    '''
    uid = 1
    session = g.session
    feature_info = json.loads(request.form['feature_info'])
    dm_id = feature_info['dm_id']
    idf_list = []
    odf_list = []
    feature_list = []
    for df_id in (
        session.query(db.DM_DF.df_id).filter(db.DM_DF.dm_id == dm_id)
    ):
        feature_list.append(df_id[0])
    print('feature_list'+str(feature_list))
    for df_id in feature_list:
        for df_name in (
            session.query(db.DeviceFeature.df_name).filter(db.DeviceFeature.df_type == "input")
            .filter(db.DeviceFeature.df_id == df_id)
        ):
            idf_list.append(df_name[0])

        for df_name in (
            session.query(db.DeviceFeature.df_name).filter(db.DeviceFeature.df_type == "output")
            .filter(db.DeviceFeature.df_id == df_id)
        ):
            odf_list.append(df_name[0])

    return_info = {
        'idf_list':[],
        'odf_list':[]
    }
    return_info['idf_list'] = idf_list
    return_info['odf_list'] = odf_list
    return_info = json.dumps(return_info)
    print('df_list', return_info)

    return return_info


@app.route('/get_device_list', methods=['POST'])
def get_device_list():
    '''
    input value:
        feature_info = json.loads(request.form['feature_info'])
        {
            'mount_info': {},
            'p_id': p_id,
            'dm_id': integer(optional)
        }
    return value:
        return_info = {
            'device_info': [[d_name, d_id], ...],
            'is_mounted': 1/0,
        }
    '''
    u_id = 1
    session = g.session
    feature_info = json.loads(request.form['feature_info'])
    p_id = feature_info['p_id']
    mount_info = feature_info['mount_info']
    print('\nget_device_list:\n', feature_info)

    feature_name_list = mount_info['device_feature_list'] #no use
    do_id = mount_info['do_id']

    if do_id != -1:
        mounted_device = (
            session.query(db.DeviceObject.d_id)
            .filter(db.DeviceObject.do_id == do_id)
            .first()[0]
        )
    else:
        mounted_device = -1;
    
    print('mounted_device_id\n', mounted_device)

    is_mounted = (
        session.query(db.DeviceObject.d_id)
        .filter(db.DeviceObject.d_id == mounted_device)
        .first()[0]
    )
    is_mounted = 0 if is_mounted == None else 1
    print(mounted_device, is_mounted)

    d_name_list = []
    d_id_list = []
    return_info = {
        'device_info': [],
        'is_mounted': is_mounted,
    }
    if do_id != -1:
        # filter by dm
        dm_id = (
            session.query(db.DeviceObject.dm_id)
            .filter(db.DeviceObject.do_id == do_id)
            .first()[0]
        )
    else:
        dm_id = (
            session.query(db.DeviceModel.dm_id)
            .filter(db.DeviceModel.dm_id == mount_info['dm_id']).first()
        )
        if dm_id == None:
            dm_id = -1
        else:
            dm_id = dm_id[0]

    print('dm_id: ', dm_id)
    for d_name, d_id in (
        session.query(db.Device.d_name, db.Device.d_id)
        #.select_from(db.Device)  #Issue#17, demand revert by YB
        #.outerjoin(db.DeviceObject, db.DeviceObject.d_id == db.Device.d_id)  #Issue#17, demand revert by YB
        .filter(db.Device.dm_id == dm_id,
                db.Device.status == 'online',
                #db.DeviceObject.d_id == None,  #Issue#17, demand revert by YB
                or_(db.Device.u_id == u_id, db.Device.u_id == None))
    ):
        d_name_list.append([d_name, 0, d_id]) # for is_sim
        d_id_list.append(d_id)


    return_info['device_info'] = d_name_list

    return_info = json.dumps(return_info)
    print('device_list', return_info)

    # turn other connections black
    for i in (
        session.query(db.DF_Module)
        .join(db.NetworkApplication)
        .filter(db.NetworkApplication.p_id == p_id)
        .all()
    ):
        i.color = 'black'
        session.commit()

    return return_info


@app.route('/get_function_info', methods=['POST'])
def get_function_info():
    '''
    input value:
        fn_id
    return value:
        return_info = {
           'code': 'def.....',
           'version': [['20150202', dnv_id], ...],
        }
    '''
    u_id = 1
    session = g.session
    fn_id = request.form['fn_id']
    print('\nget_function_info:\n', fn_id)
    return_info = {
        'code': None,
        'version': [],
    }

    draft = (
        session.query(db.FunctionVersion.code)
        .select_from(db.Function)
        .join(db.FunctionVersion)
        .filter(db.Function.fn_id == fn_id, db.FunctionVersion.u_id == u_id,
                db.FunctionVersion.completeness == 0)
        .first()
    )

    if draft != None:
        draft = draft[0]

    code = (
        session.query(db.FunctionVersion.code)
        .select_from(db.Function)
        .join(db.FunctionVersion)
        .filter(db.Function.fn_id == fn_id, db.FunctionVersion.u_id == u_id,
                db.FunctionVersion.completeness == 1)
        .order_by(desc(db.FunctionVersion.date))
        .first()
    )

    customize_version = (
        session.query(db.FunctionVersion.date, db.FunctionVersion.fnvt_idx,
                      db.FunctionVersion.completeness)
        .select_from(db.Function)
        .join(db.FunctionVersion)
        .filter(db.Function.fn_id == fn_id, db.FunctionVersion.u_id == u_id)
        .order_by(desc(db.FunctionVersion.date))
        .all()
    )

    # the function has been modified by the user (default -> customize)
    if len(customize_version) != 0:
        for i in customize_version:
            if i[2] == 1:
                return_info['version'].append([i[0].strftime('%Y%m%d'), i[1]])
            else:
                return_info['version'].append(['draft', i[1]])

    default_version = (
        session.query(db.FunctionVersion.fnvt_idx)
        .select_from(db.Function)
        .join(db.FunctionVersion)
        .filter(db.Function.fn_id == fn_id, db.FunctionVersion.u_id == None)
        .order_by(desc(db.FunctionVersion.date))
        .all()
    )
    for i in default_version:
        return_info['version'].append(['default', i[0]])

    if fn_id == 'add_function':
        return_info['code'] = 'def run(*args):\n\n    return'
        print(return_info)
        return_info = json.dumps(return_info)
        return return_info
    else:
        if code != None:
            code = code[0]
            if draft != None:
                return_info['code'] = draft
            else:
                return_info['code'] = code
            print(return_info)
            return_info = json.dumps(return_info)
            return return_info
        elif len(customize_version) != 0:
        # draft !!
            code = (
                session.query(db.FunctionVersion.code)
                .select_from(db.Function)
                .join(db.FunctionVersion)
                .filter(db.Function.fn_id == fn_id, db.FunctionVersion.u_id == u_id,
                        db.FunctionVersion.completeness == 0)
                .first()[0]
            )
            return_info['code'] = code
            print(return_info)
            return_info = json.dumps(return_info)
            return return_info
        else:
        # default function only
            code = (
                session.query(db.FunctionVersion.code)
                .select_from(db.Function)
                .join(db.FunctionVersion)
                .filter(db.Function.fn_id == fn_id, db.FunctionVersion.u_id == None)
                .order_by(desc(db.FunctionVersion.date))
                .first()[0]
            )
            return_info['code'] = code
            print(return_info)
            return_info = json.dumps(return_info)
            return return_info


@app.route('/get_function_version_body', methods=['POST'])
def get_function_version_body():
    '''
    input value:
        fnvt_idx
    return value:
        code
    '''
    session = g.session
    fnvt_idx = json.loads(request.form['fnvt_idx'])
    print('\nget_function_version_body:\n', fnvt_idx)

    # special case: generate code template
    if fnvt_idx == 0:
        code = 'def run():\n\n    return'
    else:
        code = (
            session.query(db.FunctionVersion.code)
            .filter(db.FunctionVersion.fnvt_idx == fnvt_idx)
            .first()[0]
        )
    print(code)
    return code


@app.route('/get_temp_function_list', methods=['POST'])
def get_temp_function_list():
    '''
    input value:
        dfo_id
    return value:
        ['fn_name', ...]
    '''
    u_id = 1
    session = g.session
    return_info = []
    dfo_id = json.loads(request.form['dfo_id'])

    print('\nget_temp_function_list:\n', dfo_id)

    if dfo_id == 0:
        feature_id = None
    else:
        feature_id = (
            session.query(db.DFObject.df_id)
            .filter(db.DFObject.dfo_id == dfo_id)
            .first()[0]
        )

    fn_name_list = (
        session.query(db.Function.fn_name)
        .join(db.FunctionVersion, db.FunctionSDF)
        .filter(db.FunctionVersion.u_id == u_id,
                db.FunctionVersion.completeness == 0,
                db.FunctionSDF.df_id == feature_id)
        .all()
    )
    for i in fn_name_list:
        return_info.append(i[0])

    print(return_info)
    return json.dumps(return_info)


@app.route('/check_function_is_switch', methods=['POST'])
def check_function_is_switch():
    '''
    input value:
        fn_id
    output value:
        argu_info = {
            'is_switch': 0/1,
            'non_df_argument': '',
            'fnvt_idx': None,
        }
            - 1: is switch
            - 0: otherwise
    '''
    u_id = 1
    session = g.session
    fn_id = request.form['fn_id']
    print('\ncheck_function_is_switch:\n', fn_id)
    argu_info = {
        'is_switch': None,
        'non_df_argument': '',
        'fnvt_idx': None,
    }
    non_df_argument = None
    fnvt_idx = 0
    is_switch = None

    query_fnv = (
        session.query(db.FunctionVersion.is_switch,
                      db.FunctionVersion.non_df_args,
                      db.FunctionVersion.fnvt_idx)
        .filter(db.FunctionVersion.fn_id == fn_id,
                db.FunctionVersion.u_id == u_id,
                db.FunctionVersion.completeness == 1)
        .order_by(desc(db.FunctionVersion.date))
        .first()
    )
    if query_fnv:
        is_switch = query_fnv[0]
        non_df_argument = query_fnv[1]
        fnvt_idx = query_fnv[2]
    else:
        query_fnv = (
            session.query(db.FunctionVersion.is_switch,
                          db.FunctionVersion.non_df_args,
                          db.FunctionVersion.fnvt_idx)
            .filter(db.FunctionVersion.fn_id == fn_id,
                    db.FunctionVersion.u_id == None,
                    db.FunctionVersion.completeness == 1)
            .order_by(desc(db.FunctionVersion.date))
            .first()
        )
        if query_fnv:
            is_switch = query_fnv[0]
            non_df_argument = query_fnv[1]
            fnvt_idx = query_fnv[2]
        else:
            is_switch = 0

    argu_info['is_switch'] = is_switch
    argu_info['non_df_argument'] = non_df_argument
    argu_info['fnvt_idx'] = fnvt_idx

    print(argu_info)
    return json.dumps(argu_info)


@app.route('/save_non_df_argument', methods=['POST'])
def save_non_df_argument():
    '''
    input value:
        argu_info={
            'fnvt_idx': None,
            'non_df_argument': '',
        }
    output value:
        'ok'
    '''
    u_id = 1
    session = g.session
    argu_info = json.loads(request.form['argu_info'])
    print('save_non_df_arguments:\n', argu_info)

    (
        session.query(db.FunctionVersion)
        .filter(db.FunctionVersion.fnvt_idx == argu_info['fnvt_idx'])
        .first()
    ).non_df_args = argu_info['non_df_argument']
    session.commit()
    return 'ok'


@app.route('/save_function_info', methods=['POST'])
def save_function_info():
    '''
    input value:
        fn_info = json.loads(request.form['fn_info'])
        fn_info = {
            'fn_name': '...',
            'code': 'def run()...',
            'df_id': 3,
            'fnvt_idx': 1,
            'is_switch': 0/1,
            'non_df_argument': '',
            'ver_enable': 0/1,
        }
    return value:
        return_info = {
            'fnvt_idx': 3,
                - 0: no draft stored
            'fn_id': 4,
    '''
    u_id = 1
    session = g.session
    data = request.form['fn_info']
    fn_info = json.loads(data)

    print("\nsave_function_info:\n", fn_info)
    return_info = {
        'fnvt_idx': None,
        'fn_id': None,
    }
    # check if the function unmodified
    isModify = (
        session.query(db.Function.fn_id, db.FunctionVersion.code,
                      db.FunctionVersion.is_switch)
        .join(db.FunctionVersion)
        .filter(db.Function.fn_name == fn_info['fn_name'],
                db.FunctionVersion.code == fn_info['code'],
                db.FunctionVersion.fnvt_idx == fn_info['fnvt_idx'],
                or_(db.FunctionVersion.u_id == u_id, db.FunctionVersion.u_id == None),
                db.FunctionVersion.is_switch == fn_info['is_switch'],
                db.FunctionVersion.non_df_args == fn_info['non_df_argument'])
        .first()
    )
    if isModify != None or len(''.join(fn_info['fn_name'].split())) == 0: # no name
        return_info['fnvt_idx'] = 0
        print(return_info)
        return json.dumps(return_info)

    # check if the function name exists
    fn_id = (
        session.query(db.Function.fn_id)
        .join(db.FunctionVersion)
        .filter(db.Function.fn_name == fn_info['fn_name'],
                or_(db.FunctionVersion.u_id == u_id, db.FunctionVersion.u_id == None))
        .first()
    )
    today = datetime.date.today()
    fnvt_idx = None
    if fn_id != None:
        # existing function
        print('old function\n')
        # only store one draft for one function
        fn_id = fn_id[0]
        old_date = (
            session.query(db.FunctionVersion.date)
            .filter(db.FunctionVersion.fn_id == fn_id,
                    or_(db.FunctionVersion.u_id == u_id, db.FunctionVersion.u_id == None)
            )
            .order_by(desc(db.FunctionVersion.date))
            .first()[0]
        )
        return_info['fn_id'] = fn_id
        (
            session.query(db.FunctionVersion)
            .filter(db.FunctionVersion.fn_id == fn_id,
                    db.FunctionVersion.u_id == u_id,
                    db.FunctionVersion.completeness == 0)
            .delete()
        )
        session.commit()
        new_ver_date = None
        if fn_info['is_switch'] == 1 and fn_info['ver_enable'] == 0:
            new_ver_date = old_date
        else:
            new_ver_data = today

        function_version = db.FunctionVersion(
            fn_id = fn_id, u_id = u_id, completeness = 0,
            date = new_ver_data, code = fn_info['code'], is_switch = fn_info['is_switch'],
            non_df_args = fn_info['non_df_argument']
        )
        session.add(function_version)
        session.commit()
        print(function_version.fnvt_idx, fn_info['is_switch'])
        fnvt_idx = function_version.fnvt_idx
    else:
        # new function
        print('new function\n')
        # 1. insert new entry into Function
        new_function = db.Function(fn_name = fn_info['fn_name'])
        session.add(new_function)
        session.commit()
        # 2. insert relevant info into FunctionVersion
        function_version = db.FunctionVersion(fn_id = new_function.fn_id,
            u_id = u_id, completeness = 0, date = today, code = fn_info['code'],
            is_switch = fn_info['is_switch'], non_df_args = fn_info['non_df_argument'])

        return_info['fn_id'] = new_function.fn_id
        session.add(function_version)
        session.commit()
        fnvt_idx = function_version.fnvt_idx
        # 3. insert positive list display info into FunctionList
        if fn_info['df_id'] != '0':
            df_id = (
                session.query(db.DFObject.df_id)
                .filter(db.DFObject.dfo_id == fn_info['df_id'])
                .first()
            )
        else: df_id = None
        if df_id: df_id = df_id[0]

        session.add(db.FunctionSDF(fn_id = new_function.fn_id, u_id = u_id,
            df_id = df_id, display = 1)
        )
        session.commit()
    return_info['fnvt_idx'] = fnvt_idx
    print(return_info)

    return json.dumps(return_info)


@app.route('/delete_all_temp_function', methods=['POST'])
def delete_all_temp_function():
    '''
    input value:
        df_id
    return value:
        'ok'
    '''
    u_id = 1
    session = g.session
    dfo_id = json.loads(request.form['df_id'])

    print('\ndelete_all_temp_function:\n', dfo_id)


    if dfo_id == 0:
        feature_id = None
    else:
        feature_id = (
            session.query(db.DFObject.df_id)
            .filter(db.DFObject.dfo_id == dfo_id)
            .first()[0]
        )

    all_fn_id = []

    all_df_fn_id_tuple = (
        session.query(db.FunctionSDF.fn_id)
        .filter(or_(db.FunctionSDF.u_id == None, db.FunctionSDF.u_id == u_id),
                db.FunctionSDF.df_id == feature_id)
        .group_by(db.FunctionSDF.fn_id)
        .all()
    )
    all_df_fn_id = [ df_fn_id for (df_fn_id, ) in all_df_fn_id_tuple ]

    if all_df_fn_id == []:
        all_fn_id = []
    else:
        all_fn_id = (
            session.query(db.FunctionVersion.fn_id)
            .filter(db.FunctionVersion.fn_id.in_(all_df_fn_id),
                    db.FunctionVersion.completeness == 0,
                    db.FunctionVersion.u_id == u_id)
            .all()
        )

    for id in all_fn_id:
        (
            session.query(db.FunctionVersion)
            .filter(db.FunctionVersion.completeness == 0,
                    db.FunctionVersion.u_id == u_id,
                    db.FunctionVersion.fn_id == id[0])
            .delete()
        )
        session.commit()
        if len(
                session.query(db.FunctionVersion.fnvt_idx)
                .filter(db.FunctionVersion.fn_id == id[0],
                        or_(db.FunctionVersion.u_id == None, db.FunctionVersion.u_id == u_id))
                .all()
        ) == 0:
            (
                session.query(db.FunctionSDF)
                .filter(db.FunctionSDF.fn_id == id[0])
                .delete()
            )
            session.commit()
            (
                session.query(db.Function)
                .filter(db.Function.fn_id == id[0])
                .delete()
            )
            session.commit()

    return 'ok'


@app.route('/delete_function_info', methods=['POST'])
def delete_function_info():
    '''
    input value:
        fnvt_idx = fnvt_idx
    return value:
        version = [['20150202', fnvt_idx], ...]
    '''
    u_id = 1
    session = g.session
    fnvt_idx = json.loads(request.form['fnvt_idx'])
    print('\ndelete_function_info:\n', fnvt_idx)
    version = []

    fn_id = (
        session.query(db.FunctionVersion.fn_id)
        .filter(db.FunctionVersion.fnvt_idx == fnvt_idx)
        .first()[0]
    )

    # check if all versions are deleted
    if (
        session.query(func.count(db.FunctionVersion.fnvt_idx))
        .filter(db.FunctionVersion.fn_id == fn_id,
                db.FunctionVersion.fnvt_idx != fnvt_idx,
                or_(db.FunctionVersion.u_id == u_id, db.FunctionVersion.u_id == None))
        .first()[0]
    )< 1:
        isUsed = (
            session.query(func.count(db.DF_Module.fn_id))
            .join(db.NetworkApplication, db.Project)
            .filter(db.DF_Module.fn_id == fn_id,
                    db.Project.u_id == u_id)
            .first()[0]
        )
        isUsed = isUsed + (
            session.query(func.count(db.DF_Parameter.fn_id))
            .filter(db.DF_Parameter.fn_id == fn_id,
                    db.DF_Parameter.u_id == u_id)
            .first()[0]
        )
        if isUsed == 0:
            (
                session.query(db.FunctionVersion)
                .filter(db.FunctionVersion.fnvt_idx == fnvt_idx, db.FunctionVersion.u_id == u_id)
                .delete()
            )
            session.commit()
            (
                session.query(db.FunctionSDF)
                .filter(db.FunctionSDF.fn_id == fn_id)
                .delete()
            )
            session.commit()
            (
                session.query(db.Function)
                .filter(db.Function.fn_id == fn_id)
                .delete()
            )
            session.commit()
    else:
        (
            session.query(db.FunctionVersion)
            .filter(db.FunctionVersion.fnvt_idx == fnvt_idx, db.FunctionVersion.u_id == u_id)
            .delete()
        )
        session.commit()

    ver = (
        session.query(db.FunctionVersion.date, db.FunctionVersion.fnvt_idx)
        .select_from(db.Function)
        .join(db.FunctionVersion)
        .filter(db.Function.fn_id == fn_id, db.FunctionVersion.u_id == u_id)
        .order_by(desc(db.FunctionVersion.date))
        .all()
    )

    # the function has been modified by the user (default -> customize)
    if len(ver) != 0:
        for i in ver:
            version.append([i[0].strftime('%Y%m%d'), i[1]])

    ver = (
        session.query(db.FunctionVersion.fnvt_idx)
        .select_from(db.Function)
        .join(db.FunctionVersion)
        .filter(db.Function.fn_id == fn_id, db.FunctionVersion.u_id == None)
        .order_by(desc(db.FunctionVersion.date))
        .all()
    )
    for i in ver:
        version.append(['default', i[0]])

    version = json.dumps(version)
    print(version)
    return version


@app.route('/move_in_df_function_list', methods=['POST'])
def move_in_df_function_list():
    '''
    input value:
        fn_info = {
            'fn_id': 1,
            'dfo_id': 3, 0 means Join
        }
    return value:
        positive_list={
            'other_list': [['x1',fn_id], [], ...],
            'quick_list': [['norm()', fn_id], [], ...],
        }
    '''
    u_id = 1
    session = g.session
    fn_info = json.loads(request.form['fn_info'])

    print("\nmove_in_df_function_list:\n", fn_info)

    positive_list = {
        'other_list': None,
        'quick_list': None,
    }

    feature_id = None
    if fn_info['dfo_id'] != 0:
        feature_id = (
            session.query(db.DFObject.df_id)
            .filter(db.DFObject.dfo_id == fn_info['dfo_id'])
            .first()[0]
        )

    isDefault = (
        session.query(func.count(db.FunctionSDF.fnsdf_id))
        .select_from(db.Function)
        .join(db.FunctionSDF)
        .filter(db.Function.fn_id == fn_info['fn_id'],
                db.FunctionSDF.u_id == None,
                db.FunctionSDF.df_id == feature_id)
        .first()[0]
    )

    # default function
    if isDefault > 0:
        (
            session.query(db.FunctionSDF)
            .filter(db.FunctionSDF.fn_id == fn_info['fn_id'],
                    db.FunctionSDF.df_id == feature_id,
                    db.FunctionSDF.u_id == u_id,
                    db.FunctionSDF.display == 0)
            .delete()
        )
        session.commit()

    # customize function
    else:
        (
            session.query(db.FunctionSDF)
            .filter(db.FunctionSDF.fn_id == fn_info['fn_id'],
                    db.FunctionSDF.df_id == feature_id,
                    db.FunctionSDF.u_id == u_id,
                    db.FunctionSDF.display == 1)
            .delete()
        )
        session.commit()
        session.add(
            db.FunctionSDF(
                fn_id=fn_info['fn_id'],
                df_id=feature_id,
                u_id=u_id, display=1
            )
        )
        session.commit()

    positive_list['quick_list'] = remove_disabled(get_df_function_list(feature_id))
    positive_list['other_list'] = remove_disabled(
        get_none_positive_list(get_all_function_list(), positive_list['quick_list']))
    positive_list['quick_list'].insert(0, ['add new function', 'add_function', 1])
    print(positive_list)

    return json.dumps(positive_list)


# modify
@app.route('/move_out_df_function_list', methods=['POST'])
def move_out_df_function_list():
    '''
    input value:
        fn_info = {
            'fn_id': 1,
            'dfo_id': 3,
        }
    return value:
        positive_list={
            'other_list': [['x1',fn_id], [], ...],
            'quick_list': [['norm()', fn_id], [], ...],
        }
    '''
    u_id = 1
    session = g.session
    fn_info = json.loads(request.form['fn_info'])

    print("\nmove_out_df_function_list:\n", fn_info)

    positive_list = {
        'other_list': None,
        'quick_list': None,
    }

    if fn_info['fn_id'] != 0:
        if fn_info['dfo_id'] == 0:
            feature_id = None
        else:
            feature_id = (
                session.query(db.DFObject.df_id)
                .filter(db.DFObject.dfo_id == fn_info['dfo_id'])
                .first()[0]
            )

        isDefault = (
            session.query(func.count(db.FunctionSDF.fnsdf_id))
            .filter(db.FunctionSDF.fn_id == fn_info['fn_id'],
                    db.FunctionSDF.u_id == None,
                    db.FunctionSDF.df_id == feature_id)
            .first()[0]
        )

        isUsed = (
            session.query(func.count(db.DF_Module.fn_id))
            .join(db.NetworkApplication, db.Project)
            .filter(db.DF_Module.fn_id == fn_info['fn_id'],
                    db.Project.u_id == u_id)
            .first()[0]
        )
        isUsed = isUsed + (session.query(func.count(db.DF_Parameter.fn_id))
            .filter(db.DF_Parameter.fn_id == fn_info['fn_id'],
                    db.DF_Parameter.u_id == u_id)).first()[0]
        isDraft = (session.query(func.count(db.FunctionVersion.completeness))
            .filter(db.FunctionVersion.u_id == u_id, db.FunctionVersion.completeness == 0,
                    db.FunctionVersion.fn_id == fn_info['fn_id'])).first()[0]

        print('isDefault:\n', isDefault)
        if isUsed == 0 and isDraft == 0:
            positive_list['fn_is_used'] = 0
            # default function
            if isDefault > 0:
                session.add(
                    db.FunctionSDF(
                        fn_id=fn_info['fn_id'],
                        df_id=feature_id,
                        u_id=u_id, display=0
                    )
                )
                session.commit()
            # customize function
            else:
                (session.query(db.FunctionSDF)
                    .filter(db.FunctionSDF.fn_id == fn_info['fn_id'],
                            db.FunctionSDF.df_id == feature_id,
                            db.FunctionSDF.u_id == u_id,
                            db.FunctionSDF.display == 1)).delete()
                session.commit()

    positive_list['quick_list'] = remove_disabled(get_df_function_list(feature_id))
    positive_list['other_list'] = remove_disabled(
        get_none_positive_list(get_all_function_list(), positive_list['quick_list'])
    )

    positive_list['quick_list'].insert(0, ['add new function', 'add_function', 1])
    print(positive_list)

    return json.dumps(positive_list)


@app.route('/get_updated_positive_config_info', methods=['POST'])
def get_updated_positive_config_info():
    '''
    input value:
        p_df_info = {
            'dfo_id': dfo_id,
            'param_i': param_i,
            'na_id': na_id
        }
            - odf module needs param_i to get fn_id for each dimension
    return value:
        return_info = {
            'fn_id': fn_id,
            'quick_list': [['norm()', fn_id], [], ...],
        }
    '''
    u_id = 1
    session = g.session
    p_df_info = request.form['p_df_info']
    p_df_info = json.loads(p_df_info)
    print('\nget_updated_positive_config_info:\n', p_df_info)
    dfo_id = int(p_df_info['dfo_id'])
    param_i = p_df_info['param_i']
    na_id = p_df_info['na_id']
    return_info = {
        'fn_id': None,
        'quick_list': None,
    }
    if na_id != 0:
        isConnected = (
            session.query(db.DF_Module.fn_id)
            .filter(db.DF_Module.param_i == param_i,
                    db.DF_Module.dfo_id == dfo_id,
                    db.DF_Module.na_id == na_id)
            .first()
        )

    # if dfo_id is 0, it means join module
    if dfo_id == 0:
        df_id = None
    else:
        df_id = (
            session.query(db.DFObject.df_id)
            .filter(db.DFObject.dfo_id == dfo_id)
            .first()
        )
        if df_id: 
            df_id = df_id[0]

            df_type = (session.query(db.DeviceFeature.df_type)
                .filter(db.DeviceFeature.df_id == df_id)
                .first()
            )
            if df_type: df_type = df_type[0]
            else: df_type = 0
        else:
            df_id = None
    # if not connected, get default function setting from DF_Parameter
    if isConnected == None or na_id == 0:
        if dfo_id != 0:
            (dm_id, d_id) = (
                session.query(db.DeviceObject.dm_id,
                              db.DeviceObject.d_id)
                .join(db.DFObject)
                .filter(db.DFObject.dfo_id == dfo_id)
                .first()
            )
            mf_id = (
                session.query(db.DM_DF.mf_id)
                .filter(db.DM_DF.dm_id == dm_id, db.DM_DF.df_id == df_id)
                .first()
            )
            if mf_id: mf_id = mf_id[0]
            else: mf_id=0

            isConnected = (
                session.query(db.DF_Parameter.fn_id)
                .filter(db.DF_Parameter.param_i == param_i, db.DF_Parameter.mf_id == mf_id,
                        )
                .first()
            )
            if isConnected == None:
                isConnected = (
                    session.query(db.DF_Parameter.fn_id)
                    .filter(db.DF_Parameter.param_i == param_i, db.DF_Parameter.mf_id == mf_id,
                            db.DF_Parameter.u_id == None)
                    .first()
                )
            return_info['fn_id'] = isConnected[0]

        # join module
        else:
            return_info['fn_id'] = (
                session.query(db.MultipleJoin_Module.fn_id)
                .filter(db.MultipleJoin_Module.na_id == na_id)
                .first()[0]
            )
    else:
        if dfo_id != 0:
            return_info['fn_id'] = isConnected[0]
        else:
            return_info['fn_id'] = (
                session.query(db.MultipleJoin_Module.fn_id)
                .filter(db.MultipleJoin_Module.na_id == na_id)
                .first()[0]
            )

    if na_id != 0:
        connected_idf = (
            session.query(db.DF_Module.dfo_id)
            .join(db.DFObject, db.DeviceFeature)
            .filter(db.DF_Module.na_id == na_id, db.DeviceFeature.df_type == 'input')
            .group_by(db.DF_Module.dfo_id)
            .all()
        )

    if df_id == None or ((len(connected_idf) > 1) and df_type == 'input'):
        #return_info['quick_list'] = remove_disabled(get_df_function_list(df_id))
        return_info['quick_list'] = get_df_function_list(df_id)
    else:
        return_info['quick_list'] = get_df_function_list(df_id)
    return_info['quick_list'].append(['add new function', 'add_function', 1])
    return_info = json.dumps(return_info)
    print(return_info)

    return return_info


@app.route('/get_dfo_function_list', methods=['POST'])
def get_dfo_function_list():
    '''
    input value:
        dfo_id = 3,
    return value:
        positive_list={
            'df_name': 'G-sensor',
            'other_list': [['x1',fn_id], [], ...],
            'quick_list': [['norm()', fn_id], [], ...],
        }
    '''
    session = g.session
    dfo_id = int(request.form['dfo_id'])
    print('\nget_df_function_list:\n', dfo_id)
    function_list = {
        'df_name': None,
        'quick_list': None,
        'other_list': None,
    }

    if dfo_id == 0:
        df_id = None
    else:
        df_id = (
            session.query(db.DFObject.df_id)
            .filter(db.DFObject.dfo_id == dfo_id)
            .first()[0]
        )

    if df_id == None:
        function_list['df_name'] = 'Join'
    else:
        function_list['df_name'] = (
            session.query(db.DeviceFeature.df_name)
            .filter(db.DeviceFeature.df_id == df_id)
            .first()[0]
        )
    function_list['quick_list'] = remove_df_function(
        remove_disabled(get_df_function_list(df_id)), 'set_range'
    )
    function_list['other_list'] = remove_disabled(
        get_none_positive_list(get_all_function_list(), function_list['quick_list'])
    )
    function_list['quick_list'].insert(0, ['add new function', 'add_function', 1])

    print(function_list)

    return json.dumps(function_list)


@app.route('/check_function_is_used', methods=['POST'])
def check_function_is_used():
    '''
    input value:
        fn_name
    output value:
        '1' / '0', # '1': using, '0': available
    '''
    u_id = 1
    session = g.session
    fn_name = request.form['fn_name']
    print('\ncheck_function_is_used: ', fn_name)

    #empty string
    if not fn_name.strip():
        return '0'

    query = (
        session.query(db.Function.fn_id)
        .filter(db.Function.fn_name == fn_name)
        .first()
    )
    if query != None:
        fn_id = query[0]
    else:
        return '0'

    isUsed = (
        session.query(func.count(db.DF_Module.fn_id))
        .filter(db.DF_Module.fn_id == fn_id)
        .first()[0]
    )
    print(isUsed)

    return '1' if (isUsed > 0) else '0'


@app.route('/get_log_data', methods=['POST'])
def get_log_data():
    '''
    input value:
        simulator_info = {
            'do_id': 12,
            'dfo_id': 23,
        }
    output value:
        'log data.............'
    '''
    session = g.session
    simulator_info = request.form['simulator_info']
    print('\nget_log_data:\n', simulator_info)

    simulator_info = json.loads(simulator_info)
    do_id = int(simulator_info['do_id'])
    dfo_id = int(simulator_info['dfo_id'])

    mac_addr = (
        session.query(db.Device.mac_addr)
        .join(db.DeviceObject)
        .filter(db.DeviceObject.do_id == do_id)
        .first()
    )

    if mac_addr:
        mac_addr = mac_addr[0]
        df_name = (
            session.query(db.DeviceFeature.df_name)
            .join(db.DFObject)
            .filter(db.DFObject.dfo_id == dfo_id)
            .first()[0]
        )
        log_data = pull_data(mac_addr, df_name, 'Input')
        return json.dumps(log_data)
    else:
        return ''



@app.route('/push_user_input_data', methods=['POST'])
def push_user_input_data():
    '''
    input value:
        user_input = {
            'idfo_id': idfo_id,
            'data': '23;34;45;...',
        }
    output value:
        'ok'
    '''
    session = g.session
    user_input = json.loads(request.form['user_input'])
    print('\npush_user_input_data:\n', user_input)
    idfo_id = user_input['idfo_id']

    (d_id, df_id, do_id) = (
        session.query(db.DeviceObject.d_id,
                      db.DFObject.df_id, db.DeviceObject.do_id)
        .select_from(db.DeviceObject)
        .join(db.DFObject)
        .filter(db.DFObject.dfo_id == idfo_id)
        .first()
    )

    dm_name = (
        session.query(db.DeviceModel.dm_name)
        .select_from(db.DeviceModel)
        .join(db.DeviceObject)
        .filter(db.DeviceObject.do_id == do_id)
        .first()[0]
    )
    mac_addr = (
        session.query(db.Device.mac_addr)
        .filter(db.Device.d_id == d_id)
        .first()[0]
    )

    data = [ ''.join(i.split()) for i in user_input['data'].split(';')]
    if '' in data:
        data.remove('')
    param_no = (
        session.query(db.DeviceFeature.param_no)
        .filter(db.DeviceFeature.df_id == df_id)
        .first()[0]
    )
    # wrong parameter numbers
    if param_no != len(data):
        print('\nwrong parameter numbers')
        return 'ok'

    df_parameter = (
        session.query(db.DF_Parameter.param_type)
        .select_from(db.DF_Parameter)
        .join(
            db.DM_DF,
            (db.DeviceModel, db.DM_DF.dm_id == db.DeviceModel.dm_id),
            (db.DeviceFeature, db.DM_DF.df_id == db.DeviceFeature.df_id),
        )
        .filter(db.DF_Parameter.u_id == None,
                db.DF_Parameter.mf_id != None,
                db.DeviceModel.dm_name == dm_name,
                db.DeviceFeature.df_id == df_id)
        .order_by(asc(db.DF_Parameter.param_i))
    )

    processed_data = []
    for data_, type_ in zip(data, df_parameter):
        print(data_, type_)

        try:
            if type_[0] == 'int':
                val = int(data_)
            elif type_[0] == 'float':
                val = float(data_)
            elif type_[0] == 'boolean':
                val = bool(data_)
            elif type_[0] == 'void':
                val = None
            elif type_[0] == 'string':
                val = str(data_)
            elif type_[0] == 'json':
                val = data_
            else:
                raise Exception('DF type not support: ' + type_[0])
        except ValueError:
            print('Wrong type', data_)
            val = None

        processed_data.append(val)

    return 'ok'


@app.route('/get_substage_list', methods=['POST'])
def get_substage_list():
    '''
    input value:
        monitor_info = {
            'is_multiple_join': 1/0,
            'na_id': 1,
            'odfo_id': 2
        }
    output value:
        substage_list = {
            'idf': ['Input', 'Type', 'Function', 'Normalization'],
            'odf': ['Function', 'Scaling'],
            'join': 0/1
                0: no multiple join
                1: multiple join
        }
    '''
    session = g.session
    monitor_info = request.form['monitor_info']
    monitor_info = json.loads(monitor_info)
    print('\nget_substage_list:\n', monitor_info)
    substage_list = {
        'idf': [],
        'odf': [],
        'join': 0,
    }
    is_multiple_join =  monitor_info['is_multiple_join']
    odfo_id = monitor_info['odfo_id']
    na_id = monitor_info['na_id']

    if is_multiple_join == 1:
        substage_list['idf'] = ['Input', 'Type', 'Function', 'Normalization']
    else:
        substage_list['idf'] = ['Input', 'Type', 'Function']
    odf_normalization = (
        session.query(db.DF_Module.normalization)
        .filter(db.DF_Module.na_id == na_id, db.DF_Module.dfo_id == odfo_id)
        .first()
    )
    if odf_normalization: odf_normalization = odf_normalization[0]
    else: odf_normalization == False

    if odf_normalization == True:
        print('scaling')
        substage_list['odf'] = ['Function', 'Scaling']
    else:
        print('no scaling')
        substage_list['odf'] = ['Function']
    return json.dumps(substage_list)


@app.route('/pull_monitored_data', methods=['POST'])
def pull_monitored_data():
    '''
    input value:
        data_path_info = {
            'na_id': 12,
            'idfo_id': 1,
            'i_substage': 'Input'/'Type'/'Function'/'Normalization'/,
            'odfo_id': 2,
            'o_substage': 'Function'/'Scaling',
            'execution_mode': 'Continue',
            'is_multiple_join': True/False,
        }
    output value:
        return_info = {
            'in': [[timestamp, log], ...],
            'join': [[timestamp, log], ...],
            'out': [[timestamp, log], ...]
        }
    '''
    session = g.session
    data_path_info = json.loads(request.form['data_path_info'])
    print('\npull_monitored_data:\n', data_path_info)

    return_info = {
        'in': [],
        'join': [],
        'out': [],
    }
    if  data_path_info['execution_mode'] == 'Step':
        print('return_info',return_info)
        return json.dumps(return_info)
    na_id = data_path_info['na_id']
    idfo_id = data_path_info['idfo_id']
    i_substage = data_path_info['i_substage']
    odfo_id = data_path_info['odfo_id']
    o_substage = data_path_info['o_substage']
    is_multiple_join = data_path_info['is_multiple_join']

    # monitor join module
    odo_id = (session.query(db.DeviceObject.d_id)
        .join(db.DFObject)
        .filter(db.DFObject.dfo_id == odfo_id)
        .first()
    )

    if odo_id: 
        odo_id = odo_id[0]
        out_mac_addr = (
            session.query(db.Device.mac_addr)
            .join(db.DeviceObject)
            .filter(db.DeviceObject.do_id == odo_id).first()
        )
    else: out_mac_addr = None

    ido_id = (session.query(db.DeviceObject.d_id)
        .join(db.DFObject)
        .filter(db.DFObject.dfo_id == idfo_id)
        .first()
    )

    if ido_id:
        ido_id = ido_id[0]
        in_mac_addr = (
            session.query(db.Device.mac_addr)
            .join(db.DeviceObject)
            .filter(db.DeviceObject.do_id == ido_id)
            .first()
        )
    else: in_mac_addr = None

    return_info['in'] = pull_data(None, None, i_substage, na_id, idfo_id)

    if is_multiple_join == True:
        return_info['join'] = pull_data(None, None, 'function', na_id, 0)

    return_info['out'] = pull_data(None, None, o_substage, na_id, odfo_id)

    print('in', len(return_info['in']), 'join', len(return_info['join']), 'out', len(return_info['out']))
    return_info = json.dumps(return_info)
    print(return_info)
    return return_info

@app.route('/get_monitor_info', methods=['POST'])
def get_monitor_info():
    '''
    input value:
        na_id = na_id
    output value:
        result = {
            'idf_info': [[df_name, df_id], ...],
            'odf_info': [[df_name, df_id], ...],
            'do_id': do_id,
            'exec_button': 'Continue',
            'join': 0/1,
        }
    '''
    session = g.session
    na_id = request.form['na_id']
    print('\nget_monitor_info:\n', na_id)

    result = {
        'idf_info': [],
        'odf_info': [],
        'exec_button': 'Continue',
        'is_multiple_join': False,
    }

    idf_info = (
        session.query(db.DeviceFeature.df_name, db.DFObject.dfo_id)
        .select_from(db.DF_Module)
        .join((db.DFObject,
              db.DF_Module.dfo_id == db.DFObject.dfo_id),
              (db.DeviceFeature,
              db.DFObject.df_id == db.DeviceFeature.df_id),
              (db.DeviceObject,
              db.DeviceObject.do_id == db.DFObject.do_id))
        .filter(db.DF_Module.na_id == na_id,
                db.DeviceFeature.df_type == 'input')
        .group_by(db.DFObject.dfo_id)
        .order_by(db.DeviceObject.do_idx, db.DFObject.dfo_id)
        .all()
    )

    odf_info = (
        session.query(db.DeviceFeature.df_name, db.DFObject.dfo_id)
        .select_from(db.DF_Module)
        .join((db.DFObject,
              db.DF_Module.dfo_id == db.DFObject.dfo_id),
              (db.DeviceFeature,
              db.DFObject.df_id == db.DeviceFeature.df_id),
              (db.DeviceObject,
              db.DeviceObject.do_id == db.DFObject.do_id))
        .filter(db.DF_Module.na_id == na_id,
                db.DeviceFeature.df_type == 'output')
        .group_by(db.DFObject.dfo_id)
        .order_by(desc(db.DeviceObject.do_idx), db.DFObject.dfo_id)
        .all()
    )

    result['idf_info'] = idf_info
    result['odf_info'] = odf_info
    is_multiple_join = (session.query(db.MultipleJoin_Module)
        .filter(db.MultipleJoin_Module.na_id == na_id)
        .first()
    )
    if is_multiple_join == None:
        result['is_multiple_join'] = False
    else:
        result['is_multiple_join'] = True

    d_id = (session.query(db.DeviceObject.d_id)
        .select_from(db.DeviceObject)
        .join(db.DFObject)
        .filter(db.DFObject.dfo_id == idf_info[0][1])
        .first()
    )
    if d_id: d_id = d_id[0]

    print('return_info:\n', result)
    return json.dumps(result)

@app.route('/get_realtime_data', methods=['POST'])
def get_realtime_data():
    '''
    input value:
        simulator_info = {
            'do_id': 12,
        }
    output value:
        return_info = [['df_name','log data.............'], ...]
    '''
    session = g.session
    simulator_info = request.form['simulator_info']
    print('\nget_realtime_data:\n', simulator_info)

    return_info = []

    simulator_info = json.loads(simulator_info)
    do_id = int(simulator_info['do_id'])

    mac_addr = (
        session.query(db.Device.mac_addr)
        .join(db.DeviceObject)
        .filter(db.DeviceObject.do_id == do_id)
        .first()
    )

    if mac_addr:
        mac_addr = mac_addr[0]
        df_name_id_list = (
            session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id)
            .join(db.DFObject)
            .filter(db.DFObject.do_id == do_id)
            .group_by(db.DeviceFeature.df_name)
            .all()
        )

        for df_name_id in df_name_id_list:
            return_info.append([df_name_id[1], pull_data(mac_addr, df_name_id[0], 'Input')])

    return_info = json.dumps(return_info)
    #print('return_info\n', return_info)
    return return_info


def dfm():
    return render_template('manage.html', category_list = ALL_CATEGORY)


auth = HTTPBasicAuth()
@auth.get_password
def get_pw(username):
    if username in ec_config.users:
        return ec_config.users.get(username)
    return None

if ec_config.manager_auth_required:
    connection = auth.login_required(connection)
    connection = app.route('/connection', methods=['GET'])(connection)
    dfm = auth.login_required(dfm)
    dfm = app.route('/dfm', methods=['GET'])(dfm)
else:
    connection = app.route('/connection', methods=['GET'])(connection)
    dfm = app.route('/dfm', methods=['GET'])(dfm)


projectMgrAuth = HTTPBasicAuth()
@projectMgrAuth.get_password
def set_pw(username):
    if username in ec_config.projectMgrUsers:
        return ec_config.projectMgrUsers.get(username)
    return None

projectMgr = projectMgrAuth.login_required(projectMgr)
projectMgr = app.route('/projectMgr', methods=['GET'])(projectMgr)

# Use authentication to reset project password API - ref: IOTTALKV1-1
resetProjectPassword = projectMgrAuth.login_required(reset_project_password)
resetProjectPassword = app.route('/reset_project_password', methods=['POST'])(resetProjectPassword)

#################### admin /company page ###################
# modify add comments
@app.route('/reload_admin_data', methods=['POST'])
def reload_admin_data():
    '''
    input value:
        dm_name/''
            '': add new device model
    output value:
        model_block = {
            'in_device': {
                'idf_list': [[df_name, df_id, comment], ...],
                'dm_name': dm_name,
                'dm_id': dm_id,
                'dm_type': dm_type,
            },
            'out_device': {
                'odf_list': [[df_name, df_id, comment], ...],
                'dm_name': dm_name,
                'dm_id': dm_id,
                'dm_type': dm_type,
            }
        }
    '''
    session = g.session
    dm_name = request.form['dm_name']
    #dm_name = 'Samsung-GT-i8552'
    (dm_id, dm_type) = (
        session.query(db.DeviceModel.dm_id, db.DeviceModel.dm_type)
        .filter(db.DeviceModel.dm_name == dm_name)
        .first()
    )

    print('\nreload_admin_data:\n', dm_name)

    model_block = {
        'in_device': {
            'idf_list': [],
            'dm_name': dm_name,
            'dm_id': dm_id,
            'dm_type': dm_type,
        },
        'out_device': {
            'odf_list': [],
            'dm_name': dm_name,
            'dm_id': dm_id,
            'dm_type': dm_type,
        },
    }
    if dm_name == '':
        return json.dumps(model_block)
    else:
        idf_info = (
            session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id, db.DeviceFeature.comment)
            .select_from(db.DeviceFeature)
            .join(
                db.DM_DF,
                (db.DeviceModel, db.DM_DF.dm_id == db.DeviceModel.dm_id),
            )
            .filter(db.DeviceModel.dm_id == dm_id, db.DeviceFeature.df_type == 'input')
            .all()
        )
        model_block['in_device']['idf_list'] = idf_info

        odf_info = (
            session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id, db.DeviceFeature.comment)
            .select_from(db.DeviceFeature)
            .join(
                db.DM_DF,
                (db.DeviceModel, db.DM_DF.dm_id == db.DeviceModel.dm_id),
            )
            .filter(db.DeviceModel.dm_id == dm_id, db.DeviceFeature.df_type == 'output')
            .all()
        )
        model_block['out_device']['odf_list'] = odf_info
        print('model_block\n', model_block)
        return json.dumps(model_block)


@app.route('/save_model_feature_info', methods=['POST'])
def save_model_feature_info():
    '''
    input value:
        feature_info = {
            'type': ['float', ...],
            'min': [1, ...],
            'max': [2, ...],
            'unit': [1, ...],
            'dm_id': dm_id,
            'df_id': df_id,
        }
    output value:
        '0'/'1'
            -'0': success
            -'1': fail
    '''
    session = g.session
    feature_info = json.loads(request.form['feature_info'])
    print('\nsave_model_feature_info:\n', feature_info)

    dm_id = feature_info['dm_id']
    df_id = feature_info['df_id']
    _min = feature_info['min']
    _max = feature_info['max']
    _unit = feature_info['unit']
    _type = feature_info['type']

    # get mf_id
    mf_id = (
        session.query(db.DM_DF.mf_id)
        .filter(db.DM_DF.dm_id == dm_id, db.DM_DF.df_id == df_id)
        .first()
    )

    if mf_id:
        print('exist')
        (
            session.query(db.DF_Parameter)
            .filter(db.DF_Parameter.mf_id == mf_id[0],
                    db.DF_Parameter.u_id == None,
                    db.DF_Parameter.df_id == None)
            .delete()
        )
        session.commit()
        #disabled_fn_id = (
        #    session.query(db.Function.fn_id)
        #    .filter(db.Function.fn_name == 'disabled')
        #    .first()[0]
        #)
        disabled_fn_id = -1
        for i in range(len(_type)):
            min_ = None if _min[i] == '' or _min[i] == _max[i] else _min[i]
            max_ = None if _max[i] == '' or _min[i] == _max[i] else _max[i]
            norm_ = 0 if min_ == None or max_ == None else 1
            new_df_parameter = db.DF_Parameter(
                df_id = None,
                mf_id = mf_id[0],
                param_i = i,
                param_type = _type[i],
                fn_id = None, #disabled_fn_id,
                u_id = None,
                idf_type = 'sample',
                min = min_,
                max = max_,
                unit_id = _unit[i],
                normalization = norm_
            )
            session.add(new_df_parameter)
            session.commit()
        return '0'
    else:
        return '1'

@app.route('/delete_device_model', methods=['POST'])
def delete_device_model():
    '''
    input value:
        dm_id
    output value:
        '0'/'1'
            '0': success
            '1': fail
    '''
    session = g.session
    dm_id = int(request.form['dm_id'])
    print('\ndelete_model_info:\n', dm_id)
    if dm_id != 0:
        # device
        device = (
            session.query(db.Device.d_id)
            .filter(db.Device.dm_id == dm_id, db.Device.status == 'online')
            .all()
        )
        # p_dm
        p_dm = (
            session.query(db.DeviceObject.do_id)
            .filter(db.DeviceObject.dm_id == dm_id)
            .all()
        )
        if len(device)+len(p_dm) == 0:
            dfp_id_list = [ dfp_id for (dfp_id, ) in (
                (session.query(db.DF_Parameter.dfp_id)
                .join(
                    db.DM_DF,
                    (db.DM_DF.mf_id == db.DF_Parameter.mf_id)
                )
                .filter(db.DM_DF.dm_id == dm_id)).all()) ]
            print(dfp_id_list)
            for dfp_id in dfp_id_list:
                (
                    session.query(db.DF_Parameter)
                    .filter(db.DF_Parameter.dfp_id == dfp_id)
                    .delete()
                )
                session.commit()
            d_id_list = (
                session.query(db.Device.d_id)
                .filter(db.Device.dm_id == dm_id)
                .all()
            )
            (
                session.query(db.Device)
                .filter(db.Device.dm_id == dm_id)
                .delete()
            )
            (
                session.query(db.DM_DF)
                .filter(db.DM_DF.dm_id == dm_id)
                .delete()
            )
            session.commit()
            (
                session.query(db.Device)
                .filter(db.Device.dm_id == dm_id)
                .delete()
            )
            (
                session.query(db.DeviceModel)
                .filter(db.DeviceModel.dm_id == dm_id)
                .delete()
            )
            session.commit()
            return '0'
        else:
            print('in use')
            return '1'
    else:
        return '0'

@app.route('/check_device_model_name_is_exist', methods=['POST'])
def check_device_model_name_is_exist():
    '''
    input value:
        feature_list = {
            'dm_name': dm_name,
        }
    output value:
        return_info = {
            'save_status': '0'/'1',
                - '0': success, '1' fail
            'dm_id': dm_id,
        }
    '''
    session = g.session
    dm_name = request.form['dm_name']

    if ''.join(dm_name.split()) != '':
        dm_id = (
            session.query(db.DeviceModel.dm_id)
            .filter(db.DeviceModel.dm_name == dm_name)
            .first()
        )
        if dm_id == None:
            return '0'

    return '1'


@app.route('/save_device_model', methods=['POST'])
def save_device_model():
    '''
    input value:
        feature_list = {
            'odf_list': [[df_name, df_id], ...],
            'idf_list': [[df_name, df_id], ...],
            'dm_name': dm_name,
            'dm_id': dm_id,
            'dm_type': dm_type,
        }
    output value:
        return_info = {
            'save_status': '0'/'1',
                - '0': success, '1' fail
            'dm_id': dm_id,
        }
    '''
    session = g.session
    feature_list = request.form['feature_list']
    feature_list = json.loads(feature_list)
    print('\nsave_device_model:\n', feature_list)
    return_info = {
        'save_status': '1',
        'dm_id': 0
    }
    dm_id = int(feature_list['dm_id'])
    dm_type = feature_list['dm_type']
    dm_name = feature_list['dm_name']
    odf_list = feature_list['odf_list']
    idf_list = feature_list['idf_list']
    if dm_type == 'P':
        dm_type = 'smartphone'
    elif dm_type == 'W':
        dm_type = 'wearable'
    else:
        dm_type = 'other'

    # create a new device model
    if ''.join(dm_name.split()) == '':
        return_info['save_status'] = '1'
        return_info['dm_id'] = dm_id
        print('empty name')
        return json.dumps(return_info)

    is_update = False
    if dm_id == 0:
    # check name exist
        dm_id = (
            session.query(db.DeviceModel.dm_id)
            .filter(db.DeviceModel.dm_name == dm_name)
            .first()
        )
        if dm_id != None:
            dm_id = dm_id[0]
            is_update = True
        else:
            # add new device model
            new_dm = db.DeviceModel(
                dm_name = dm_name,
                dm_type = dm_type
            )
            session.add(new_dm)
            session.commit()
            return_info['dm_id'] = new_dm.dm_id
            return_info['save_status'] = '0'
            for df in (idf_list+odf_list):
                new_dm_df = db.DM_DF(
                    dm_id = new_dm.dm_id,
                    df_id = df[1]
                )
                session.add(new_dm_df)
                session.commit()
                build_company_range_from_service(df[1], new_dm_df.mf_id)
            print('return_info:\n', return_info)
            return json.dumps(return_info)
    else:
        is_update = True


    if(is_update):
        # check if anyone uses this model
        is_used = (
            session.query(db.DeviceObject.do_id)
            .filter(db.DeviceObject.dm_id == dm_id)
            .all()
        )
        #is_used = []                         # Remove # ahead if you wnat to disable Device_Model_is_used check. That is, allows to add DFs into a running DM.
        if is_used == []:
            origin_dm_name = (
                session.query(db.DeviceModel.dm_name)
                .filter(db.DeviceModel.dm_id == dm_id)
                .first()
            )
            if origin_dm_name: origin_dm_name = origin_dm_name[0]
            if origin_dm_name == dm_name:
                exist_df = (
                    session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id)
                    .select_from(db.DeviceFeature)
                    .join(db.DM_DF)
                    .filter(db.DM_DF.dm_id == dm_id)
                    .all()
                )

                for df in exist_df:
                    if list((df[0], str(df[1]))) in (idf_list+odf_list):
                        continue
                    else:
                        # delete some device features
                        # delete entries in DF_Parameter
                        print('*\n*\n remove some df')
                        mf_id = (
                            session.query(db.DM_DF.mf_id)
                            .filter(db.DM_DF.dm_id == dm_id, db.DM_DF.df_id == df[1])
                            .first()
                        )
                        if mf_id: mf_id = mf_id[0]
                        (
                            session.query(db.DF_Parameter)
                            .filter(db.DF_Parameter.mf_id == mf_id)
                            .delete()
                        )
                        # delete entries in DM_DF
                        (
                            session.query(db.DM_DF)
                            .filter(db.DM_DF.mf_id == mf_id)
                            .delete()
                        )
                        session.commit()
                for df in (idf_list+odf_list):
                    if tuple((df[0],int(df[1]))) in exist_df:
                        continue
                    else:
                        # add new DM_DF entries
                        print('*\n*\n new df', df)
                        new_dm_df = db.DM_DF(
                            dm_id = dm_id,
                            df_id = df[1]
                        )
                        session.add(new_dm_df)
                        session.commit() # add ~
                        build_company_range_from_service(df[1], new_dm_df.mf_id)
                dm = (session.query(db.DeviceModel)
                    .filter(db.DeviceModel.dm_id == dm_id)).first()
                dm.dm_type = dm_type
                session.commit()

                return_info['dm_id'] = dm_id
                return_info['save_status'] = '0'
                print('success')
                print('return_info:\n', return_info)
                return json.dumps(return_info)
            else:
                new_dm = db.DeviceModel(
                    dm_name = dm_name,
                    dm_type = dm_type
                )
                session.add(new_dm)
                session.commit()
                return_info['dm_id'] = new_dm.dm_id
                return_info['save_status'] = '0'
                for df in (idf_list+odf_list):
                    new_dm_df = db.DM_DF(
                        dm_id = new_dm.dm_id,
                        df_id = df[1]
                    )
                    session.add(new_dm_df)
                    session.commit()
                    build_company_range_from_service(df[1], new_dm_df.mf_id)
                print('return_info:\n', return_info)
                return json.dumps(return_info)
        else:
            return_info['dm_id'] = dm_id
            return_info['save_status'] = '1'
            print('model is used')
            print('return_info:\n', return_info)
            return json.dumps(return_info)


@app.route('/delete_device_feature', methods=['POST'])
def delete_device_feature():
    '''
    input value:
        df_name
    output value:
        '0'/'1'
            '0': success
            '1': fail
    '''
    session = g.session
    df_name = request.form['df_name']
    print('\ndelete_device_feature:\n', df_name)
    df_id = (
        session.query(db.DeviceFeature.df_id)
        .filter(db.DeviceFeature.df_name == df_name)
        .first()
    )
    if df_id == None:
        print('This feature does not exist')
        return '0'
    # delete old entries in DF_Parameter & DeviceFeature
    df_is_used = (
        session.query(db.DM_DF.mf_id)
        .filter(db.DM_DF.df_id == df_id[0])
        .all()
    )
    if df_is_used == []:
    # not in use
        (
            session.query(db.DF_Parameter)
            .filter(db.DF_Parameter.u_id == None,
                    db.DF_Parameter.mf_id == None,
                    db.DF_Parameter.df_id == df_id[0])
            .delete()
        )
        (
            session.query(db.FunctionSDF)
            .filter(db.FunctionSDF.df_id == df_id[0])
            .delete()
        )
        (
            session.query(db.DeviceFeature)
            .filter(db.DeviceFeature.df_id == df_id[0])
            .delete()
        )
        session.commit()
        return '0'
    else:
        print('used')
        return '1'

@app.route('/check_device_feature_name_is_exist', methods=['POST'])
def check_device_feature_name_is_exist():
    '''
    input value:
        'df_name': 'g-sensor'
    retrun value:
        '0'/'1'
            '0': not exist
            '1': exist
    '''
    session = g.session
    df_name = request.form['df_name']

    if ''.join(df_name.split()) != '':
        df_id = (
            session.query(db.DeviceFeature.df_id)
            .filter(db.DeviceFeature.df_name == df_name)
            .first()
        )
        if df_id == None:
            return '0'

    return '1'

@app.route('/save_device_feature', methods=['POST'])
def save_device_feature():
    '''
    input value:
        feature_info = request.form['feature_info']
            feature_info = {
                'df_name': 'g-sensor',
                'df_category': 'Sight',
                'df_type': 'input'/'output',
                'df_comment': 'comment',
                'type': ['float', ...],
                'min': [-200, ...],
                'max': [200, ...],
                'unit': [1, ...],
            }
    return value:
        '0'/'1'
            '0': success
            '1': fail
    '''
    session = g.session
    feature_info = request.form['feature_info']
    feature_info = json.loads(feature_info)
    print('\nsave_device_feature:\n', feature_info)

    type_list = feature_info['type']
    min_list = feature_info['min']
    max_list = feature_info['max']
    unit_list = feature_info['unit']
    df_name = feature_info['df_name']
    df_comment = feature_info['df_comment']

    if ''.join(df_name.split()) != '':
        df_id = (
            session.query(db.DeviceFeature.df_id)
            .filter(db.DeviceFeature.df_name == df_name)
            .first()
        )
        if df_id != None:
        # df name exists
            df_id = df_id[0]
            print('exist')
            # delete old entries in DF_Parameter
            df_type_ = 'input' if feature_info['df_type'] == 'IDF' else 'output'
            df_query = (
                session.query(db.DeviceFeature)
                .filter(db.DeviceFeature.df_id == df_id)
                .first()
            )
            df_query.df_type = df_type_
            df_query.df_category = feature_info['df_category']
            df_query.comment = feature_info['df_comment']
            session.commit()
            (
                session.query(db.DF_Parameter)
                .filter(db.DF_Parameter.u_id == None,
                        db.DF_Parameter.mf_id == None,
                        db.DF_Parameter.df_id == df_id)
                .delete()
            )
            (
                session.query(db.FunctionSDF)
                .filter(db.FunctionSDF.df_id == df_id)
                .delete()
            )
            session.commit()
        # insert a new entry into DeviceFeature table
        else:
            df_type_ = 'input' if feature_info['df_type'] == 'IDF' else 'output'
            new_df = db.DeviceFeature(
                df_name = df_name,
                df_type = df_type_,
                df_category = feature_info['df_category'],
                param_no = len(type_list),
                comment = df_comment)
            session.add(new_df)
            session.commit()
            df_id = new_df.df_id

        # insert a new entry into DF_Parameter table
        disabled_name = 'disabled'
        #disabled_fn_id = (
        #    session.query(db.Function.fn_id)
        #    .filter(db.Function.fn_name == disabled_name)
        #    .first()[0]
        #)
        disabled_fn_id = -1

        for i in range(len(type_list)):
            normalization = 0 if feature_info['df_type'] == 'IDF' or min_list[i] == max_list[i] else 1
            min_ = None if min_list[i] == '' else min_list[i]
            max_ = None if max_list[i] == '' else max_list[i]
            new_parameter = db.DF_Parameter(
                df_id = df_id,
                mf_id = None,
                param_i = i,
                param_type = type_list[i],
                u_id = None,
                idf_type = 'sample',
                fn_id = None,
                min = min_,
                max = max_,
                unit_id = unit_list[i],
                normalization = normalization,
            )
            session.add(new_parameter)
            session.commit()
            if feature_info['df_type'] == 'ODF':
                fn_name = 'x' + str(i + 1)
                fn_id = (
                    session.query(db.Function.fn_id)
                    .filter(db.Function.fn_name == fn_name)
                    .first()
                )
                if fn_id == None:
                    # 1. insert new entry into Function
                    new_function = db.Function(fn_name = fn_name)
                    session.add(new_function)
                    session.commit()
                    # 2. insert relevant info into FunctionVersion
                    code = 'def run(*args):\n    return args[' + str(i) + ']'
                    function_version = db.FunctionVersion(fn_id = new_function.fn_id,
                        completeness = 1, date = datetime.date.today(), code = code,
                        is_switch = 0, non_df_args = '')
                    session.add(function_version)
                    session.commit()
                    fn_id = new_function.fn_id
                else:
                    fn_id = fn_id[0]

                session.add(
                    db.FunctionSDF(
                        fn_id=fn_id,
                        df_id=df_id,
                        u_id=1, display=1
                    )
                )
                session.commit()
        return '0'
    else:
        return '1'


@app.route('/get_category_feature', methods=['POST'])
def get_category_feature():
    '''
    input value:
        df_category = 'Sight',
    output value:
       feature_list = {
           'idf': [[df_name, df_id], ...],
           'odf': [[df_name, df_id], ...],
        }
    '''
    session = g.session
    df_category = request.form['df_category']

    print('\nget_category_feature:\n', df_category)
    feature_list = {
        'idf': [],
        'odf': [],
    }
    # idf
    for idf in (
        session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id)
        .filter(db.DeviceFeature.df_category == df_category,
                db.DeviceFeature.df_type == 'input')
        .order_by(db.DeviceFeature.df_name)
        .all()
    ):
        feature_list['idf'].append([idf[0], idf[1]])

    # odf
    for odf in (
        session.query(db.DeviceFeature.df_name, db.DeviceFeature.df_id)
        .filter(db.DeviceFeature.df_category == df_category,
                db.DeviceFeature.df_type == 'output')
        .order_by(db.DeviceFeature.df_name)
        .all()
    ):
        feature_list['odf'].append([odf[0], odf[1]])

    print('return info:\n', feature_list)
    return json.dumps(feature_list)


@app.route('/get_category_list', methods=['POST'])
def get_category_list():
    '''
    input value:
        None
    output value:
        ['Sight', 'Hearing', 'Feeling', 'Motion', 'Other', ]
    '''
    session = g.session

    category_list = {
        'idf_category': [],
        'odf_category': []
    }

    idf = (session.query(db.DeviceFeature.df_category)
                 .filter(db.DeviceFeature.df_type == 'input')
                 .group_by(db.DeviceFeature.df_category)
                 .all()
          )

    odf = (session.query(db.DeviceFeature.df_category)
                 .filter(db.DeviceFeature.df_type == 'output')
                 .group_by(db.DeviceFeature.df_category)
                 .all()
          )

    for category in idf:
        category_list['idf_category'].append(category[0])

    for category in odf:
        category_list['odf_category'].append(category[0])

    return json.dumps(category_list)


@app.route('/get_type_list', methods=['POST'])
def get_type_list():
    '''
    input value:
        None
    output value:
        ['float', 'int', 'boolean', 'void', 'string', 'json']
    '''
    return json.dumps(['float', 'int', 'boolean', 'void', 'string', 'json'])


@app.route('/get_category_by_df_name', methods=['POST'])
def get_category_by_df_name():
    '''
    input value:
        df_name
    output value:
        category
    '''
    session = g.session
    df_name = request.form['df_name']
#    df_name = 'G-sensor'
    category = (
        session.query(db.DeviceFeature.df_category)
        .filter(db.DeviceFeature.df_name == df_name)
        .first()
    )
    if category: category = category[0]
    return category


@app.route('/get_feature_info', methods=['POST'])
def get_feature_info():
    '''
    input value:
            feature_name = 'G-sensor'
    return value:
        feature_info = {
            'df_id': df_id,
            'df_name': 'G-sensor',
            'df_category': 'Sight',
            'df_type': 'input'/'output',
            'df_comment': 'comment',
            'df_parameter': [[df_type, min, max, unit_id], ['float', -20, 20, 1], ...],
            'all_parameter_type': ['float', 'int', 'boolean', 'void', 'string', 'json'],
            'all_df_category': ['Sight', 'Hearing', 'Feeling', 'Motion', 'Other', ]
        }
    '''

    session = g.session
    feature_name = request.form['feature_name']
    print('\nget_feature_info:\n', feature_name)

    feature_info = {
        'df_id': 0,
        'df_name': feature_name,
        'df_category': 'Sight',
        'df_type': 'input',
        'df_comment': '',
        'df_parameter': [],
        'all_parameter_type': ['float', 'int', 'boolean', 'void', 'string', 'json'],
        'all_df_category':  ALL_CATEGORY,
     }


    if feature_name == '':
        feature_info['df_parameter'].append(['float', 0, 0])
        feature_info = json.dumps(feature_info)
        print('feature_info\n', feature_info)
        return feature_info

    (df_category, df_type, df_id, df_comment) = (
        session.query(db.DeviceFeature.df_category,
                      db.DeviceFeature.df_type,
                      db.DeviceFeature.df_id,
                      db.DeviceFeature.comment)
        .filter(db.DeviceFeature.df_name == feature_name)
        .first()
    )

    feature_info['df_id'] = df_id
    feature_info['df_category'] = df_category
    feature_info['df_type'] = df_type
    feature_info['df_comment'] = df_comment

    service_default = (
        session.query(db.DF_Parameter.param_type, db.DF_Parameter.min, db.DF_Parameter.max, db.DF_Parameter.unit_id)
        .filter(db.DF_Parameter.mf_id == None, db.DF_Parameter.df_id == df_id,
                db.DF_Parameter.u_id == None)
        .order_by(db.DF_Parameter.param_i)
        .all()
    )
    for i in service_default:
        feature_info['df_parameter'].append([i[0], i[1], i[2], i[3]])

    feature_info = json.dumps(feature_info)
    print('feature_info\n', feature_info)
    return feature_info


@app.route('/get_device_feature_info', methods=['POST'])
def get_device_feature_info():
    '''
    input value:
        model_info = {
            'df_name': 'G-sensor',
            'dm_id': dm_id,
        }
    return value:
        feature_info = {
            'df_name': 'G-sensor',
            'df_category': 'Sight',
            'df_type': 'input'/'output',
            'df_parameter': [[df_type, min, max, unit_id], ['float', -20, 20, 1], ...],
            'all_parameter_type': ['float', 'int', 'boolean', 'void', 'string', 'json'],
            'all_df_category': ['Sight', 'Hearing', 'Feeling', 'Motion', 'Other', ],
            'accessible': '0'/'1',
                -'0': can save
        }
    '''

    session = g.session
    model_info = json.loads(request.form['model_info'])

    print('\nget_device_feature_info:\n', model_info)
    df_name = model_info['df_name']
    dm_id = model_info['dm_id']

    feature_info = {
        'df_name': '',
        'df_category': 'Sight',
        'df_type': 'input',
        'df_parameter': [],
        'all_parameter_type': ['float', 'int', 'boolean', 'void', 'string', 'json'],
        'all_df_category': ALL_CATEGORY,
        'accessible': '1',
     }


    if df_name == '':
        feature_info['df_parameter'].append(['float', 0, 0])
        feature_info = json.dumps(feature_info)
        print('feature_info\n', feature_info)
        return feature_info

    feature_info['df_name'] = df_name

    (df_category, df_type, df_id) = (
        session.query(db.DeviceFeature.df_category, db.DeviceFeature.df_type, db.DeviceFeature.df_id)
        .filter(db.DeviceFeature.df_name == df_name)
        .first()
    )

    feature_info['df_category'] = df_category
    feature_info['df_type'] = df_type

    mf_id = (
        session.query(db.DM_DF.mf_id)
        .filter(db.DM_DF.dm_id == dm_id, db.DM_DF.df_id == df_id)
        .first()
    )
    if mf_id:
        # priority2 (mf_id) company(?)
        mf_id = mf_id[0]
        query_result = (
            session.query(db.DF_Parameter.param_type, db.DF_Parameter.min, db.DF_Parameter.max, db.DF_Parameter.unit_id)
            .filter(db.DF_Parameter.mf_id == mf_id, db.DF_Parameter.u_id == None)
            .order_by(db.DF_Parameter.param_i)
            .all()
        )

        if len(query_result) <= 0:
        # priority3 (u_id & mf_id = None) service
            query_result = (
                session.query(db.DF_Parameter.param_type, db.DF_Parameter.min, db.DF_Parameter.max, db.DF_Parameter.unit_id)
                .filter(db.DF_Parameter.mf_id == None, db.DF_Parameter.df_id == df_id,
                        db.DF_Parameter.u_id == None)
                .order_by(db.DF_Parameter.param_i)
                .all()
            )
        feature_info['accessible'] = '0'
    else:
        query_result = (
            session.query(db.DF_Parameter.param_type, db.DF_Parameter.min, db.DF_Parameter.max, db.DF_Parameter.unit_id)
            .filter(db.DF_Parameter.mf_id == None, db.DF_Parameter.df_id == df_id,
                    db.DF_Parameter.u_id == None)
            .order_by(db.DF_Parameter.param_i)
            .all()
        ) #service
        feature_info['accessible'] = '1'

    for i in query_result:
        feature_info['df_parameter'].append([i[0], i[1], i[2], i[3]])

    feature_info = json.dumps(feature_info)
    print('feature_info\n', feature_info)
    return feature_info


@app.route('/delete_project', methods=['POST'])
def delete_project():
    '''
    input value:
        p_id
    output value:
        'ok'
    '''
    session = g.session
    p_id = int(request.form['p_id'])
    print('\ndelete_project:\n', p_id)

    # delete all NetworkApplication related records
    for na_id, in (session.query(db.NetworkApplication.na_id)
        .filter(db.NetworkApplication.p_id == p_id)
    ):
        # delete records in MultipleJoin_Module
        (session.query(db.MultipleJoin_Module)
        .filter(db.MultipleJoin_Module.na_id == na_id)
        ).delete()
        session.commit()

        # delete DFModule
        (session.query(db.DF_Module)
        .filter(db.DF_Module.na_id == na_id)
        ).delete()
        session.commit()

        # delete NetworkApplication
        (session.query(db.NetworkApplication)
        .filter(db.NetworkApplication.na_id == na_id)
        ).delete()
        session.commit()

    # delete all DeviceObject related records
    for do_id, in (session.query(db.DeviceObject.do_id)
        .filter(db.DeviceObject.p_id == p_id)
    ):
        (session.query(db.DFObject)
        .filter(db.DFObject.do_id == do_id)
        ).delete()
        session.commit()
        (session.query(db.DeviceObject)
        .filter(db.DeviceObject.do_id == do_id)
        ).delete()
        session.commit()

    # delete Project
    (session.query(db.Project)
    .filter(db.Project.p_id == p_id)
    ).delete()
    session.commit()

    return 'ok'

@app.route('/get_unit_list', methods=['POST'])
def get_unit_list():
    '''
    output value:
        unit_list = [
            {'unit_id': unit_id,  'unit_name': unit_name},
            ...
        ]
    '''
    session = g.session
    unit_list = []
    query = (session.query(db.Unit).all())
    for unit in query:
        unit_list.append({'unit_id': unit.unit_id, 'unit_name': unit.unit_name})
    unit_list = json.dumps(unit_list)
    return unit_list

@app.route('/add_unit', methods=['POST'])
def add_unit():
    '''
    input value:
        { 'unit_name' : unit_name, }
    output value:
        response = {
            'unit_id': unit_id, 
            'status': 'ok'/'is_exist'/'err'
        }
    '''
    session = g.session
    unit_name = request.form['unit_name'].strip()
    response = {
        'status': 'err',
        'unit_id': None,
    }

    unit_id = (session.query(db.Unit.unit_id)
                    .filter(db.Unit.unit_name == unit_name)
                    .first()
            )

    if not unit_id:
        unit = db.Unit(unit_name = unit_name)
        session.add(unit)
        session.commit()
        unit_id = unit.unit_id
        if unit_id:
            response['status'] = 'ok'
            response['unit_id'] = unit_id
    else:
        response['status'] = 'is_exist'
        response['unit_id'] = unit_id[0]

    response = json.dumps(response)
    return response

def get_mdb_id():
    if os.path.isfile('MDB_ID'):
        with open('MDB_ID') as f:
            mdb_id = f.read()
            try:
                val = uuid.UUID(mdb_id, version=4)
                return str(val)
            except ValueError:
                pass

    with open('MDB_ID', 'w') as f:
        mdb_id = str(uuid.uuid4())
        f.write(mdb_id)
        return mdb_id

    raise Exception('can\'t get MDB_ID')

@app.route('/get_all_category', methods=['POST'])
def get_all_category():
    return json.dumps(ALL_CATEGORY)

@app.route('/download_feature', methods=['GET'])
def download_feature():
    mdb_id = get_mdb_id()
    return render_template('download_feature.html', category_list = ALL_CATEGORY, mdb_id = mdb_id)

@app.route('/save_download_feature', methods=['POST'])
def save_download_feature():
    '''
    input value:
        {
            "name": string,
            "type": enum['input', 'output'],
            "category": string,
            "description": string,
            "parameter": [
                {
                    "data_type": enum['float', 'int', 'void', 'boolean', 'string', 'json'],
                    "type": enum['variant', 'sample'],
                    "min": int,
                    "max": int,
                    "normalization": boolean,
                    "function": string,
                    "unit": string,
                },
                ...
            ]
        }
    output value:
        {
            'status': 'ok' / 'err',
            'msg': '',
            'df_id': '',
        }
    '''
    response = {'status': '', 'msg': ''}

    df_info = json.loads(request.form['df_info'])

    session = g.session
    
    df_name = df_info['name']
    df_type = df_info['type']
    df_category = df_info['category']
    df_comment = df_info['description']
    df_parameter = df_info['parameter']

    #check function is exist
    for parameter in df_parameter:
        fn_name = parameter['function']
        fn_id = (session.query(db.Function.fn_id)
                        .select_from(db.Function)
                        .filter(db.Function.fn_name == fn_name)
                        .first()
                )
        if not fn_id:
            response['status'] = 'err'
            response['msg'] = 'didn\'t find matching function: ' + fn_name
            return json.dumps(response)

        parameter['fn_id'] = fn_id[0]

    #check unit is exist
    for parameter in df_parameter:
        unit_name = parameter['unit']
        unit_id = (session.query(db.Unit.unit_id)
                          .select_from(db.Unit)
                          .filter(db.Unit.unit_name == unit_name)
                          .first()
                  )
        if not unit_id:
            new_unit = db.Unit(unit_name = unit_name)
            session.add(new_unit)
            session.commit()
            unit_id = new_unit.unit_id
            parameter['unit_id'] = unit_id
        else:
            parameter['unit_id'] = unit_id[0]
    
    #check name
    serial_number = (session.query(
                                cast(
                                    func.replace(
                                        func.replace(db.DeviceFeature.df_name, df_name, ''), ' -', ''),
                                    Integer
                                )
                             )
                            .select_from(db.DeviceFeature)
                            .filter(db.DeviceFeature.df_name.like(df_name + '%'))
                            .order_by(
                                cast(
                                    func.replace(
                                        func.replace(db.DeviceFeature.df_name, df_name, ''), ' -', ''),
                                    Integer
                                )
                                .desc()
                            )
                           .first()
                   )

    #name exist, add serial number to save
    if serial_number:
        df_name = df_name + ' -' + str(serial_number[0] + 1)

    #save feature
    new_df = db.DeviceFeature(
                df_name = df_name,
                df_type = df_type,
                df_category = df_category,
                param_no = len(df_parameter),
                comment = df_comment)
    session.add(new_df)
    session.commit()
    df_id = new_df.df_id

    #save parameter
    for index, parameter in enumerate(df_parameter):
        normalization = 0 if df_type == 'input' or parameter['min'] == parameter['max'] else 1
        min_ = None if parameter['min'] == '' else parameter['min']
        max_ = None if parameter['max'] == '' else parameter['max']
        new_parameter = db.DF_Parameter(
            df_id = df_id,
            mf_id = None,
            param_i = index,
            param_type = parameter['data_type'],
            u_id = None,
            idf_type = parameter['type'],
            fn_id = parameter['fn_id'],
            min = min_,
            max = max_,
            unit_id = parameter['unit_id'],
            normalization = normalization,
        )
        session.add(new_parameter)
        session.commit()


    response['status'] = 'ok'
    response['msg'] = 'done'
    response['df_id'] = df_id

    return json.dumps(response)

@app.route('/upload_feature', methods=['POST'])
def upload_feature():
    '''
        input value
            {
                'username': 'username',
                'df_id': df_id
            }
        output value
            {
                'status': '',
                'message': ''
            }
    '''
    username = request.form['username']
    df_id = request.form['df_id']
    session = g.session
    result = (session.query(
                            db.DeviceFeature.df_name,
                            db.DeviceFeature.df_type,
                            db.DeviceFeature.df_category,
                            db.DeviceFeature.comment,
                            db.DF_Parameter.param_type,
                            db.DF_Parameter.idf_type,
                            db.DF_Parameter.min,
                            db.DF_Parameter.max,
                            db.DF_Parameter.normalization,
                            db.Function.fn_name,
                            db.Unit.unit_name,
                      )
                      .select_from(db.DeviceFeature)
                      .join(db.DF_Parameter)
                      .join(db.Function)
                      .join(db.Unit)
                      .filter(db.DeviceFeature.df_id == (db.DeviceFeature.df_id if not df_id else df_id))
                      .order_by(asc(db.DeviceFeature.df_id), asc(db.DF_Parameter.param_i))
                      .all()
             )

    if not result or len(result) <= 0:
        return json.dumps({'status': 'err', 'message': 'device feature not find'})

    doc = {
        '_id': get_mdb_id(),
        'version': "1",
        'user': username,
        'timestamp': time.time(),
        'device_feature':[],
    }

    feature = {
        'name': None,
        'type': None,
        'category': None,
        'description': None,
        'parameter': [],
    }

    parameter = {
        'data_type': None,
        'type': None,
        'min': None,
        'max': None,
        'normalization': None,
        'function': None,
        'unit': None,
    }

    for row in result:
        if feature['name'] != row[0]:
            if feature['name'] != None:
                doc['device_feature'].append(feature.copy())

            feature['name'] = row[0]
            feature['type'] = row[1]
            feature['category'] = row[2]
            feature['description'] = row[3]
            feature['parameter'] = []
        
        parameter['data_type'] = row[4]
        parameter['type'] = row[5]
        parameter['min'] = row[6]
        parameter['max'] = row[7]
        parameter['normalization'] = row[8]
        parameter['function'] = row[9]
        parameter['unit'] = row[10]
        
        feature['parameter'].append(parameter.copy())

    if feature['name'] != None:
        doc['device_feature'].append(feature.copy())

    client = Cloudant(ec_config.MDB_KEY, ec_config.MDB_PASS, account = ec_config.MDB_ACCOUNT)
    client.connect()
    MDB = client[ec_config.MDB_TABLE_FEATURE]

    try:
        remote_doc = MDB[doc['_id']]
        remote_doc['user'] = username
        remote_doc['timestamp'] = time.time()

        if not df_id:
            remote_doc['device_feature'] = doc['device_feature']
        else:
            for remote_df in remote_doc['device_feature']:
                if remote_df['name'] == feature['name']:
                    remote_doc['device_feature'].remove(remote_df)
                    break
            remote_doc['device_feature'].append(feature)

        remote_doc.save()
            
    except KeyError:
        print(MDB.create_document(doc))

    return json.dumps({'status': 'ok', 'id': doc['_id']})


@app.route('/check_project_name_is_exist', methods=['POST'])
def check_project_name_is_exist():
    '''
        input value
            {
                'project_name': 'project_name',
            }
        output value
            {
                'status': 'ok',
                'is_exist': boolean,
            }
    '''
    project_name = request.form['project_name']
    session = g.session
    result = (session.query(func.count(db.Project.p_name))
                      .select_from(db.Project)
                      .filter(db.Project.p_name == project_name)
                      .first()
             )
    if result: result = result[0]
    return json.dumps({'status': 'ok', 'is_exist': (result!=0)})


#################### db setting ##############
@app.before_request
def before_request():
    g.session = db.get_session()

@app.teardown_request
def teardown_request(exception):
    session = getattr(g, 'session', None)
    if session is not None:
        session.close()


#################### ccmapi ####################
from ccm.api.v0.devicefeature import api as devicefeature_api_v0
from ccm.api.v0.device import api as device_api_v0
from ccm.api.v0.devicemodel import api as devicemodel_api_v0
from ccm.api.v0.project import api as project_api_v0
from ccm.api.v0.deviceobject import api as deviceobject_api_v0
from ccm.api.v0.networkapplication import api as na_api_v0


# API blueprint
app.register_blueprint(project_api_v0, url_prefix='/api/v0/project')
app.register_blueprint(deviceobject_api_v0,
                       url_prefix='/api/v0/project/<int:p_id>/deviceobject')
app.register_blueprint(device_api_v0,
                       url_prefix='/api/v0/project/<int:p_id>/deviceobject/<int:do_id>/device')
app.register_blueprint(na_api_v0, url_prefix='/api/v0/project/<int:p_id>/na')
app.register_blueprint(devicemodel_api_v0, url_prefix='/api/v0/devicemodel')
app.register_blueprint(devicefeature_api_v0, url_prefix='/api/v0/devicefeature')


#################### main ####################
if __name__ == '__main__':
    app.config['SESSION_REFRESH_EACH_REQUEST'] = False
    app.run(
        host = ec_config.CCM_HOST, 
        port = ec_config.CCM_PORT,
        threaded = True,
        debug = ec_config.IS_DEBUG,
    )
