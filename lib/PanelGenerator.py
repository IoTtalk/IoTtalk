import csmapi
import ec_config
import re

Keypad_html = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
#Panting_html = [0,0,0]
# Color_html = 0
Color_html = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
Button_html = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
Switch_html = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
PPT_Control_html = 0
Knob_html = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
is_empty = 0

def htmlQueue(DF_name):
    global Keypad_html, Color_html, Button_html, Switch_html, PPT_Control_html, Knob_html
    if DF_name == 'PPT_Control':
        PPT_Control_html = 1
    # elif DF_name == 'Color-I':
    #     Color_html = 1
    elif DF_name.strip(re.search(r'\d+$', DF_name).group(0))  == 'Color-I':
        Color_html[int(re.search(r'\d+$', DF_name).group(0))-1] = 1
    elif DF_name.strip(re.search(r'\d+$', DF_name).group(0))  == 'Keypad':
        Keypad_html[int(re.search(r'\d+$', DF_name).group(0))-1] = 1
    elif DF_name.strip(re.search(r'\d+$', DF_name).group(0)) == 'Button':
        #print ('Button:  ~~  ', int(DF_name[len(DF_name)-1:]))
        Button_html[int(re.search(r'\d+$', DF_name).group(0))-1] = 1
    elif DF_name.strip(re.search(r'\d+$', DF_name).group(0)) == 'Switch':
        #print ('Switch:  ~~  ', int(DF_name[len(DF_name)-1:]))
        Switch_html[int(re.search(r'\d+$', DF_name).group(0))-1] = 1
    elif DF_name.strip(re.search(r'\d+$', DF_name).group(0)) == 'Knob':
        Knob_html[int(re.search(r'\d+$', DF_name).group(0))-1] = 1
    else:
        print ('DF_name not found.')

def PanelGen():
    global Keypad_html, Color_html, Button_html, Switch_html, PPT_Control_html, Knob_html, is_empty
    Keypad_html = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    #Panting_html = [0,0,0]
    # Color_html = 0
    Color_html = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    Button_html = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    Switch_html = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    PPT_Control_html = 0
    Knob_html = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    is_empty = 0

    html = open ('./da/Remote_control/index.html','w')

    try:
        DF_list = (csmapi.pull('IoTtalk_Control_Panel', 'profile'))['df_list']
        Command = (csmapi.pull('IoTtalk_Control_Panel', '__Ctl_O__'))
    except Exception:
        print ('No Panel Registration.')
        html.write('No Panel Registration.')
    else:    
        print ('DF_list', DF_list)
        if Command != []:
            DF_STATUS =  list(Command[0][1][1]['cmd_params'][0])
            print ('DF_STATUS: ', DF_STATUS)
        else:
            print ('Command is NULL.')
            DF_STATUS = []
            is_empty = 1

        index=0
        for STATUS in DF_STATUS:
            if STATUS == '1':
                #print ('DF: ',DF_list[index])
                htmlQueue(DF_list[index])
            #print ('index: ', index)
            index=index+1
        htmlGenerator(html)
    html.close()
    return 200

def alias_name(DF_name):
    try:
        return csmapi.get_alias('IoTtalk_Control_Panel',DF_name)[0]
    except:
        return DF_name

def get_switch_state(DF_name):
    try:
        return csmapi.pull('IoTtalk_Control_Panel',DF_name)[0][1][0]
    except:
        return []

def htmlGenerator(file):
    file.write('''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Control Panel</title>
    <!-- <script src="include/mobilecheck.js"></script> -->
    <link rel="stylesheet" href="style.css">
    <script src="jquery.min.js"></script>

    <link rel="stylesheet" href="include/knob/knobKnob.css">
    <script src="include/knob/transform.js"></script>
    <script src="include/knob/knobKnob.jquery.js"></script>

    <script src="main.js"></script>
   </head>
  <body>
<TD style="FONT-SIZE: 13px; COLOR:#000000; LINE-HIGHT:50px; FONT-FAMILY:Arial,Helvetica,sans-serif">\n\n''')


    if is_empty:
        file.write('''
    <legend>Please select Remote_control in the IoTtalk GUI!</legend>
        ''')
        return 0



    idx=0
    if 1 in Keypad_html:
        for idx in range (0,64):
            if Keypad_html[idx] == 1:

                DF_alias = alias_name('Keypad'+ str(idx+1))
                
                file.write('    <legend>'+ DF_alias +'</legend>\n')
                file.write('''    <button onclick="push('Keypad{NUM}',1)">1</button>
    <button onclick="push('Keypad{NUM}',2)">2</button>
    <button onclick="push('Keypad{NUM}',3)">3</button> <br>
    <button onclick="push('Keypad{NUM}',4)">4</button>
    <button onclick="push('Keypad{NUM}',5)">5</button>
    <button onclick="push('Keypad{NUM}',6)">6</button> <br>
    <button onclick="push('Keypad{NUM}',7)">7</button>
    <button onclick="push('Keypad{NUM}',8)">8</button>
    <button onclick="push('Keypad{NUM}',9)">9</button> <br>
    <button onclick="push('Keypad{NUM}',10)">*</button>
    <button onclick="push('Keypad{NUM}',0)">0</button>
    <button onclick="push('Keypad{NUM}',11)">#</button>  <br> <br>\n\n'''.format(NUM=str(idx+1)))

    # if Color_html == 1:
        
    #     DF_alias = alias_name('Color-I')

    #     file.write('    <legend>'+ DF_alias  +'</legend>')
    #     file.write('''
    # <button onclick="push('Color-I',[255,0,0])" style="width:100px; height:100px; background-color:#FF0000"></button>
    # <button onclick="push('Color-I',[255,85,17])" style="width:100px; height:100px; background-color:#FF5511 "></button>
    # <button onclick="push('Color-I',[255,255,0])" style="width:100px; height:100px; background-color:#FFFF00"></button> <br>
    # <button onclick="push('Color-I',[0,255,0])" style="width:100px; height:100px; background-color:#00FF00"></button>
    # <button onclick="push('Color-I',[0,0,255])" style="width:100px; height:100px; background-color:#0000FF"></button>
    # <button onclick="push('Color-I',[102,0,255])" style="width:100px; height:100px; background-color:#6600FF"></button> <br>
    # <button onclick="push('Color-I',[255,0,255])" style="width:100px; height:100px; background-color:#FF00FF"></button>
    # <button onclick="push('Color-I',[255,255,255])" style="width:100px; height:100px; background-color:#FFFFFF"></button>
    # <button onclick="push('Color-I',[0,0,0])" style="width:100px; height:100px; background-color:#000000"></button> <br><br> \n\n''')

    idx=0
    if 1 in Color_html:
        for idx in range (0,64):
            if Color_html[idx] == 1:

                DF_alias = alias_name('Color-I'+ str(idx+1))
                file.write('    <legend>'+ DF_alias  +'</legend>')
                file.write('''
    <button onclick="push('Color-I{NUM}',[255,0,0])" style="width:100px; height:100px; background-color:#FF0000"></button>
    <button onclick="push('Color-I{NUM}',[255,85,17])" style="width:100px; height:100px; background-color:#FF5511 "></button>
    <button onclick="push('Color-I{NUM}',[255,255,0])" style="width:100px; height:100px; background-color:#FFFF00"></button> <br>
    <button onclick="push('Color-I{NUM}',[0,255,0])" style="width:100px; height:100px; background-color:#00FF00"></button>
    <button onclick="push('Color-I{NUM}',[0,0,255])" style="width:100px; height:100px; background-color:#0000FF"></button>
    <button onclick="push('Color-I{NUM}',[102,0,255])" style="width:100px; height:100px; background-color:#6600FF"></button> <br>
    <button onclick="push('Color-I{NUM}',[255,0,255])" style="width:100px; height:100px; background-color:#FF00FF"></button>
    <button onclick="push('Color-I{NUM}',[255,255,255])" style="width:100px; height:100px; background-color:#FFFFFF"></button>
    <button onclick="push('Color-I{NUM}',[0,0,0])" style="width:100px; height:100px; background-color:#000000"></button> <br><br> \n\n'''.format(NUM=str(idx+1)))
    '''
    if 1 in Panting_html:
        file.write('    <legend>Painting</legend>\n')
        for idx in range (0,3):
            if Panting_html[idx] == 1:
                if idx == 0:
                    file.write('    <button onclick="push(\'Red\',1)" style="width:100px; height:100px; background-color:red"></button>\n')
                elif idx == 1:
                    file.write('    <button onclick="push(\'Green\', 2)" style="width:100px; height:100px; background-color:green"></button>\n')
                elif idx == 2:
                    file.write('    <button onclick="push(\'Blue\',3)" style="width:100px; height:100px; background-color:blue"></button>\n')
        file.write('    <br><br> \n\n')
    '''
        
    idx=0
    if 1 in Button_html:
        file.write('    <legend>Button</legend>\n')
        for idx in range (0,64):
            if Button_html[idx] == 1:

                DF_alias = alias_name('Button'+ str(idx+1))

                button_text = '    <button onclick="push(\'Button' + str(idx+1) + '\',' + str(idx+1) + ')" style="width:200px;" >'+ DF_alias + '</button> <br>\n'
                file.write(button_text)
        file.write('    <br>\n\n')

    idx=0
    if 1 in Switch_html:
        file.write('    <legend>Switch</legend>\n')
        for idx in range (0,64):
            if Switch_html[idx] == 1:

                DF_alias = alias_name('Switch'+ str(idx+1))
                switch_text = '    <span>'+DF_alias+'</span>\n'
                state = get_switch_state('Switch'+str(idx+1))

                if state != [] and state > 0 :
                    switch_text += '    <div id="Switch' + str(idx+1) + '" class="toggle-button toggle-button-selected">\n' 
                else:
                    switch_text += '    <div id="Switch' + str(idx+1) + '" class="toggle-button">\n'
                
                switch_text += '        <button></button>\n' + '    </div>\n    <br>\n\n'
                file.write(switch_text)
        file.write('    <br>\n\n')
        

    if PPT_Control_html == 1:
         file.write('''
    <legend>Power Point Panel</legend>
    <button onclick="push('PPT_Control','F5')" style="width:50px;">S</button>
    <button onclick="push('PPT_Control','up_arrow')" style="width:50px;">&uarr;</button>
    <button onclick="push('PPT_Control','esc')"  style="width:50px;">E</button> <br>
    <button onclick="push('PPT_Control','left_arrow')"  style="width:50px;">&larr;</button>
    <button onclick="push('PPT_Control','down_arrow')"  style="width:50px;">&darr;</button>
    <button onclick="push('PPT_Control','right_arrow')"  style="width:50px;">&rarr;</button> <br><br>\n\n''')


    if 1 in Knob_html:
        #file.write('    <legend>Knob</legend>\n')
        for i in range(0,64):
            if Knob_html[i] == 1:

                DF_alias = alias_name('Knob'+ str(i+1))

                file.write('    <legend>'+ DF_alias +'</legend>\n')
                file.write("    <div style='margin-top:-33px; margin-bottom:15px;'  type='text' role='Knob%d' class='knob-container'></div>\n\n" % (i+1))
        file.write('    <br>\n\n')

    file.write('  </body>\n</html>')
