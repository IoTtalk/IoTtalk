
from logging.handlers import TimedRotatingFileHandler
import logging
import os.path
import time
import traceback
import datetime

import requests

import db
import csmapi
import ec_config
db.connect(ec_config.DB_NAME)

from . import clogging
from . import create_data_paths
from . import exec_data_path


# name will be fixed after get p_id in _main()
LOG_FILE = os.path.join(ec_config.LOG_PATH, 'p%s.log')
LOGLEVEL = logging.DEBUG


def main(p_id, u_id, lock=None):

    init_logger(p_id)
    log = logging.getLogger(__name__)

    while True:
        try:
            _main(p_id, u_id, lock)

        except csmapi.CSMError:
            exception = traceback.format_exc()
            log.warning(exception)
            time.sleep(1)
            continue

        except:
            exception = traceback.format_exc()
            session = db.get_session()
            prj = session.query(db.Project).filter(db.Project.p_id==p_id).first()
            prj.exception = exception
            prj.status = 'off'
            session.commit()
            session.close()
            log.error(exception)
            break


def init_logger(p_id):
    global LOG_FILE
    LOG_FILE = LOG_FILE % p_id

    # logger for p%s.log
    logger_esm_project = logging.getLogger(__name__)
    logger_esm_init = logging.getLogger(create_data_paths.__name__)
    logger_esm_exec = logging.getLogger(exec_data_path.__name__)

    hd = TimedRotatingFileHandler(LOG_FILE, when='midnight', backupCount=3)
    hd.setLevel(LOGLEVEL)
    hd.setFormatter(clogging.get_default_formatter())
    logger_esm_project.addHandler(hd)
    logger_esm_init.addHandler(hd)
    logger_esm_exec.addHandler(hd)


def isDataEarlyThanStart(startTime, dataTime):
    try:
        if '.' not in dataTime: dataTime = dataTime + '.000000'
        dataTime = datetime.datetime.strptime(dataTime, '%Y-%m-%d %H:%M:%S.%f')
    except ValueError as e:
        print('Wrong time format:', e)
        return False

    if startTime > dataTime:
        print ('ESM startTime:', startTime, '; dataTime:', dataTime, '; DataTime is early than ESM startTime. Ignore.')
        return True
    else: return False
   

def _main(p_id, u_id, lock=None):
    log = logging.getLogger(__name__)

    # init
    session = db.get_session()
    data_paths = create_data_paths.create_data_paths(session, p_id, u_id, lock)
    session.close()

    # init all_idfs.  all_idfs[(mac_addr, df_name)] = timestamp
    all_idfs = {}
    for path in data_paths:
        all_idfs[(path.idf_mac_addr, path.idf_df_name)] = None

    log.info('start project_na with p_id = %s', p_id)

    startTime =  datetime.datetime.now()
    # main loop.
    while True:
        remove_idfs = []
        for idf, last_modified_time in all_idfs.items():
 
            samples = None
            try:
                samples = csmapi.pull(idf[0], idf[1])
            except Exception as e: 
                if str(e).find('mac_addr not found: SimDev') != -1:
                    remove_idfs.append(idf)
                elif str(e).find('df_name not found:') != -1:
                    raise Exception('Device "' + path.idf_d_name + '" has inconsistent IDFs with the server: ' + str(e))
                elif str(e).find('mac_addr not found') != -1:
                    raise Exception('Device "' + path.idf_d_name + '" offline. ' + str(e))
                else:
                    print('Unknow CSM error:\n', str(e))
                    time.sleep(1)

            if not samples: continue

            # if has new data
            if samples[0][0] != last_modified_time:
                # update timestamp
                all_idfs[idf] = samples[0][0]

                if isDataEarlyThanStart(startTime, samples[0][0]): continue

                log.debug('{LB}has new data %s', idf)
                for path in data_paths:
                    if (path.idf_mac_addr, path.idf_df_name) == idf:
                        exec_data_path.exec_data_path(path, samples)

        for remove_idf in remove_idfs:
            all_idfs.pop(remove_idf, None)
            print('Remove non-existent Simulated Device:', remove_idf[0])

        time.sleep(ec_config.ESM_EXEC_DATA_PATH_RATE)

