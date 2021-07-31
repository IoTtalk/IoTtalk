
import csmapi
from json import loads as json_loads
from json import dumps as json_dumps

def read_data(mac_addr, df_name):
    return csmapi.pull(mac_addr, df_name)

def write_data(mac_addr, df_name, data):
    return csmapi.push(mac_addr, df_name, data)
