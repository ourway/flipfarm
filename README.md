flipfarm renderfarm management system
====

before installation, remember to disable firewall:

```
sudo ufw disable
```



```
sudo apt-get update
sudo apt-get install redis-server libssl-dev libffi-dev python-dev -y
wget https://bootstrap.pypa.io/get-pip.py
sudo -H /usr/bin/python get-pip.py
rm get-pip.py
cd flipfarm
sudo -H /usr/bin/python -m pip install virtualenv httpie cython
virtualenv .pyenv
source .pyenv/source/activate



```
