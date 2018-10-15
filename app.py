#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from os import path, listdir
import json

BASE_DIR = path.dirname(__file__)


def load_json(filename):
    if path.exists(filename):
        try:
            with open(filename) as f:
                return json.load(f)
        except Exception as e:
            print(e)


def save_json(obj, filename, sort_keys=False):
    with open(filename, 'w') as f:
        json.dump(obj, f, ensure_ascii=False, sort_keys=sort_keys)


class MainHandler(RequestHandler):
    URL = r'/'

    def get(self):
        pages = [f[:-5] for f in listdir(path.join(BASE_DIR, 'static', 'pos')) if f.endswith('.json')]
        self.render('index.html', pages=pages)


class CutHandler(RequestHandler):
    URL = r'/(\w+)'

    def get(self, name):
        filename = path.join(BASE_DIR, 'static', 'pos', name + '.json')
        page = load_json(filename)
        self.render('block_cut.html', page=page, imgsize=page['imgsize'], blocks=json.dumps(page.get('blocks', [])))

    def post(self, name):
        filename = path.join(BASE_DIR, 'static', 'pos', name + '.json')
        page = load_json(filename)
        blocks = json.loads(self.get_body_argument('blocks'))
        assert 'imgsize' in page and isinstance(blocks, list)
        page['blocks'] = blocks
        save_json(page, filename)
        self.write('ok')


def make_app():
    handlers = [MainHandler, CutHandler]
    return Application([(h.URL, h) for h in handlers],
                       debug=True,
                       static_path=path.join(BASE_DIR, 'static'),
                       template_path=path.join(BASE_DIR, 'views'))


if __name__ == '__main__':
    app = make_app()
    app.listen(8001)
    print('Start the app on http://localhost:8001')
    IOLoop.current().start()
