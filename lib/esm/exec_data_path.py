
import inspect
import logging

import csmapi

from . import data_path

# idf_data_cache[(mac_addr, df_name, na_id)] = <data>
idf_data_cache = {}


def exec_data_path(path, samples):
    global idf_data_cache 
    '''idf_type - norm - idf_fn - join - scaling - odf_fn - CSM

    data always be a list.

    if path['odf_key'][1] == 'Display':  # odf's feature
        # special case
        # 此 case 是在 join 之前，遇到 Display 時 join function 會被忽略
        # 若無 join，則直接 idf_id 進去，若有 join，則看 join 裡的所有 idf_id
        # p.s. idf_id = (mac_addr, df_name, na_id)
    '''
    log = logging.getLogger(__name__)
    assert(isinstance(path, data_path.DataPath))
    log.debug('{G}exec path to (%s, %s)', path.odf_mac_addr, path.odf_df_name)

    # added by MZ: if samples is empty, then return
    # to decouple exec_data_path from esm_project.py
    if not samples:
        return

    # data is insufficient for variant.
    if len(samples) < 2:
        # Issue: 'sample' does not work on the first sample
        # The previous method: return
        # The new method: duplicate the only element -- proposed by MZ
        # Effect: 'variant' gives a zero when on the arrival of the first sample
        samples.append(samples[0])

    csmapi.dfm_push(path.na_id, path.idf_dfo_id, 'input', samples[0][1])
    # idf_type
    data = [None] * max(len(path.idf_type), len(samples[0][1]))

    if len(samples[0][1]) < len(path.idf_type):
        for i in range(len(path.idf_type) - len(samples[0][1])):  samples[0][1].append(None)

    for i in range(len(path.idf_type)):
        if path.idf_type[i] == 'sample':
            data[i] = samples[0][1][i]
        elif path.idf_type[i] == 'variant':
            if (samples[0][1][i] != None) and (samples[1][1][i] != None):
                data[i] = samples[0][1][i] - samples[1][1][i]
            else: data[i] = 0
        else:
            log.error('UNKNOWN idf_type: %s', path.idf_type)

    if len(samples[0][1]) - len(path.idf_type) > 0:
        for i in range(len(samples[0][1]) - len(path.idf_type)):     
            data[len(path.idf_type)+i] = samples[0][1][len(path.idf_type)+i]
        
    csmapi.dfm_push(path.na_id, path.idf_dfo_id, 'type', data)


    csmapi.dfm_push(path.na_id, path.idf_dfo_id, 'function', data)


    # norm
    if path.idf_norm:
        min_max = csmapi.dfm_pull_min_max(path.na_id, path.idf_dfo_id, 'function')
        for i in range(len(data)):
            if  min_max[i] != None:
                minimun, maximum = min_max[i]
            else:  minimun, maximum = 0, 1
            if minimun == maximum:
                data[i] = 1
            else:
                if type(data[i]) == int or type(data[i]) == float:
                    data[i] = (data[i] - minimun) / (maximum - minimun)
                else: data[i] = 0
        csmapi.dfm_push(path.na_id, path.idf_dfo_id, 'normalization', data)


    # store data into idf_data_cache[(mac_addr, df_name, na_id)]
    idf_data_cache[(path.idf_mac_addr, path.idf_df_name, path.na_id)] = data


    # Display(special case) (this case will quit the routine)
    if path.odf_df_name == 'Display':
        log.debug('Display special case!!')
        rst = {}   # rst[<d_name>] = {<feature>: <data from old_data>}

        # if has join, get from path.join_params, else get only path itself
        if path.join_enable:
            idfs = path.join_params
        else:
            idfs = [(path.idf_mac_addr, path.idf_df_name, path.na_id)]

        for mac_addr, df_name, na_id in idfs:
            d_name = csmapi.pull(mac_addr, 'profile')['d_name']
            if (mac_addr, df_name, na_id) in idf_data_cache:
                cache_data = idf_data_cache[(mac_addr, df_name, na_id)]
                if d_name in rst:
                    rst[d_name][df_name] = cache_data
                else:
                    rst[d_name] = {df_name: cache_data}
        csmapi.push(path.odf_mac_addr, path.odf_df_name, [rst])
        return


    csmapi.dfm_push(path.na_id, path.odf_dfo_id, 'function', data)


    # scaling
    if path.odf_scaling:
        min_max = csmapi.dfm_pull_min_max(path.na_id, path.odf_dfo_id, 'function')
        for i in range(len(data)):
            if min_max[i] != None:             
                from_min, from_max = min_max[i]
            else: from_min, from_max = 0, 1
            to_min, to_max = path.odf_range[i]

            if from_min == from_max:
                norm = 1
            else:
                if type(data[i]) == int or type(data[i]) == float:
                    norm = (data[i] - from_min) / (from_max - from_min)
                else: norm = 0            
            data[i] = norm*(to_max-to_min) + to_min

        csmapi.dfm_push(path.na_id, path.odf_dfo_id, 'scaling', data)


    # send to CSM
    try:
        if path.odf_mac_addr:
            if  data and data[0] != None:
                csmapi.push(path.odf_mac_addr, path.odf_df_name, data)
    except Exception as e:
        if str(e).find('mac_addr not found: SimDev') != -1:
            print('SimDev ODF Error:', e)
        elif str(e).find('df_name not found:') != -1:
            raise Exception('Device "' + path.odf_d_name + '" has inconsistent ODFs with the server: ' + str(e))
        elif str(e).find('mac_addr not found') != -1:
            raise Exception('Device "' + path.odf_d_name + '" offline. ' + str(e))
        else:
            print('Unknow CSM error:', str(e))
