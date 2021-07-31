import os.path
IS_DEBUG = True

EASYCONNECT_ROOT_PATH = os.path.join(os.path.dirname(__file__), '..')

SQLITE_PATH = os.path.join(EASYCONNECT_ROOT_PATH, 'sqlite')
MYSQL_HOST = ''
MYSQL_USER = ''
MYSQL_PASS = ''

DB_NAME = 'sqlite:ec_db.db'

LOG_PATH = os.path.join(EASYCONNECT_ROOT_PATH, 'log')

CCM_HOST = '0.0.0.0'
CCM_PORT = 7788

CSM_HOST = '0.0.0.0'
CSM_PORT = 9999
CSM_DEBUG = True
CSM_SAMPLE_THRESHOLD = 3      # number of samples to keep in dfm_logs.
CSM_PULL_SAMPLE_LEN = 2

ESM_EXEC_DATA_PATH_RATE = 0.1   # sec
ESM_UMOUNT_ALL_ON_START = False
ESM_CSM_PASS = None
DEVICE_AUTH = False

BROADCAST_IF = 'eth0'
AUTO_DETECT_BROADCAST_IF = False
BROADCAST_PORT = 17000

WEB_DA_DIR_PATH = os.path.join(EASYCONNECT_ROOT_PATH, 'da')

MDB_ACCOUNT = 'iottalk'
MDB_KEY = 'zysomentionsuroppostreye'
MDB_PASS = '917cd9025d2b18056cd0d61657f65fc372e33d25'
MDB_TABLE_FEATURE = 'device_feature'

manager_auth_required = False 
cyber_auth_required   = False
users = {
    "iottalk": "2016",
}

projectMgrUsers = {
    "iottalk": "2019",
}

daUsers = {
    "demo": "demo"
}
