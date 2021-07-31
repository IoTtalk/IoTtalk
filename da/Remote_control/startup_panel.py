import time
import requests
import register

while True:
    try:
        profile = {
            'd_name': 'Controller',
            'dm_name': 'Remote_control',
            'u_name': 'yb',
            'df_list': [],
        }
        for i in range(1,26):
            profile['df_list'].append("Keypad%d" % i)
            profile['df_list'].append("Button%d" % i)
            profile['df_list'].append("Switch%d" % i)
            profile['df_list'].append("Knob%d" % i)
            profile['df_list'].append("Color-I%d" % i)


        result = None

        try:
            r = register.pull('IoTtalk_Control_Panel', 'profile')
        except Exception as e:
            print(e)
            if str(e).find('mac_addr not found:') != -1:
                print('Register Remote Control...')
                result = register.register('IoTtalk_Control_Panel', profile)
            else: 
                print('Device maybe existed with unknown password.')
                break    
        else: 
            print('Device is existed with unknown password.')
            break

        if result: 
            passwd_file = open(r'./da/Remote_control/passwd_remote_control', 'w+')
            passwd_file.write(result[1])
            passwd_file.close()
            break
           
    except requests.exceptions.ConnectionError as e:
        print('requests.exceptions.ConnectionError:', e)
        print('retry after 3 second')
        time.sleep(3)
    except register.CSMError as e:
        print('csmapi.CSMError:', e)
        print('retry after 3 second')
        time.sleep(3)

print('Remote_control registration is done.' )
