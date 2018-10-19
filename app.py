#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado import netutil, process
from tornado.httpserver import HTTPServer
from tornado.options import define, options
import logging
from os import path, listdir
import json

BASE_DIR = path.dirname(__file__)
define('port', default=8001, help='run port', type=int)
define('debug', default=options.port != 80, help='debug mode', type=bool)
define('num_processes', default=4, help='sub-processes count', type=int)
kinds = ['GL', 'JX', 'QL', 'YB']


def load_json(filename):
    if path.exists(filename):
        try:
            with open(filename) as f:
                return json.load(f)
        except Exception as e:
            logging.error('%s: %s' % (str(e), filename))


def save_json(obj, filename, sort_keys=False):
    with open(filename, 'w') as f:
        json.dump(obj, f, ensure_ascii=False, sort_keys=sort_keys)


class MainHandler(RequestHandler):
    URL = r'/'

    def get(self):
        index = load_json(path.join('static', 'index.json'))
        self.render('index.html', kinds=kinds, index=index)


class PagesHandler(RequestHandler):
    URL = r'/(block|column|char)/([A-Z]{2})'

    def get(self, pos, kind):
        def get_icon(p):
            return path.join('icon', *p.split('_')[:-1], p + '.jpg')

        index = load_json(path.join('static', 'index.json'))
        pages = index[kind]
        pos_type = '字切分' if pos == 'char' else '栏切分' if pos == 'block' else '列切分'
        self.render('pages.html', kinds=kinds, pages=pages,
                    pos_type=pos_type, pos=pos, kind=kind, get_icon=get_icon)


class CutProofHandler(RequestHandler):
    URL = r'/(block|column|char)/([A-Z]{2})/(\w{4,20})'

    def get(self, pos, kind, name):
        def get_img(p):
            return path.join('img', *p.split('_')[:-1], p + '.jpg')

        name = kind + '_' + name
        filename = path.join(BASE_DIR, 'static', 'char-pos', *name.split('_')[:-1], name + '.json')
        page = load_json(filename)
        page[pos + 's'] = json.dumps(page[pos + 's'])
        self.render('char_cut.html' if pos == 'char' else 'block_cut.html',
                    pos_type='字切分' if pos == 'char' else '栏切分' if pos == 'block' else '列切分',
                    page=page, pos=pos, kind=kind, **page, get_img=get_img)

    def post(self, pos, kind, name):
        filename = path.join(BASE_DIR, 'static', 'char-pos', *name.split('_')[:-1], name + '.json')
        page = load_json(filename)
        boxes = json.loads(self.get_body_argument('boxes'))
        assert isinstance(boxes, list)
        if page[pos + 's'] != boxes:
            page[pos + 's'] = boxes
            save_json(page, filename)
            logging.info('%d boxes saved: %s' % (len(boxes), name))
        self.write('ok')


def make_app():
    handlers = [MainHandler, PagesHandler, CutProofHandler]
    return Application([(h.URL, h) for h in handlers],
                       debug=options.debug,
                       static_path=path.join(BASE_DIR, 'static'),
                       template_path=path.join(BASE_DIR, 'views'))


if __name__ == '__main__':
    options.parse_command_line()
    try:
        app = make_app()
        server = HTTPServer(app)
        if options.debug:
            server.listen(options.port)
            fork_id = 0
        else:
            sockets = netutil.bind_sockets(options.port)
            fork_id = process.fork_processes(options.num_processes)
            server.add_sockets(sockets)

        logging.info('Start the app #%d on http://localhost:%d' % (fork_id, options.port))
        IOLoop.current().start()
    except KeyboardInterrupt:
        logging.info('Stop the app')
