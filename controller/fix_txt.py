#!/usr/bin/env python
# -*- coding: utf-8 -*-

from controller.base import BaseHandler
from os import path, listdir
import json
import re

messages = []
occurrence = {}
TXT_PATH = path.join(path.dirname(path.dirname(__file__)), 'static', 'txt')


def output(msg):
    messages.append(msg)


def has_json(txt_file):
    json_file = txt_file.replace('/txt/', '/pos/proof/').replace('.txt', '.json')
    return path.exists(json_file)


def scan_dir(txt_path):
    def change(new_text, old_text, tag):
        if new_text != old_text:
            changes.append(tag)
        return new_text

    for fn in listdir(txt_path):
        filename = path.join(txt_path, fn)
        if path.isdir(filename):
            scan_dir(filename)
        elif fn.endswith('.txt') and has_json(filename):
            with open(filename) as f:
                old = text = f.read()
            changes = []
            if text.startswith('"'):
                text = change(json.loads(text), text, 'json')
            text = change(re.sub(r'\s*<!--.+-->\s*\n?', '', text, flags=re.M), text, 'note')
            text = change(re.sub(r'(p|span)\.(p|s)\d[^}\n]+}?\n?', '', text, flags=re.M), text, 'p|span')
            text = change(re.sub(r'\xa0', ' ', text), text, 'a0')
            text = change(re.sub(r'<|>', '', text), text, '<>')
            text = change('\n\n\n'.join(re.sub(r'\n{2}', '\n', b, flags=re.M)
                                        for b in text.split('\n\n\n')), text, 'ln2')
            if fn[:2] == 'GL' and 0:
                text = change(text.replace('爲', '為'), text, '爲->為')
                text = change(text.replace('無', '无'), text, '無->无')
            # text = change(text.replace('庾', '𢈔'), text, '庾->U00022214')
            if old != text:
                with open(filename, 'w') as f:
                    f.write(text)
                    output(path.basename(filename) + ': ' + ', '.join(changes))


def find_especial_chars(chars, txt_path, sub_set=None, pattern=None):
    for fn in listdir(txt_path):
        filename = path.join(txt_path, fn)
        if path.isdir(filename):
            find_especial_chars(chars, filename, sub_set, pattern)
        elif fn.endswith('.txt') and has_json(filename):
            with open(filename) as f:
                text = f.read()
            res = re.findall(pattern or r'[^\u4E00-\u9FA50-9A-MO-Za-z\u3000○,，。?？ \t\n]', text)
            res = set(res)
            if sub_set:
                res &= sub_set
            if res:
                for r in list(res):
                    if r in text:
                        occurrence[r] = occurrence.get(r, set())
                        occurrence[r].add(fn)
                lines = sub_set and [t for t in text.split('\n') if [1 for r in list(res) if r in t]]
                lines = lines and '\t' + lines[0] or ''
                chars |= res
                output(fn + ': ' + ''.join(list(res)) + lines)
    return chars


class FixTextHandler(BaseHandler):
    URL = r'/fix_txt/(.*)'

    def get(self, op):
        del messages[:]
        if op == 'fix':
            scan_dir(TXT_PATH)
            especial_chars = []
        else:
            pattern = None
            if op == 'upper':
                sub_set = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                pattern = r'[^\u4E00-\u9FA50-9a-z\u3000○,，。?？ \t\n]'
            elif op == 'lower':
                sub_set = list('abcdefghijklmnopqrstuvwxyz')
                pattern = r'[^\u4E00-\u9FA50-9A-Z\u3000○,，。?？ \t\n]'
            elif op == 'digit':
                sub_set = list('0123456789')
                pattern = r'[^\u4E00-\u9FA5A-Za-z\u3000○,，。?？ \t\n]'
            elif op == 'sign':
                sub_set = list('`~!@#$%^&*()-_+=:;"\'<,>.?/{[}]|\\')
                pattern = r'[^\u4E00-\u9FA50-9A-Za-z\u3000○。？ \t\n]'
            elif op == 'unknown':
                sub_set = ['N', '*']
            else:
                sub_set = [op] if op else []
                pattern = r'\*' if op == '*' else r'\?' if op == '?' else r'\+' if op == '+' else op
            especial_chars = sorted(list(find_especial_chars(set(), TXT_PATH, set(sub_set), pattern)))
        self.render('text.html', chars=especial_chars, occurrence=occurrence,
                    messages=[s.split('.txt') for s in messages],
                    unicode=lambda c: str(c.encode('unicode-escape'))[3:-1])


if __name__ == '__main__':
    output = print
    scan_dir(TXT_PATH)
