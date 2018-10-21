#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado import netutil, process
from tornado.httpserver import HTTPServer
from tornado.options import define, options
import logging
from os import path
import controller.proof as p


BASE_DIR = path.dirname(__file__)
define('port', default=8001, help='run port', type=int)
define('debug', default=options.port != 80, help='debug mode', type=bool)
define('num_processes', default=4, help='sub-processes count', type=int)


def make_app():
    handlers = [p.MainHandler, p.PagesHandler, p.CutProofHandler]
    return Application([(h.URL, h) for h in handlers],
                       debug=options.debug,
                       compiled_template_cache=False,
                       static_path=path.join(BASE_DIR, 'static'),
                       template_path=path.join(BASE_DIR, 'views'))


if __name__ == '__main__':
    options.parse_command_line()
    try:
        app = make_app()
        server = HTTPServer(app, xheaders=True)
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
