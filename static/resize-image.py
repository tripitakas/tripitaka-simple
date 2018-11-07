#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os import path, mkdir
from PIL import Image
from glob import glob
import json


def export_icon(filename, dst_dir, fn, size):
    dst_file = path.join(dst_dir, fn[0: fn.rindex('.')] + '.jpg')
    try:
        im = Image.open(filename)
        w0, h0 = w, h = im.size
    except Exception as e:
        print('%s error: %s' % (str(e), fn))
        return

    if w > size:
        h = round(size * h / w)
        w = size
    if h > size:
        w = round(size * w / h)
        h = size
    if w0 == w and h0 == h:
        return

    try:
        im.thumbnail((w, h), Image.ANTIALIAS)
        im.save(dst_file, 'JPEG')
        print('%s\t%d x %d' % (dst_file, w, h))
        return True
    except Exception as e:
        print('%s error: %s' % (str(e), fn))


def export_icons(img_dir, icon_dir):
    if not path.exists(icon_dir):
        mkdir(icon_dir)
    for fn in os.listdir(img_dir):
        filename = path.join(img_dir, fn)
        if path.isdir(filename):
            export_icons(filename, path.join(icon_dir, fn))
        if '.jpg' in fn:
            export_icon(filename, icon_dir, fn, 450)


def check_json(json_dir):
    for filename in glob(path.join(json_dir, '*.json')):
        try:
            with open(filename) as f:
                old = f.read()
            text = old.replace(']"blocks": [', ', ')
            if text != old:
                with open(filename, 'w') as f:
                    f.write(text)
            p = json.loads(text)
            assert 'blocks' in p, filename + ' no block'
        except Exception as e:
            print('%s error: %s' % (str(e), filename))


def set_char_img_size(img_dir, json_dir):
    for fn in os.listdir(json_dir):
        json_file = os.path.join(json_dir, fn)
        img_file = os.path.join(img_dir, fn[:-3] + 'jpg')
        if fn.endswith('.cut') and os.path.exists(img_file):
            with open(json_file) as f:
                info = json.load(f)
            im = Image.open(img_file)
            w, h = im.size
            info['imgsize'] = dict(width=w, height=h)
            with open(json_file, 'w') as f:
                json.dump(info, f, ensure_ascii=False)


if __name__ == "__main__":
    base_dir = path.dirname(__file__)
    # check_json(path.join(base_dir, 'block_pos'))
    export_icons(path.join(base_dir, 'img'), path.join(base_dir, 'icon'))
    # set_char_img_size(path.join(base_dir, 'img'), path.join(base_dir, 'char_pos'))
