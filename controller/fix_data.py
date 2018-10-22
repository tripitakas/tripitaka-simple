#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path, listdir
import re
from operator import itemgetter
from controller.base import BaseHandler


data_path = path.join(path.dirname(path.dirname(__file__)), 'data')
lock_path = path.join(data_path, 'lock', 'char')
log_file = path.join(data_path, '..', 'log', 'app.log')
ip_user = {}
work = {}


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


def callback_get_ip_users(num, fn, filename, text, rows):
    if 'saved' in text and rows[1]:
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
            print(fn, rows[0], '?')


def callback_sum_work(num, fn, filename, text, rows):
    if rows[1]:
        work[rows[1]] = work.get(rows[1], 0) + 1


def fix():
    work.clear()
    scan_lock_files(callback_get_ip_users)
    scan_lock_files(callback_anonymous)
    scan_lock_files(callback_sum_work)
    return [(u, c) for u, c in sorted(work.items(), key=itemgetter(1), reverse=True)]


class RankingHandler(BaseHandler):
    URL = r'/ranking'

    def get(self):
        ranking = fix()
        items = ['<li><a href="/char/me/{0}">{0}</a> {1}</li>'.format(n, c) for n, c in ranking]
        self.write('<h3>校对排行榜</h3><ol>%s</ol>' % ''.join(items))


if __name__ == '__main__':
    print(fix())
    clean_log()
