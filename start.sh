#!/bin/sh
cd `dirname $0`
[[ -d log ]] || mkdir log
sudo pkill -f 'python app.py --port=80'
find . -name "*.pyc" | sudo xargs rm -rf
sudo nohup python app.py --port=80 >> log/app.log 2>&1 &
