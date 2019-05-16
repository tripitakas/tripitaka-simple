#!/bin/sh
cd `dirname $0`
sudo pkill -f 'python3 app.py'
find . -name "*.pyc" | sudo xargs rm -rf
sudo nohup python3 app.py --port=80 --debug=0 >> log/app.log 2>&1 &
