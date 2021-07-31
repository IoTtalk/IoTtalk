import pickle
import csmapi 

MAC_addr='IoTtalk_Message'

def MsgNameCount():
    number_of_name = 0
    try:
        Command = (csmapi.pull(MAC_addr, '__Ctl_O__'))
    except Exception:
        print ('No Message Registration.')
    else:
        if Command != []:
            DF_STATUS =  list(Command[0][1][1]['cmd_params'][0])
            print ('DF_STATUS: ', DF_STATUS)
            number_of_name = DF_STATUS.count('1')            
            print ('Number of name = ', number_of_name)
        else:
            print ('Command is NULL.')
            DF_STATUS = []
            number_of_name = 0
    return number_of_name

def SaveMsgContact(msg_json_content):
    pickle.dump(msg_json_content, open( "MsgContact", "wb" ))
    csmapi.push(MAC_addr, '__Ctl_I__', [msg_json_content])

def LoadMsgContact():
    try:
        msg_json_content = pickle.load(open("MsgContact", "rb" ))     
    except Exception:
        msg_json_content = {} 
    return msg_json_content 










