#!/usr/bin/env python
# -*- coding: utf-8 -*-

from controller.base import load_json, save_json, get_date_time, BaseHandler
import logging
from os import path, listdir, remove
import json
import random
import time

BASE_DIR = path.dirname(path.dirname(__file__))
kinds = dict(GL='高丽藏', JX='嘉兴藏', QL='乾隆藏', YB='永乐北藏')


class MainHandler(BaseHandler):
    URL = r'/'

    def get(self):
        index = load_json(path.join('static', 'index.json'))
        self.render('index.html', kinds=kinds, index=index, pos='char')


class PagesHandler(BaseHandler):
    URL = r'/(block|column|char)/([A-Z]{2}|me)/?'

    def get(self, pos, kind):
        def get_icon(p):
            return path.join('icon', *p.split('_')[:-1], p + '.jpg')

        pos_type = '字切分' if pos == 'char' else '栏切分' if pos == 'block' else '列切分'
        me = '\n' + (self.current_user or self.get_ip()) + '\n'
        self.unlock_timeout(pos, me)

        if kind == 'me':
            pages = []
            lock_path = path.join(BASE_DIR, 'data', 'lock', pos)
            for fn in listdir(lock_path):
                filename = path.join(lock_path, fn)
                if '_' in fn and '.' not in fn:
                    with open(filename) as f:
                        text = f.read()
                    if me in text:
                        pages.append(fn)
            pages.sort()
            return self.render('pages.html', kinds=kinds, pages=pages, count=len(pages),
                               pos_type=pos_type, pos=pos, kind=kind, get_icon=get_icon)

        index = load_json(path.join('static', 'index.json'))
        pages, count = self.pick_pages(pos, index[kind], 12)
        self.render('pages.html', kinds=kinds, pages=pages, count=count,
                    pos_type=pos_type, pos=pos, kind=kind, get_icon=get_icon)

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


class CutProofHandler(BaseHandler):
    URL = r'/(block|column|char)/([A-Z]{2})/(\w{4,20})'

    def get(self, pos, kind, name):
        def get_img(p):
            return path.join('img', *p.split('_')[:-1], p + '.jpg')

        name = kind + '_' + name
        filename = path.join(BASE_DIR, 'static', 'char-pos', *name.split('_')[:-1], name + '.json')
        page = load_json(filename)
        if not page:
            return self.write('error:{0} 页面不存在'.format(name))
        page[pos + 's'] = json.dumps(page[pos + 's'])

        lock_file = PagesHandler.get_lock_file(pos, name)
        if path.exists(lock_file):
            with open(lock_file) as f:
                text = f.read()
                if text and self.get_ip() not in text:
                    return self.write('error:别人已锁定了本页面，请返回选择其他页面。')
        if not path.exists(lock_file):
            with open(lock_file, 'w') as f:
                f.write('\n'.join([self.get_ip(), self.current_user, get_date_time()]))
        self.render('char_cut.html' if pos == 'char' else 'block_cut.html',
                    pos_type='字切分' if pos == 'char' else '栏切分' if pos == 'block' else '列切分',
                    page=page, pos=pos, kind=kind, **page, get_img=get_img)

    def post(self, pos, kind, name):
        filename = path.join(BASE_DIR, 'static', 'char-pos', *name.split('_')[:-1], name + '.json')
        page = load_json(filename)
        submit = self.get_body_argument('submit') == 'true'
        boxes = json.loads(self.get_body_argument('boxes'))
        assert isinstance(boxes, list)
        if page[pos + 's'] != boxes:
            page[pos + 's'] = boxes
            save_json(page, filename)
            logging.info('%d boxes saved: %s' % (len(boxes), name))

        lock_file = PagesHandler.get_lock_file(pos, name)
        with open(lock_file, 'w') as f:
            f.write('\n'.join([self.get_ip(), self.current_user, get_date_time(), 'saved']))

        if submit:
            pages = PagesHandler.pick_pages(pos, load_json(path.join('static', 'index.json'))[kind], 1)[0]
            self.write('jump:' + pages[0][3:] if pages else 'error:本类切分已全部校对完成。')
        self.write('')
