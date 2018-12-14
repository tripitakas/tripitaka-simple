#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path, listdir
import time


def scan_dir(src_dir):
    for fn in listdir(src_dir):
        filename = path.join(src_dir, fn)
        if path.isdir(filename):
            scan_dir(filename)
        elif fn[0] not in '._':
            ts = get_modify_time(filename)
            lines.append('%s\t%s\t%s' % (src_dir, fn, ts))


def timestamp_to_str(timestamp):
    ts = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', ts)


def get_modify_time(filename):
    t = path.getmtime(filename)
    return timestamp_to_str(t)


if __name__ == "__main__":
    lines = []
    scan_dir('static')
    with open('files.txt', 'w') as f:
        f.write('\n'.join(lines))
