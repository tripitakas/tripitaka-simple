#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Usage: python data/sum_pos.py [char|column|block|proof]

import sys
from os import path, listdir
import re
import json
from operator import itemgetter


data_path = path.dirname(__file__)
new_counts = {}
changes = {}
page_users = {}


def scan_lock_files(lock_path, callback):
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
        user = rows[1 + i * 4] or rows[0 + i * 4]
        if user and user not in users:
            users.add(user)
    page_users[fn] = (len(users), '\t'.join(list(users)))


def scan_pos_files(pos_type, num, src_path, callback):
    for fn in listdir(src_path):
        filename = path.join(src_path, fn)
        if path.isdir(filename):
            num = scan_pos_files(pos_type, num, filename, callback)
        elif fn.endswith('.json'):
            with open(filename) as f:
                p = json.load(f)
            if callback(pos_type, num, filename, p):
                num += 1
    return num


def callback_sum_new_box(pos_type, num, filename, p):
    items = [c for c in p.get(pos_type + 's', []) if re.match(r'^new', c['char_id'])]
    if items:
        new_counts[p['imgname']] = len(items)
        return True


def callback_sum_changed_box(pos_type, num, filename, p):
    items = [c for c in p.get(pos_type + 's', []) if c.get('changed')]
    if items:
        changes[p['imgname']] = len(items)
        return True


def sum_work(pos_type):
    global new_counts, changes, page_users
    lock_path = path.join(data_path, 'lock', pos_type)
    pos_path = path.join(data_path, '..', 'static', 'pos', pos_type)
    lines = []
    scan_pos_files(pos_type, 0, pos_path, callback_sum_new_box)
    new_counts = sorted(new_counts.items(), key=itemgetter(1), reverse=True)
    for i, (n, c) in enumerate(new_counts):
        s = '%d\t%s\t%s\t%d' % (i + 1, n[:2], n[3:], c)
        print(s)
        lines.append(s)
    with open(pos_type + '_new_box.txt', 'w') as f:
        f.write('\n'.join(lines))

    lines = []
    scan_pos_files(pos_type, 0, pos_path, callback_sum_changed_box)
    changes = sorted(changes.items(), key=itemgetter(1), reverse=True)
    for i, (n, c) in enumerate(changes):
        s = '%d\t%s\t%s\t%d' % (i + 1, n[:2], n[3:], c)
        print(s)
        lines.append(s)
    with open(pos_type + '_changed_box.txt', 'w') as f:
        f.write('\n'.join(lines))

    lines = []
    work = {}
    scan_lock_files(lock_path, callback_sum_work)
    page_users = sorted(page_users.items(), key=itemgetter(1), reverse=True)
    new_counts, changes = dict(new_counts), dict(changes)
    counts = {}
    for i, (n, (c, person)) in enumerate(page_users):
        kind, page, person_count = n[:2], n[3:], c
        s = '%d\t%s\t%s\t%d\t%d\t%d\t%s' % (
            i + 1, kind, page, person_count, new_counts.get(n, 0), changes.get(n, 0), person)
        print(s)
        lines.append(s)
        work[kind] = work.get(kind, {})
        for p in person.split('\t'):
            work[kind][p] = work[kind].get(p, 0) + 1
            counts[p] = counts.get(p, 0) + 1
    with open(pos_type + '_work.txt', 'w') as f:
        f.write('\n'.join(lines))
    with open(pos_type + '_work_count.txt', 'w') as f:
        f.write('校对者\t页数\t%s\n' % '\t'.join(work.keys()))
        counts = sorted(list(counts.items()), key=itemgetter(1), reverse=True)
        for p in counts:
            f.write('%s\t%d\t%s\n' % (p[0], p[1], '\t'.join([str(work[kind].get(p[0], 0)) for kind in work.keys()])))

if __name__ == '__main__':
    sum_work(sys.argv[1] if len(sys.argv) > 1 else 'char')
