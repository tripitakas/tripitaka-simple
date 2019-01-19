#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@desc: 比较文字校对结果
@file: cmp_pos.py
@time: 2019/1/19
"""
from controller.base import BaseHandler
from os import listdir, path, remove
import json
import re
from operator import itemgetter

pos_path = path.join(path.dirname(path.dirname(__file__)), 'static', 'pos')


class CmpTxtPosHandler(BaseHandler):
    URL = r'/cmp_txt_pos/([A-Z]{2})'

    def get(self, kind):
        result = cmp_pos_txt(kind + '1', kind, self.get_query_argument('rm', 0))
        self.render('cmp_txt_pos.html', kind=kind, changes=result['changes'])


def cmp_page(page1, page2, result):
    changes = []
    if len(page1['chars']) != len(page2['chars']):
        changes.append('字框个数不同: %d != %d' % (len(page1['chars']), len(page2['chars'])))
    count = min(len(page1['chars']), len(page2['chars']))
    chars1 = sorted(page1['chars'], key=itemgetter('char_id'))[:count]
    chars2 = sorted(page2['chars'], key=itemgetter('char_id'))[:count]
    for i, (c1, c2) in enumerate(zip(chars1, chars2)):
        if c1['char_id'] != c2['char_id']:
            changes.append('字框编号不同: %d, %s != %s' % (i, c1['char_id'], c2['char_id']))
        elif c1.get('txt') != c2.get('txt'):
            if len(c2.get('txt', '')) > 1:
                code = int(re.sub(r'^U', '', c2['txt']), 16)
                c2['txt'] = chr(code)
            changes.append('字框文字不同: %s, %s != %s' % (c1['char_id'], c1.get('txt'), c2.get('txt')))
    if changes:
        result['changes'].append(dict(name=page1['imgname'], changes=changes))


def cmp_pages(path1, path2, result, rm_tmp):
    if not path.exists(path1):
        return
    for fn in listdir(path1):
        filename1 = path.join(path1, fn)
        filename2 = path.join(path2, fn)
        if not path.exists(filename2):
            continue
        if path.isdir(filename1):
            cmp_pages(filename1, filename2, result, rm_tmp)
        elif fn.endswith('.json'):
            filename_ = filename2 + '~'
            if path.exists(filename_):
                cmp_page(json.load(open(filename1)), json.load(open(filename_)), result)
                if rm_tmp:
                    remove(filename_)
            else:
                cmp_page(json.load(open(filename1)), json.load(open(filename2)), result)


def cmp_pos_txt(kind1, kind2, rm_tmp=True):
    result = dict(kind1=kind1, kind2=kind2, changes=[])
    cmp_pages(path.join(pos_path, 'proof', kind1), path.join(pos_path, 'proof', kind2), result, rm_tmp)
    return result


if __name__ == '__main__':
    with open(path.join(pos_path, 'cmp.json'), 'w') as f:
        json.dump(cmp_pos_txt('YB1', 'YB'), f, ensure_ascii=False)
