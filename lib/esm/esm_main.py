
import multiprocessing
import time
import os.path
import logging
from logging.handlers import TimedRotatingFileHandler

import db
import ec_config
db.connect(ec_config.DB_NAME)
import csmapi

from . import clogging
from . import esm_project

FileLock = multiprocessing.Lock()

MAIN_LOG_FILE = os.path.join(ec_config.LOG_PATH, 'main.log')
ALL_LOG_FILE = os.path.join(ec_config.LOG_PATH, 'all.log')

SCREEN_LOGLEVEL = logging.INFO
ALL_LOG_LOGLEVEL = logging.DEBUG
MAIN_LOG_LOGLEVEL = logging.DEBUG


# globals
prjs = {}       # prjs[p_id] = {'status': on/off, 'proc': process}


#################### routines ####################
def check_prj_state(session):
    """check all project status."""
    log = logging.getLogger(__name__)
    global prjs

    # check if project is deleted
    p_id_in_db = [i[0] for i in session.query(db.Project.p_id)]
    for p_id in list(prjs.keys()):
        if p_id not in p_id_in_db:
            # the project is deleted
            if prjs[p_id]['proc']:
                prjs[p_id]['proc'].terminate()
                prjs[p_id]['proc'].join()
            log.info('delete esm_project p_id = %s', p_id)
            del prjs[p_id]


    for prj in session.query(db.Project):

        # new project default to off
        if prj.p_id not in prjs:
            prjs[prj.p_id] = {'status': 'off', 'proc': None}
            log.info('New project: %s', prj.p_id)

        # check the project that status changed.
        if prjs[prj.p_id]['status'] != prj.status:
            if prj.status == 'off':         # status changed to off
                prjs[prj.p_id]['proc'].terminate()
                prjs[prj.p_id]['proc'].join()
                prjs[prj.p_id]['proc'] = None
                log.info('kill esm_project p_id = %s', prj.p_id)
            elif prj.status == 'on':        # start a esm_project
                p = multiprocessing.Process(
                    target = esm_project.main,
                    args = (prj.p_id, prj.u_id, FileLock)
                )
                p.start()
                p.name = 'esm_project-{} [{}]'.format(prj.p_id, prj.p_id)
                prjs[prj.p_id]['proc'] = p
                log.info('start esm_project p_id = %s', prj.p_id)
            else:
                log.error('UNKNOWN status = ' + prj.status)
                exit(1)
            prjs[prj.p_id]['status'] = prj.status

        # check the project that need to restart.
        if prj.restart == True:
            # do not need to restart if status==off
            if prj.status == 'on':
                prjs[prj.p_id]['proc'].terminate()
                prjs[prj.p_id]['proc'].join()
                p = multiprocessing.Process(
                    target = esm_project.main,
                    args = (prj.p_id, prj.u_id, FileLock)
                )
                p.start()
                p.name = 'esm_project-{} [{}]'.format(prj.p_id, prj.p_id)
                prjs[prj.p_id]['proc'] = p
                log.info('restart esm_project p_id = %s', prj.p_id)
            prj.restart = False
            session.commit()


#################### main ####################
def init():
    from . import create_data_paths  # init its logger

    # logger init
    logging.getLogger().setLevel(logging.DEBUG)
    logger_root= logging.getLogger()
    logger_esm_main = logging.getLogger(__name__)
    logger_esm_init = logging.getLogger(create_data_paths.__name__)

    # screen logger handler
    hd = logging.StreamHandler()
    hd.setLevel(SCREEN_LOGLEVEL)
    hd.setFormatter(clogging.get_default_formatter())
    logger_root.addHandler(hd)

    # all.log logger handler
    hd = TimedRotatingFileHandler(ALL_LOG_FILE, when='midnight', backupCount=3)
    hd.setLevel(ALL_LOG_LOGLEVEL)
    hd.setFormatter(clogging.get_default_formatter())
    logger_root.addHandler(hd)

    # main.log logger handler
    hd = TimedRotatingFileHandler(MAIN_LOG_FILE, when='midnight', backupCount=3)
    hd.setLevel(MAIN_LOG_LOGLEVEL)
    hd.setFormatter(clogging.get_default_formatter())
    logger_esm_main.addHandler(hd)
    logger_esm_init.addHandler(hd)

    # disable requests log
    logging.getLogger('requests').setLevel(logging.WARNING)


    # DeviceObject unmount, turn off all projects.
    if ec_config.ESM_UMOUNT_ALL_ON_START:
        session = db.get_session()    
        session.query(db.DeviceObject).update({'d_id': None})

        session.query(db.Project).update({'status': 'off'})
        session.commit()
        session.close()

    # clean DF-module in CSM.
    csmapi.dfm_reset_all()


def main():
    log = logging.getLogger(__name__)

    # reset prjs
    global prjs
    prjs = {}

    log.info('started')

    # main loop
    while True:

        # main things
        session = db.get_session()
        check_prj_state(session)
        session.close()

        time.sleep(1)

