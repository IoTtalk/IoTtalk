#!/bin/sh
cd $(dirname $0)
cd ../
ProjectPath=$(pwd)
ProjectName=$(echo $ProjectPath | tr "/" "\n" | tail -n 1)

export PYTHONPATH="$PYTHONPATH:$ProjectPath/lib"

if [ ! -d $ProjectPath/sqlite ]; then
    mkdir $ProjectPath/sqlite
fi

$ProjectPath/bin/initdb.py sqlite:ec_db.db -q

# restarting easyconnect ...
#ps  | grep SCREEN | grep easyconnect | awk '{print $2}' | xargs kill 2> /dev/null
#sleep 1
#~/easyconnect/setup/startup.sh
