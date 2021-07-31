"""Python binding for CSM API."""
import ec_config
ENDPOINT = 'http://localhost:{}'.format(ec_config.CSM_PORT)

import requests

# example
profile = {
    'd_name': 'D1',
    'dm_name': 'MorSensor',
    'u_name': 'yb',
    'df_list': ['Acceleration', 'Temperature'],
}
mac_addr = 'C860008BD249'
#csmapi.register(csmapi.mac_addr, csmapi.profile)
#register(mac_addr, profile)

f = open("passwd", "r")
ec_config.ESM_CSM_PASS = f.read()
f.close()

TIMEOUT=10
IoTtalk = requests.Session()

class CSMError(Exception):
    pass


def register(mac_addr, profile):
    r = IoTtalk.post(
        ENDPOINT + '/' + mac_addr,
        json = {'profile': profile}, timeout=TIMEOUT
    )
    if r.status_code != 200: raise CSMError(r.text)
    else: passwordKey = r.json().get('password')
    return True

def deregister(mac_addr):
    r = IoTtalk.delete(ENDPOINT + '/' + mac_addr, timeout=TIMEOUT)
    if r.status_code != 200: raise CSMError(r.text)
    return True

import time
def push(mac_addr, df_name, data):
    def df_put(mac_addr, df_name, data):
        r = IoTtalk.put(
            ENDPOINT + '/' + mac_addr + '/' + df_name,
            json = {'data': data},
            timeout=TIMEOUT,
            headers = {'password-key': ec_config.ESM_CSM_PASS}
        )
        return r

    retry_counter = 0
    while True:
        r = df_put(mac_addr, df_name, data)
        if r.status_code == 200: 
            return True
        if r.status_code == 502: 
            print('Cannot connect to CSM. Retry push() after 1 second.')
        else:
            if 'df_name not found:' in r.text:
                retry_counter+=1
                print('df_name not found, retry counter:', retry_counter)
                if retry_counter > 10:
                    print('df_name not found, retry 10 times and all failed.')
                    raise CSMError(r.text)
            else:
                raise CSMError(r.text)
        time.sleep(1)    

def pull(mac_addr, df_name):
    def df_get(mac_addr, df_name):
        r = IoTtalk.get(ENDPOINT + '/' + mac_addr + '/' + df_name,
            timeout=TIMEOUT,
            headers = {'password-key': ec_config.ESM_CSM_PASS}
        )
        return r

    retry_counter = 0
    while True:
        r = df_get(mac_addr, df_name)
        if r.status_code == 200: 
            return r.json()['samples']
        if r.status_code == 502:
            print('Error 502: Cannot connect to CSM. pull() pass.')
            return []
        if 'df_name not found:' in r.text:
            retry_counter+=1
            print('df_name not found, retry counter:', retry_counter)
            if retry_counter > 10:
                print('df_name not found, retry 10 times and all failed.')
                raise CSMError(r.text)
        else:
            raise CSMError(r.text)

        time.sleep(1)


def tree():
    r = IoTtalk.get(ENDPOINT + '/tree', timeout=TIMEOUT)
    if r.status_code != 200: raise CSMError(r.text)
    return r.json()

def get_alias(mac_addr, df_name):
    r = IoTtalk.get(ENDPOINT + '/get_alias/' + mac_addr + '/' + df_name, timeout=TIMEOUT)
    if r.status_code != 200: raise CSMError(r.text)
    return r.json()['alias_name']

##### DF-module part #####
# dfo_id == 0 means join
# 不是我喜歡用 + 來串字串，是因為這樣寫某人比較好理解。
def dfm_push(na_id, dfo_id, stage, data):
    def dfm_put(na_id, dfo_id, stage, data):
        r = IoTtalk.put(
            ENDPOINT + '/dfm/' + str(na_id) + '/' + str(dfo_id) + '/' + stage,
            json = {'data': data},
            timeout=TIMEOUT
        )
        return r

    while True:
        r = dfm_put(na_id, dfo_id, stage, data)
        if r.status_code == 200: return True
        if r.status_code != 502: raise CSMError(r.text)
        print('Cannot connect to CSM. Retry dfm_push() after 1 second.')
        time.sleep(1)
        

def dfm_pull(na_id, dfo_id, stage):
    r = IoTtalk.get(
        ENDPOINT + '/dfm/' + str(na_id) + '/' + str(dfo_id) + '/' + stage, timeout=TIMEOUT
    )
    if r.status_code != 200:
        if r.status_code == 502:
            print('Error 502: Cannot connect to CSM . dfm_pull() pass.')
            return []
        raise CSMError(r.text)
    return r.json()['samples']

def dfm_push_min_max(na_id, dfo_id, stage, min_max):
    r = IoTtalk.put(
        ENDPOINT + '/dfm/' + str(na_id) + '/' + str(dfo_id) + '/' + stage + '/min_max',
        json = {'min_max': min_max},
        timeout=TIMEOUT
    )
    if r.status_code != 200: raise CSMError(r.text)
    return True

def dfm_pull_min_max(na_id, dfo_id, stage):
    r = IoTtalk.get(
        ENDPOINT + '/dfm/' + str(na_id) + '/' + str(dfo_id) + '/' + stage + '/min_max', timeout=TIMEOUT
    )
    if r.status_code != 200: raise CSMError(r.text)
    return r.json()['min_max']

def dfm_reset(na_id, dfo_id):
    r = IoTtalk.delete(
        ENDPOINT + '/dfm/' + str(na_id) + '/' + str(dfo_id),
        timeout=TIMEOUT
    )
    if r.status_code != 200: raise CSMError(r.text)
    return True

def dfm_reset_all():
    r = IoTtalk.delete(
        ENDPOINT + '/dfm/',
        timeout=TIMEOUT
    )
    if r.status_code != 200: raise CSMError(r.text)
    return True
