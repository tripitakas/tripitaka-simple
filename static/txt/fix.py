#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path, listdir
import json
import re


def scan_dir(txt_path):
    for fn in listdir(txt_path):
        filename = path.join(txt_path, fn)
        if path.isdir(filename):
            scan_dir(filename)
        elif fn.endswith('.txt'):
            with open(filename) as f:
                old = text = f.read()
            if text.startswith('"'):
                text = json.loads(text)
            text = re.sub(r'\S*<!--.+-->\S*', '\n', text, flags=re.S)
            if old != text:
                with open(filename, 'w') as f:
                    f.write(text)
                    print(filename)

scan_dir(path.dirname(__file__))
