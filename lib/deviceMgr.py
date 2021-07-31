import time
import csmapi 
#import db, ec_config

def query_binding_devices(db):
    session = db.get_session()
    bindingDevices = (session.query(db.Device.mac_addr, db.Device.d_name, db.DeviceModel.dm_name,  db.Device.dm_id, db.Device.d_id)
                      .select_from(db.Device)
                      .join(db.DeviceModel)
                      .join(db.DeviceObject)
                      .filter(db.DeviceObject.d_id == db.Device.d_id)
                      .all()
                     )
    boundDevices=[]
    isDone =[]
    for device in bindingDevices:
        if (device[0].find('SimDev') != -1) or (device[0] in isDone): continue
        isDone.append(device[0])

        aDevice = [device[0], device[1],device[2]]
        df_list=[]
        DFresult = (session.query(db.DeviceFeature.df_name)
                     .select_from(db.DeviceFeature)
                     .join(db.DM_DF)
                     .filter(db.DM_DF.dm_id == device[3])
                     .all()
                   )
        for df in DFresult: df_list.append(df[0])

        aDevice.append(df_list)
        aDevice.append(device[4])
        boundDevices.append(aDevice)
    session.close()
    return boundDevices

#   deviceList = [mac_addr, d_name, dm_name, df_list, d_id]
def restore_device(db, deviceList):
    session = db.get_session()
    for device in deviceList:
        profile = {
            'd_name' : device[1],
            'dm_name': device[2],
            'df_list': device[3],
        }

        for attempt in range(30):
            try:
                csmapi.register(device[0], profile)

                selectedDFs = []
                seledDFs = (session.query(db.DeviceFeature.df_name)
                                .select_from(db.DeviceFeature)
                                .join(db.DFObject)
                                .join(db.DeviceObject)
                                .filter(db.DeviceObject.d_id == device[4])
                                .all()
                              )
                for df in seledDFs: selectedDFs.append(df[0])

                DF_STATUS = ['0' for _ in range(len(device[3]))]
                for df in selectedDFs:
                    try:
                        df_index = device[3].index(df)
                    except ValueError:    
                        print('Feature not found: "{}"'.format(df))
                    else:            
                        DF_STATUS[df_index] = '1'
                DF_STATUS = ''.join(DF_STATUS)        

                Command = ['SET_DF_STATUS',{'cmd_params':[DF_STATUS]}]
                csmapi.push(device[0], '__Ctl_O__', Command)

            except Exception as e:
                print(e)
                time.sleep(1)
                continue
            else: break
    session.close()               
    print('\033[1;31;40mRestore binding devices.\033[0m')

def flush_device_table(db):
    session = db.get_session()
    session.query(db.Device).filter().delete()
    session.commit()
    session.close()
    print('\033[1;31;40mFlush device table successfully.\033[0m')


def fluash_unbound_devices_in_device_table(db, boundDevices):
    boundDeviceList = []
    for device in boundDevices:
        boundDeviceList.append(device[0])

    session = db.get_session()
    device_table = (session.query(db.Device).all())

    for device in device_table:
        if (device.mac_addr.find('SimDev') == -1) and (device.mac_addr not in boundDeviceList): 
            session.query(db.Device).filter(db.Device.mac_addr == device.mac_addr).delete()
    session.commit()
    session.close()
    print('\033[1;31;40mRemove unbound devices in device table successfully.\033[0m')


if __name__ == '__main__':
    db.connect(ec_config.DB_NAME)
    BindingDevices = query_binding_devices(db)
    #print(BindingDevices)
    #fluash_unbound_devices_in_device_table(db, BindingDevices)
    restore_device(db, BindingDevices)
    #flush_device_table(db)

