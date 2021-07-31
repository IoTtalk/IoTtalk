import threading, time
import csmapi, SpecialModel
import db as db1
import ec_config
db1.connect(ec_config.DB_NAME)

excluded_dm = SpecialModel.control_channel_excluded_dm 

def get_dm_from_MAC_addr(db, MAC_addr):
    s = db1.get_session()
    dm_name = (s.query(db1.DeviceModel.dm_name)
               .select_from(db1.DeviceModel)
               .join(db1.Device)
               .filter(db1.DeviceModel.dm_id == db1.Device.dm_id)
               .filter(db1.Device.mac_addr == MAC_addr)
               .first())
    s.close()
    if dm_name: return dm_name[0]
    else: return None

def get_MAC_addr_from_d_id(db, d_id):
    s = db1.get_session()
    MAC_addr = (s.query(db1.Device.mac_addr)
                .select_from(db1.Device)
                .filter(db1.Device.d_id == d_id)
                .first())
    s.close()
    if MAC_addr: return MAC_addr[0]
    else: return None

def get_MAC_addr_from_do_id(db, do_id):
    s = db1.get_session()
    MAC_list = (s.query(db1.Device.mac_addr)
                .select_from(db1.Device)
                .join(db1.DeviceObject)
                .filter(db1.Device.d_id == db1.DeviceObject.d_id)
                .filter(db1.DeviceObject.do_id == do_id)
                .first())
    s.close()
    if MAC_list: return MAC_list[0]
    else: return None

def get_do_id_list_from_MAC_addr(db, do_id, MAC_addr):
    s = db1.get_session()
    do_id_list = (s.query(db1.DeviceObject.do_id)
                  .select_from(db1.DeviceObject)
                  .join(db1.Device)
                  .filter(db1.Device.d_id == db1.DeviceObject.d_id)
                  .filter(db1.Device.mac_addr == MAC_addr))
    s.close()
    do_id_list = [column.do_id for column in do_id_list]
    do_id_list.append(do_id) #因為從mac addr中查到的do_id都都是掛載中的，而這個新增的do_id是尚未存在的，所以要額外再加入列表
    return do_id_list

def get_all_MAC_addr_from_p_id(db, p_id):
    s = db1.get_session()
    all_MAC_addr = (s.query(db1.Device.mac_addr)
                    .select_from(db1.Device)
                    .join(db1.DeviceObject)
                    .join(db1.Project)
                    .filter(db1.Device.d_id == db1.DeviceObject.d_id)
                    .filter(db1.DeviceObject.p_id == db1.Project.p_id)
                    .filter(db1.Project.p_id == p_id)
                    .all())
    s.close()
    all_MAC_addr_list = [mac[0] for mac in all_MAC_addr]
    return all_MAC_addr_list

def wait_for_SET_DF_STATUS_RSP(MAC_addr, DF_STATUS, timestamp=None):
    control_channel_timestamp = None
    Command = ['RESUME',{'cmd_params':[]}]
    
    for cycle in range (200):
        try:
            time.sleep(0.2)
            RSP = csmapi.pull(MAC_addr, '__Ctl_I__')
            if  RSP == []:
                #print ( 'threadID:', threading.get_ident(),': No response in cycle:',cycle)
                continue
             
            if control_channel_timestamp == RSP[0][0]: continue
            control_channel_timestamp = RSP[0][0]
            
            if (RSP[0][1][0] != 'SET_DF_STATUS_RSP'): 
                print ('cycle: ',cycle, 'threadID:', threading.get_ident(),': It is not SET_DF_STATUS_RSP, got', RSP[0][1][0])
                continue
     
            if  RSP[0][1][1]['cmd_params'][0] != DF_STATUS:
                print('\033[1;33;44m threadID:', threading.get_ident(), ': Wrong  SET_DF_STATUS_RSP, keep waiting...\033[0m')
                continue
            break
        except Exception as e:
            print('Control Channel error: ', e)
            continue

    if (cycle != 199): print ( '\033[1;33;44m threadID:', threading.get_ident(),'Got SET_DF_STATIS_RSP, then send RESUME command.\033[0m')
    else: print (DF_STATUS, '\033[1;33;44m threadID:', threading.get_ident(), 'Retry 200 times and failed to get SET_DF_STATUS, force send RESUME command.\033[0m')
    csmapi.push(MAC_addr, '__Ctl_O__', Command)


def SET_DF_STATUS(db, do_id, d_id=None):
    
    if d_id == None:
        MAC_addr = get_MAC_addr_from_do_id(db, do_id)
    else:
        MAC_addr = get_MAC_addr_from_d_id(db, d_id)

    if MAC_addr != None:
        do_id_list = get_do_id_list_from_MAC_addr(db, do_id, MAC_addr)
        Device_profile = (csmapi.pull(MAC_addr, 'profile'))
        Real_df_list = Device_profile['df_list']

        if (Device_profile['dm_name'] == 'MorSensor'):
            DF_STATUS = ''
            x=0
            for x in range(len(Real_df_list)):
                DF_STATUS = DF_STATUS + '1'
        else:
            Selected_df_list = []

            '''
            #Only return the selected df_list from the last binded do_od
            Selected_df_list = (session.query(db1.DeviceFeature.df_name)
                               .join(db1.DFObject)
                               .filter(db1.DeviceFeature.df_id == db1.DFObject.df_id)
                               .filter(db1.DFObject.do_id == do_id)
                               )        
            
            '''
            #Return the union of selected df_list from all binded do_id
            s = db1.get_session()
            for do_id in do_id_list:
                Selected_df_list += (s.query(db1.DeviceFeature.df_name)
                                .select_from(db1.DeviceFeature)
                                .join(db1.DFObject)
                                .filter(db1.DeviceFeature.df_id == db1.DFObject.df_id)
                                .filter(db1.DFObject.do_id == do_id))
            s.close()

            DF_STATUS_list = ['0' for x in range(len(Real_df_list))]
            for column in Selected_df_list:
                try:
                    index = Real_df_list.index(column.df_name) #still need to deal with exception, otherwise it will cause crash!
                except ValueError:
                    print('Feature not found: "{}"'.format(column.df_name))
                else:
                    DF_STATUS_list[index] = '1'
            DF_STATUS = ''.join(DF_STATUS_list) 

        Command = ['SET_DF_STATUS',{'cmd_params':[DF_STATUS]}]
        print ('push to __Crl_O__:', Command)
        csmapi.push(MAC_addr, '__Ctl_O__', Command)

        s = db1.get_session()
        prj_status = (s.query(db1.Project.status)
                     .select_from(db1.Project)
                     .join(db1.DeviceObject)
                     .filter(db1.DeviceObject.do_id == do_id)
                     .first())
        s.close()
        if prj_status != None: 
            if prj_status[0] == 'off':
                print ('Project status  == off')
                return 200
            else:
                print ('Project status == on')

                dm_name = get_dm_from_MAC_addr(db, MAC_addr)
                if dm_name not in excluded_dm:
                    threading.Thread(target=wait_for_SET_DF_STATUS_RSP, name='Thd-'+MAC_addr, args=(MAC_addr,DF_STATUS)).start()
                    return 200
                else:
                    print (dm_name, ' cannot handle with RESUME command, no RESUME command.')
        return 200
    print ('MAC_addr is None.')
    return 400

def SUSPEND_device(db, do_id):
    MAC_addr = get_MAC_addr_from_do_id(db, do_id)
    dm_name = get_dm_from_MAC_addr(db, MAC_addr)
    if dm_name not in excluded_dm:
        Command = ['SUSPEND',{'cmd_params':[]}]
        csmapi.push(MAC_addr, '__Ctl_O__', Command)
        print ('SUSPEND_device:', MAC_addr)
    return 200

def SUSPEND(db, p_id):
    all_MAC_addr = get_all_MAC_addr_from_p_id(db, p_id)
    Command = ['SUSPEND',{'cmd_params':[]}]
    for MAC_addr in all_MAC_addr:
        dm_name = get_dm_from_MAC_addr(db, MAC_addr)
        if (dm_name not in excluded_dm):
            csmapi.push(MAC_addr, '__Ctl_O__', Command) 
    print ('SUSPEND all devices', p_id)
    return 200

def RESUME(db, p_id):
    all_MAC_addr = get_all_MAC_addr_from_p_id(db, p_id)
    Command = ['RESUME',{'cmd_params':[]}]
    for MAC_addr in all_MAC_addr:
        dm_name = get_dm_from_MAC_addr(db, MAC_addr)
        if (dm_name not in excluded_dm):
            csmapi.push(MAC_addr, '__Ctl_O__', Command)
    print ('RESUME all devices', p_id)
    return 200
