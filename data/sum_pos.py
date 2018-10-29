#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path, listdir
import re
import json
from operator import itemgetter


data_path = path.dirname(__file__)
lock_path = path.join(data_path, 'lock', 'char')
pos_path = path.join(data_path, 'char-pos')
new_counts = {}
changes = {}
page_users = {}


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


def callback_sum_work(num, fn, filename, text, rows):
    users = set()
    for i in range(max(len(rows) // 4, 1)):
        user = rows[1 + i * 4]
        if user and user not in users:
            users.add(user)
    page_users[fn] = (len(users), '\t'.join(list(users)))


def scan_pos_files(num, src_path, callback):
    for fn in listdir(src_path):
        filename = path.join(src_path, fn)
        if path.isdir(filename):
            num = scan_pos_files(num, filename, callback)
        elif fn.endswith('.json'):
            with open(filename) as f:
                p = json.load(f)
            if callback(num, filename, p):
                num += 1
    return num


def callback_sum_new_box(num, filename, p):
    chars = [c for c in p['chars'] if re.match(r'^new', c['char_id'])]
    if chars:
        new_counts[p['imgname']] = len(chars)
        return True


def callback_sum_changed_box(num, filename, p):
    chars = [c for c in p['chars'] if c.get('changed')]
    if chars:
        changes[p['imgname']] = len(chars)
        return True


if __name__ == '__main__':
    lines = []
    scan_pos_files(0, pos_path, callback_sum_new_box)
    new_counts = sorted(new_counts.items(), key=itemgetter(1), reverse=True)
    for i, (n, c) in enumerate(new_counts):
        s = '%d\t%s\t%s\t%d' % (i + 1, n[:2], n[3:], c)
        print(s)
        lines.append(s)
    with open('new_box.txt', 'w') as f:
        f.write('\n'.join(lines))

    lines = []
    scan_pos_files(0, pos_path, callback_sum_changed_box)
    changes = sorted(changes.items(), key=itemgetter(1), reverse=True)
    for i, (n, c) in enumerate(changes):
        s = '%d\t%s\t%s\t%d' % (i + 1, n[:2], n[3:], c)
        print(s)
        lines.append(s)
    with open('changed_box.txt', 'w') as f:
        f.write('\n'.join(lines))

    lines = []
    scan_lock_files(callback_sum_work)
    page_users = sorted(page_users.items(), key=itemgetter(1), reverse=True)
    new_counts, changes = dict(new_counts), dict(changes)
    for i, (n, (c, s)) in enumerate(page_users):
        s = '%d\t%s\t%s\t%d\t%d\t%d\t%s' % (
            i + 1, n[:2], n[3:], c, new_counts.get(n, 0), changes.get(n, 0), s)
        print(s)
        lines.append(s)
    with open('work.txt', 'w') as f:
        f.write('\n'.join(lines))
