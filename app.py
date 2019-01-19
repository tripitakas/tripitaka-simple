#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado import netutil, process
from tornado.httpserver import HTTPServer
from tornado.options import define, options
import logging
from os import path
import controller.cut as cut
from controller.proofread import ProofreadHandler, ColumnCheckHandler
from controller.fix_data import HelpHandler, RankingHandler, HistoryHandler
from controller.fix_txt import FixTextHandler
from controller.cmp_pos import CmpTxtPosHandler
from controller.export import ExportHandler


BASE_DIR = path.dirname(__file__)
define('port', default=8001, help='run port', type=int)
define('debug', default=True, help='debug mode', type=bool)
define('num_processes', default=4, help='sub-processes count', type=int)


def make_app():
    classes = [cut.MainHandler, cut.PagesHandler, cut.CutHandler, HelpHandler, RankingHandler, HistoryHandler,
               ProofreadHandler, ColumnCheckHandler, ExportHandler, FixTextHandler, CmpTxtPosHandler]
    handlers = []
    for cls in classes:
        if isinstance(cls.URL, list):
            handlers.extend([(s, cls) for s in cls.URL])
        else:
            handlers.append((cls.URL, cls))
    return Application(handlers,
                       debug=options.debug,
                       compiled_template_cache=False,
                       static_path=path.join(BASE_DIR, 'static'),
                       template_path=path.join(BASE_DIR, 'views'))


if __name__ == '__main__':
    options.parse_command_line()
    try:
        app = make_app()
        server = HTTPServer(app, xheaders=True)
        if options.debug and options.port != 80:
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
