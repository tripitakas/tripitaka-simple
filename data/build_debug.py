#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from os import path, listdir, mkdir
import re
import json
import shutil
from operator import itemgetter


base_path = path.dirname(path.dirname(__file__))
max_per_type = 5
indexes = {}
names = []


def scan_files(src_path, dst_path, data, ext, count, level):
    items = data
    for fn in sorted(listdir(src_path)):
        # level=0时，fn为char、block等；level=1时，fn为JX等藏别
        if level <= (1 if 'json' in ext else 0):
            count = 0
        if count >= max_per_type or fn[0] == '.':
            continue
        if level == 0:
            items = data[fn] = data.get(fn, {})
        elif 'json' in ext and level == 1:
            items = data[fn] = data.get(fn, [])

        filename = path.join(src_path, fn)
        dst_file = path.join(dst_path, fn)
        name = re.sub(r'\..+$', '', fn)
        if path.isdir(filename):
            if not path.exists(dst_path):
                mkdir(dst_path)
            if not path.exists(dst_file):
                mkdir(dst_file)
            count += scan_files(filename, dst_file, items, ext, count, level + 1)
        elif fn.endswith(ext):
            if fn.endswith('.json'):
                if name not in items and path.exists(re.sub(r'pos/[a-z]+/', 'img/', filename).replace('.json', '.jpg')):
                    items.append(name)
                    names.append(name)
                    shutil.copy(filename, dst_file)
                    count += 1
            elif name not in items and name in names:
                shutil.copy(filename, dst_file)
                count += 1
    return count


scan_files(path.join(base_path, 'static.tmp/pos'),
           path.join(base_path, 'static/pos'), indexes, '.json', 0, 0)
scan_files(path.join(base_path, 'static.tmp/txt'),
           path.join(base_path, 'static/txt'), indexes, '.txt', 0, 0)
scan_files(path.join(base_path, 'static.tmp/img'),
           path.join(base_path, 'static/img'), indexes, '.jpg', 0, 0)
open(path.join(base_path, 'static/index.json'), 'w').write(json.dumps(indexes, ensure_ascii=False))
