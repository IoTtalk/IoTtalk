#!/usr/bin/env python3

from datetime import date
import subprocess
import sys

import db
from db_const import *
from ec_config import SQLITE_PATH, MYSQL_HOST, MYSQL_USER, MYSQL_PASS

USAGE = '''\
Usage: {0} <db_name> [-q]
Usage: {0} sqlite:<file_name>.db [-q]

    -q  quite mode.
'''.format(sys.argv[0])

def insert_values(session):
    # DeviceFeature
    df = {}
    for k, v in DEVICE_FEATURE.items():
        df[k] = db.DeviceFeature(
            df_name = k,
            df_type = v[0], df_category = v[1], param_no = v[2], comment = v[3],
        )
    session.add_all(df.values())
    session.commit()

    # DeviceModel
    dm = {}
    for k, v in DEVICE_MODEL.items():
        dm[k] = db.DeviceModel(dm_name=k, dm_type=v)
    session.add_all(dm.values())
    session.commit()

    # Unit
    un = {}
    for unit in UNIT:
        un[unit] = db.Unit(unit_name = unit)
        session.add(un[unit])
    #session.add_all(un.values())
    session.commit()

    # User
    user = {}
    for k, v in USER.items():
        user[k] = db.User(u_name=k, passwd=v)
    session.add_all(user.values())
    session.commit()

    # Project
    prj = set()
    for k, v in PROJECT.items():
        prj.add(db.Project(
            p_name = k,
            u_id = user[v].u_id,
            status = 'on', restart = False, exception = '', sim = 'off', pwd = ''
        ))
    session.add_all(prj)
    session.commit()

    # DM_DF
    mf = {}
    for dm_name, df_name in DFPARAMETER_FOR_DM.keys():
        mf[(dm_name, df_name)] = db.DM_DF(
            dm_id = dm[dm_name].dm_id,
            df_id = df[df_name].df_id,
        )
    session.add_all(mf.values())
    session.commit()

    # DF_Parameter
    dfp = set()
    for df_name, params in DFPARAMETER_FOR_DF.items():
        for param_i, param in enumerate(params):
            dfp.add(db.DF_Parameter(
                df_id = df[df_name].df_id,
                mf_id = None,
                param_i = param_i,
                param_type = param[0],
                idf_type = param[1],
                normalization = param[2], min = param[3], max = param[4],
                u_id = None,
                unit_id = un[param[6]].unit_id,
            ))
    for df_dm_name, params in DFPARAMETER_FOR_DM.items():
        for param_i, param in enumerate(params):
            dfp.add(db.DF_Parameter(
                df_id = None,
                mf_id = mf[df_dm_name].mf_id,
                param_i = param_i,
                param_type = param[0],
                idf_type = param[1],
                normalization = param[2], min = param[3], max = param[4],
                u_id = None,
                unit_id = un[param[6]].unit_id,
            ))
    session.add_all(dfp)
    session.commit()


##############################################################################
#####                               main                                 #####
##############################################################################
def mysql_drop(db_name):
    # use `mysql` command to drop database.
    sql = '''DROP DATABASE IF EXISTS {db_name};
    CREATE DATABASE {db_name}
        DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
    USE {db_name};
    '''.format(db_name=db_name)
    subprocess.Popen(
        ['mysql', '-s', '-h', MYSQL_HOST, '-u', MYSQL_USER, '-p' + MYSQL_PASS],
        stdin=subprocess.PIPE,
    ).communicate(input=sql.encode())


def sqlite_drop(db_name):
    file_name = SQLITE_PATH + '/' + db_name[7:] # remove 'sqlite:'
    open(file_name, 'w').close()
    subprocess.Popen(['chmod', '777', file_name]).communicate()


def init(db_name):
    print('Deleting old database ...')
    if db_name.startswith('sqlite:'):
        sqlite_drop(db_name)
    else:
        mysql_drop(db_name)

    print('Creating new database ...')
    db.connect(db_name)
    db.create()

    print('Inserting default values ...')
    session = db.get_session()
    insert_values(session)
    session.close()


if __name__ == '__main__':
    # parse arguments.
    db_name = ''
    quite_mode = False
    for arg in sys.argv[1:]:
        if   arg == '-q': quite_mode = True
        else:             db_name = arg

    if not db_name:
        print(USAGE)
        exit(1)

    if quite_mode:
        init(db_name)
    else:
        ans = input('Are you sure want to reset %s? [Y/n]: ' % db_name)
        if ans.lower() in ('n', 'no'):
            print('db not changed.')
        else:
            init(db_name)
            print('done.')

