#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path, listdir, mkdir
import os
import time
import json
import shutil

DST_DIR = '/Users/zhangyg/Desktop/cut_proof/static/'
SRC_DIR = '/Users/zhangyg/Desktop/py/cut-local/static'
UPLOAD = '/Users/zhangyg/Desktop/cut_proof/upd'
changes = dict(add=[], upd=[])


def merge_files(src_dir, dst_dir):
    if not path.exists(dst_dir):
        mkdir(dst_dir)
    for fn in listdir(src_dir):
        if fn[0] in '._' or fn in ['css', 'fonts', 'images', 'img', 'js'] or fn.endswith('.py'):
            continue
        filename = path.join(src_dir, fn)
        dst_file = path.join(dst_dir, fn)
        if path.isdir(filename):
            merge_files(filename, dst_file)
        else:
            modify_time = get_modify_time(filename)
            mt = os.stat(filename)
            if not path.exists(dst_file):
                changes['add'].append('%s\t%s\t%s' % (src_dir, fn, 'add'))
                shutil.copy(filename, dst_file)
                os.utime(dst_file, (mt.st_atime, mt.st_mtime))
            elif modify_time > get_modify_time(dst_file):
                s = '%s\t%s\tupd\t%s\t%s' % (src_dir, fn, get_modify_time(dst_file), modify_time)
                changes['upd'].append(s)
                shutil.copy(filename, dst_file)
                os.utime(dst_file, (mt.st_atime, mt.st_mtime))


def cmp_files(src_dir, dst_dir, srv):
    if not path.exists(dst_dir):
        mkdir(dst_dir)
    for fn in listdir(src_dir):
        if fn[0] in '._' or fn in ['css', 'fonts', 'images', 'icon', 'icons', 'img0', 'js'] or\
                fn.endswith('.py') or fn.endswith('.js') or fn.endswith('.ico') or fn.startswith('index'):
            continue
        filename = path.join(src_dir, fn)
        dst_file = path.join(dst_dir, fn)
        if path.isdir(filename):
            cmp_files(filename, dst_file, srv)
        else:
            srv_file = filename.replace(DST_DIR, '')
            srv_kind = '/'.join(srv_file.split('/')[:2])
            srv_time = srv.get(srv_file)
            modify_time = get_modify_time(filename)
            mt = os.stat(filename)
            if not srv_time:
                changes['add'].append('%s\t%s\t%s' % (srv_kind, srv_file, modify_time))
            elif modify_time > srv_time:
                s = '%s\t%s\t%s\t%s' % (srv_kind, srv_file, srv_time, modify_time)
                changes['upd'].append(s)
            else:
                continue
            shutil.copy(filename, dst_file)
            os.utime(dst_file, (mt.st_atime, mt.st_mtime))


# 'char-pos/JX/165/7/JX_165_7_39.json: 2018-12-14 12:20:36
def build_server_files(lines):
    lines = [s.strip().split('\t') for s in lines]
    return {p + '/' + fn: tm for p, fn, tm in lines}


def timestamp_to_str(timestamp):
    ts = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', ts)


def get_modify_time(filename):
    t = path.getmtime(filename)
    return timestamp_to_str(t)


def save_diff(arr, filename):
    with open(filename, 'w') as f:
        f.write('\n'.join(arr))
    counts = {}
    for f in arr:
        f = f.split('\t')[0]
        counts[f] = counts.get(f, 0) + 1
    print(counts)


def gen_task():
    lines = [s.strip().split(' ') for s in open('140.txt').readlines()]
    users = {}
    for r in lines:
        users[r[1]] = users.get(r[1], []) + [r[0]]
    print(list(users.keys()))
    with open('fix_tasks.json', 'w') as f:
        json.dump(users, f)


if __name__ == "__main__":
    gen_task()
    # merge_files(SRC_DIR, DST_DIR)
    if 0:
        cmp_files(DST_DIR, UPLOAD, build_server_files(open('files.txt').readlines()))
        print('add: %d, upd: %d' % (len(changes['add']), len(changes['upd'])))
        save_diff(changes['add'], 'add.txt')
        save_diff(changes['upd'], 'upd.txt')
