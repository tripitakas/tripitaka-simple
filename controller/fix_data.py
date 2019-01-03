#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path, listdir, mkdir
import re
from operator import itemgetter
from controller.base import BaseHandler, load_json, save_json


data_path = path.join(path.dirname(path.dirname(__file__)), 'data')
static_path = path.join(path.dirname(path.dirname(__file__)), 'static')
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


def scan_lock_files(callback, in_path):
    num = 0
    if not path.exists(in_path):
        return
    for fn in listdir(in_path):
        filename = path.join(in_path, fn)
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
    n = 0
    for i in range(len(rows) // 4):
        user = rows[1 + i * 4]
        if not user:
            if rows[0 + i * 4] in ip_user:
                user = ip_user[rows[0 + i * 4]]
                print(num + 1, fn, rows[0 + i * 4] + '->' + user)
                n += 1
            else:
                print(fn, rows[0 + i * 4], '?')
    if n > 0:
        with open(filename, 'w') as f:
            f.write('\n'.join(rows))
        return True


def callback_sum_work(num, fn, filename, text, rows):
    users = set()
    for i in range(max(len(rows) // 4, 1)):
        user = rows[1 + i * 4]
        if user and user not in users:
            users.add(user)
            work[user] = work.get(user, 0) + 1


def fix(in_path):
    work.clear()
    scan_lock_files(callback_get_ip_users, in_path)
    scan_lock_files(callback_anonymous, in_path)
    scan_lock_files(callback_sum_work, in_path)
    return [(u, c) for u, c in sorted(work.items(), key=itemgetter(1), reverse=True)]


class RankingHandler(BaseHandler):
    URL = r'/ranking/(block|column|char|proof)'

    def get(self, pos):
        ranking = fix(path.join(data_path, 'lock', pos))
        items = ['<li><a href="/{2}/me/{0}">{0}</a> {1}</li>'.format(n, c, pos) for n, c in ranking]
        self.write('<h3>校对排行榜</h3><ol>%s</ol>' % ''.join(items))



class HistoryHandler(BaseHandler):
    URL = r'/(block|column|char|proof)/(h\d?)/([A-Za-z0-9-_ ]*)'

    def get(self, pos, h, name):
        def callback_get(num, fn, filename, text, rows):
            if name in fn:
                pairs = []
                users = set()
                for i in range(max(len(rows) // 4, 1)):
                    user = rows[1 + i * 4] or rows[i * 4]
                    if user and user not in users:
                        users.add(user)
                        pairs.append((user, rows[2 + i * 4][5:19]))
                items.append((fn, ''.join(['<span>{0} <small>{1}</small></span>'.format(n, t) for n, t in pairs]),
                              pairs and pairs[0][1]))

        items = []
        name = name[:2].upper() + re.sub(r'-|\s', '_', name[2:])
        scan_lock_files(callback_get, path.join(data_path, 'lock', pos + h[1:]))
        items.sort(key=itemgetter(2))
        items = ['<li><a href="/{2}/{3}/{4}">{0}</a> {1}</li>'.format(f, s, pos, f[:2], f[3:]) for f, s, t in items]
        css = 'li>a{display: inline-block; min-width: 120px; margin-right: 10px; text-decoration: none}'
        self.write('<style>%s</style><h3>页面校对历史 (%d 个页面)</h3><ol>%s</ol>' % (css, len(items), ''.join(items)))


class HelpHandler(BaseHandler):
    URL = r'/proofread/help'

    def get(self):
        self.render('proofread-help.html')


def merge_chars(dst_path, char_path, column_path):
    for fn in listdir(dst_path):
        dst_file = path.join(dst_path, fn)
        if path.isdir(dst_file):
            merge_chars(dst_file, char_path, column_path)
        elif fn.endswith('.json'):
            char = load_json(path.join(char_path, fn))
            column = load_json(path.join(column_path, fn))
            assert char and column
            assert char.get('blocks')
            assert char.get('chars')
            assert column.get('columns')

            assert len(char['blocks']) == len(column['blocks']) and len(char['blocks']) == 1
            for i, (a, b) in enumerate(zip(char['blocks'], column['blocks'])):
                if not(a['x'] == b['x'] and a['y'] == b['y'] and a['w'] == b['w'] and a['h'] == b['h']):
                    print('\t'.join([fn, str(i + 1), str(a), str(b)]))
                    char['blocks'][i].update(dict(x=b['x'], y=b['y'], w=b['w'], h=b['h'], changed=True))

            char['columns'] = sorted(column['columns'], key=itemgetter('x'), reverse=True)
            for i, c in enumerate(char['columns']):
                c['no'] = c['column_id'] = 'b1c%d' % (i + 1)
            save_json(char, dst_file)


def merge_columns(dst_path, char_path):
    indexes = load_json(path.join(static_path, 'index.json'))
    indexes['column'] = {}
    for fn in listdir(char_path):
        src_file = path.join(char_path, fn)
        if fn.endswith('.json') and fn[:2] in ['GL', 'QL', 'YB']:
            dst_file = dst_path
            for folder in fn.split('_')[:-1]:
                dst_file = path.join(dst_file, folder)
                if not path.exists(dst_file):
                    mkdir(dst_file)
            dst_file = path.join(dst_file, fn)
            column = load_json(src_file)
            assert column and column.get('columns')
            save_json(column, dst_file)
            indexes['column'][fn[:2]] = indexes['column'].get(fn[:2], []) + [fn[:-5]]
    save_json(indexes, path.join(static_path, 'index.json'))


if __name__ == '__main__':
    # print(fix(path.join(data_path, 'lock', 'char')))
    # clean_log()
    if 0:
        merge_columns(path.join(static_path, 'pos/column/'),
                      path.join(static_path, 'pos/column/char-cut'))
