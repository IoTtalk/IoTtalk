## System Environment
- Ubuntu 16.04 or 18.04


## System Requirement
- Python 3.5.1 +
- (optional) MySQL server

IoTtalk needs ports `80`, `5566`, `7788`, `8000`, and `9999`, make sure that the ports are not in use.  

## Setup IoTtalk
1) Update system packages  
```
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y autoremove
```


2) Install dependent system packages  
```
sudo apt-get -y install screen python3 python3-pip libsqlite3-dev libssl-dev openssl
sudo apt-get install mailutils
```


3) Enter to directory where your IoTtalk server located in  


4) Install and update dependent python3 packages  
```
sudo -H pip3 install --upgrade pip
sudo -H pip3 install setuptools
sudo -H pip3 install -r requirements.txt
sudo -H pip3 install --upgrade requests
```

5) Start up the server  
```
sudo -H ./setup/startup.sh
```




## Auto start IoTtalk  at reboot
Because some command in `setup/startup.sh` need root privilege, you need `sudo crontab -e` to edit root's crontab.  
Add one line at the end:
```
@reboot /YourPathToIoTtalk/setup/startup.sh
```
Replace _YourPathToIoTtalk_ with your path to IoTtalk 1.0. Below is an example
```
@reboot /home/iottalk/iottalk_server_1.0/setup/startup.sh
```




## Setup IoTtalk  in isolated Python environments
Use [virtualenv](https://virtualenv.pypa.io/en/stable/) in order to do so.  
The setup flow just like above. The difference is:
- Install and setup virtualenv **before** installing python packages
- Edit `setup/startup.sh` just one line to use python3 interpreter in virtualenv


To install and setup virtualenv
1. Install virtualenv : `pip3 install virtualenv` or `sudo -H pip3 install virtualenv`
2. Create new virtualenv : `virtualenv ~/iottalk-python-venv`
3. Activate the isolated enviroment : `. ~/iottalk-python-venv/bin/activate`


Now, you can install and update python3 package in isolated enviroment.  
Make sure that you install python package **without sudo**, or your python package will still be installed outside virtualenv:
```
pip3 install -r requirements.txt
pip3 install --upgrade requests
```


To make all commands both with or without `sudo` in `setup/startup.sh` use the isolated enviroment, you have to edit one line in `setup/startup.sh`.  
Change line 3 from
```
python3="python3"
```
to
```
python3="/YourPathToVirtualenv/bin/python3"
```
Replace _YourPathToVirtualenv_ with your path to virtualenv. Below is an example
```
python3="/home/iottalk/iottalk-python-venv/bin/python3"
```


Now, you can run `sudo -H ./setup/startup.sh` even without activate the virualenv.