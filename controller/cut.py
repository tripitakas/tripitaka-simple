#!/usr/bin/env python
# -*- coding: utf-8 -*-

from controller.base import load_json, save_json, get_date_time, BaseHandler
import logging
from os import path, listdir, remove
import json
import random
import time

BASE_DIR = path.dirname(path.dirname(__file__))
kinds = {
    'block': {'JX': '嘉兴藏'},
    'column': {'JX': '嘉兴藏'},
    'char': {'GL': '高丽藏', 'JX': '嘉兴藏', 'QL': '乾隆藏', 'YB': '永乐北藏'}
}

class MainHandler(BaseHandler):
    URL = r'/'

    def get(self):
        index = load_json(path.join('static', 'index.json'))
        self.render('index.html', kinds=kinds, index=index, pos='char')


class PagesHandler(BaseHandler):
    URL = [r'/(block|column|char)/([A-Z]{2}|me)/?',
           r'/(block|column|char)/(me)/(\w+)']

    @staticmethod
    def get_my_pages(pos, username):
        pages = []
        me = '\n' + username + '\n'
        lock_path = path.join(BASE_DIR, 'data', 'lock', pos)
        for fn in listdir(lock_path):
            filename = path.join(lock_path, fn)
            if '_' in fn and '.' not in fn:
                with open(filename) as f:
                    text = f.read()
                if me in text and fn not in pages:
                    pages.append(fn)
        return sorted(pages)

    def get(self, pos, kind, username=None):
        def get_icon(p):
            return '/'.join(['icon', *p.split('_')[:-1], p + '.jpg'])

        def get_info(p):
            filename = path.join(BASE_DIR, 'static', 'pos', pos, *p.split('_')[:-1], p + '.json')
            return load_json(filename)

        pos_type = '切字' if pos == 'char' else '切栏' if pos == 'block' else '切列'
        cur_user = self.current_user or self.get_ip()
        username = username or cur_user
        me = '\n' + username + '\n'
        self.unlock_timeout(pos, me)

        if kind == 'me':
            pages = self.get_my_pages(pos, username)
            return self.render('my_pages.html', kinds=kinds, pages=pages, count=len(pages), username=username,
                               pos_type=pos_type, pos=pos, kind=kind, get_icon=get_icon, get_info=get_info)

        index = load_json(path.join('static', 'index.json'))
        pages, count = self.pick_pages(pos, index[pos][kind], 12)
        html = 'block_pages.html' if pos == 'block' else 'char_pages.html'
        if pos != 'char':
            [CutHandler.lock_page(self, pos, name) for name in pages]

        self.render(html, kinds=kinds, pages=pages, count=count, username=username,
                    pos_type=pos_type, pos=pos, kind=kind, get_icon=get_icon, get_info=get_info)

    @staticmethod
    def unlock_timeout(pos, me):
        lock_path = path.join(BASE_DIR, 'data', 'lock', pos)
        now = time.time()
        for fn in listdir(lock_path):
            filename = path.join(lock_path, fn)
            if '_' in fn and '.' not in fn:
                with open(filename) as f:
                    text = f.read()
                if 'saved' not in text:
                    t = path.getctime(filename)
                    if now - t > 60 * 30 or me in text:
                        remove(filename)
                        logging.warning('%s unlocked: %s' % (fn, text.replace('\n', '|')))

    @staticmethod
    def get_lock_file(pos, name):
        return path.join(BASE_DIR, 'data', 'lock', pos, name)

    @staticmethod
    def pick_pages(pos, pages, count):
        pages = [p for p in pages if not path.exists(PagesHandler.get_lock_file(pos, p))]
        random.shuffle(pages)
        return sorted(pages[:count]), len(pages)


class CutHandler(BaseHandler):
    URL = r'/(block|column|char)/([A-Z]{2})/(\w{4,20}|all)'

    def get(self, pos, kind, name):
        def get_img(p):
            return '/'.join(['img', *p.split('_')[:-1], p + '.jpg'])

        name = kind + '_' + name
        filename = path.join(BASE_DIR, 'static', 'pos', pos, *name.split('_')[:-1], name + '.json')
        page = load_json(filename)
        if not page:
            return self.write('error: {0} 页面不存在'.format(name))
        if pos + 's' in page:
            page[pos + 's'] = json.dumps(page[pos + 's'])
        else:
            page[pos + 's'] = []

        if self.lock_page(self, pos, name) != name:
            return
        self.render('char_cut.html' if pos == 'char' else 'block_cut.html',
                    pos_type='切字' if pos == 'char' else '切栏' if pos == 'block' else '切列',
                    page=page, pos=pos, kind=kind, **page, get_img=get_img)

    @staticmethod
    def lock_page(self, pos, name, fail_write=True):
        lock_file = PagesHandler.get_lock_file(pos, name)
        if path.exists(lock_file):
            with open(lock_file) as f:
                text = f.read()
                if text and self.get_ip() not in text and (self.current_user or '匿名') not in text \
                        and 'saved' not in text:
                    return fail_write and self.write('error:别人已锁定了本页面，请返回选择其他页面。')
        if not path.exists(lock_file):
            with open(lock_file, 'w') as f:
                f.write('\n'.join([self.get_ip(), self.current_user, get_date_time()]))
        return name

    def post(self, pos, kind, name):
        """
        保存一个或多个页面的切分校对数据.
        保存一个页面时 name 为页名，请求体中需要有 boxes 框数组. 保存多个页面时 name 为空，请求体的 boxes 为[页,框数组]的数组.
        如果在请求体中指定了 submit 属性，则会输出下一个校对任务的页名（jump:name 格式，无藏别）.
        :param pos: 校对类型，block 为栏切分，column 为列切分，char 为字框切分
        :param kind: 藏别，例如 GL、JX
        :param name: 页名，例如 GL_1047_1_5，请求体中需要有 boxes 框数组. 如果页名为空，则 boxes 为[[name,boxes], ...]数组
        :return: None
        """
        submit = self.get_body_argument('submit', 0) == 'true'
        boxes = json.loads(self.get_body_argument('boxes'))
        assert name or type(boxes) == dict
        if name=='all':
            for name, arr in boxes:
                self.save(kind, pos, name, arr)
        else:
            self.save(kind, pos, name, boxes)

        if submit:
            pages = PagesHandler.pick_pages(pos, load_json(path.join('static', 'index.json'))[pos][kind], 1)[0]
            self.write('jump:' + pages[0][3:] if pages else 'error:本类切分已全部校对完成。')
        self.write('')

    def save(self, kind, pos, name, boxes):
        filename = path.join(BASE_DIR, 'static', 'pos', pos, *name.split('_')[:-1], name + '.json')
        page = load_json(filename)
        assert page and isinstance(boxes, list)
        if page[pos + 's'] != boxes:
            page[pos + 's'] = boxes
            save_json(page, filename)
            logging.info('%d boxes saved: %s' % (len(boxes), name))

        lock_file = PagesHandler.get_lock_file(pos, name)
        text = []
        if path.exists(lock_file):
            with open(lock_file) as f:
                text = f.read()
                if 'saved' in text:
                    text = text.split('\n')
                else:
                    text = []
        with open(lock_file, 'w') as f:
            text += [self.get_ip(), self.current_user, get_date_time(), 'saved']
            f.write('\n'.join(text))
