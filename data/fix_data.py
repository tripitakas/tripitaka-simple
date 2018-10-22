#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path, listdir, remove
import re

data_path = path.dirname(__file__)
lock_path = path.join(data_path, 'lock', 'char')
log_file = path.join(data_path, '..', 'log', 'app.log')


def clean_log():
    if path.exists(log_file):
        with open(log_file) as f:
            rows = f.readlines()
        rows = [r for r in rows if not re.search(r'\.(jpg|js|css)\?v=|Up\?Ip=', r)]
        with open(log_file, 'w') as f:
            f.writelines(rows)


def scan_lock_files(callback):
    num = 0
    for fn in listdir(lock_path):
        filename = path.join(lock_path, fn)
        if '.' not in fn and '_' in fn:
            with open(filename) as f:
                text = f.read()
                rows = text.split('\n')
            if callback(num, fn, filename, text, rows):
                num += 1
        else:
            remove(filename)


def callback_get_ip_users(num, fn, filename, text, rows):
    if 'saved' not in text:
        remove(filename)
    elif rows[1]:
        ip_user[rows[0]] = rows[1]
        return True


def callback_anonymous(num, fn, filename, text, rows):
    if not rows[1]:
        if rows[0] in ip_user:
            rows[1] = ip_user[rows[0]]
            print(num + 1, fn, rows[0] + '->' + rows[1])
            if 1:
                with open(filename, 'w') as f:
                    f.write('\n'.join(rows))
            return True
        else:
            print(fn, rows[0])
    # remove(filename)


ip_user = {}
scan_lock_files(callback_get_ip_users)
scan_lock_files(callback_anonymous)
clean_log()
