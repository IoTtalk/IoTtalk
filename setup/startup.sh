#!/bin/sh

python3="python3"

cd $(dirname $0)
cd ../
ProjectPath=$(pwd)
ProjectName=$(echo $ProjectPath | tr "/" "\n" | tail -n 1)
echo "ProjectPath: $ProjectPath"
echo "ProjectName: $ProjectName"

cd $ProjectPath

export PYTHONPATH="$PYTHONPATH:$ProjectPath/lib"
LOG=$ProjectPath/log/startup.log
if [ ! -d $ProjectPath/log ]; then
    mkdir $ProjectPath/log
fi
if [ ! -d $ProjectPath/sqlite ]; then
    mkdir $ProjectPath/sqlite
fi
if [ ! -f $ProjectPath/sqlite/ec_db.db ]; then
    ./setup/reset_db.sh
fi

echo --------------------------------------- >> $LOG
date >> $LOG
echo --------------------------------------- >> $LOG

myIP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*'| grep -v '127.0.0.1')

screen -dmS $ProjectName >> $LOG 2>&1
add_to_screen() {
    TITLE=$1
    CMD=$2
    screen -S $ProjectName -X screen -t "$TITLE" bash -c \
        "\
        while [ 1 ]; do \
            $CMD; echo ========== restart ==========; sleep 1; \
        done"
}

# wait for screen.
while [ 1 ]; do
    ps aux | grep -v grep | grep SCREEN | grep $ProjectName > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        break
    fi
    sleep 1
done


add_to_screen CSM "./bin/csm $python3" 
#add_to_screen CSM "sudo uwsgi ./lib/wsgi_csm.ini"
echo "Sleep 20 seconds for waitting CSM bootup."

sleep 20

add_to_screen CCM "./bin/ccm $python3" 
#add_to_screen CCM "sudo uwsgi ./lib/ccm/wsgi_ccm.ini"
add_to_screen ESM "./bin/esm $python3" 
add_to_screen WEB "sudo $python3 ./da/web.py" 

$python3 ./da/Remote_control/startup_panel.py


#echo "Waiting for CHT Pirius booting. (2 mintues.)"
#sleep 120
#add_to_screen CHT "nodejs ./da/IoTtalk-CHT-master/index.js" >> $LOG 2>&1

