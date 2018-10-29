#!/bin/sh
cd `dirname $0`
rm -fr lock char-pos
scp -r sm@47.95.216.233:/home/sm/cut_proof/data/lock ./lock
scp -r sm@47.95.216.233:/home/sm/cut_proof/static/char-pos ./char-pos
# sshpass -p password scp -r ...
python sum_pos.py
