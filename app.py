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
    URL = r'/(char|block|line)?'

    def get(self, pos='block'):
        if pos == 'block':
            pages = [f[:-5] for f in listdir(path.join(BASE_DIR, 'static', 'block_pos')) if f.endswith('.json')]
        elif pos == 'char':
            pages = [f[:-4] for f in listdir(path.join(BASE_DIR, 'static', 'char_pos')) if f.endswith('.cut')]
        else:
            pages = []
        self.render('index.html', pages=pages, pos=pos)


class BlockCutHandler(RequestHandler):
    URL = r'/block/(\w+)'

    def get(self, name):
        filename = path.join(BASE_DIR, 'static', 'block_pos', name + '.json')
        page = load_json(filename)
        self.render('block_cut.html', page=page, imgsize=page['imgsize'], blocks=json.dumps(page.get('blocks', [])))

    def post(self, name):
        filename = path.join(BASE_DIR, 'static', 'block_pos', name + '.json')
        page = load_json(filename)
        blocks = json.loads(self.get_body_argument('blocks'))
        assert 'imgsize' in page and isinstance(blocks, list)
        if page['blocks'] != blocks:
            page['blocks'] = blocks
            save_json(page, filename)
            logging.info('%d blocks saved: %s' % (len(blocks), name))
        self.write('ok')


class CharCutHandler(RequestHandler):
    URL = r'/char/(\w+)'

    def get(self, name):
        filename = path.join(BASE_DIR, 'static', 'char_pos', name + '.cut')
        page = load_json(filename)
        page['imgname'] = page.get('imgname', name)
        self.render('char_cut.html', page=page, imgsize=page['imgsize'], chars=json.dumps(page.get('char_data', [])))

    def post(self, name):
        filename = path.join(BASE_DIR, 'static', 'char_pos', name + '.cut')
        page = load_json(filename)
        chars = json.loads(self.get_body_argument('chars'))
        assert isinstance(chars, list)
        if page['chars'] != chars:
            page['chars'] = chars
            save_json(page, filename)
            logging.info('%d chars saved: %s' % (len(chars), name))
        self.write('ok')


def make_app():
    handlers = [MainHandler, BlockCutHandler, CharCutHandler]
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
