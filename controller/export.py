#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado import gen
from tornado.concurrent import Future
from tornado.ioloop import IOLoop
from controller.base import BaseHandler, get_date_time
from glob import glob
from os import path
import zipfile


class ExportHandler(BaseHandler):
    URL = r'/export/(block|column|char|proof|txt)/([A-Z]{2})'

    @gen.coroutine
    def get(self, pos, kind):
        def compress(future):
            files = glob(path.join(data_path, '**', '*.*'), recursive=True)
            if path.exists(zip_file):
                return future.set_result(len(files))
            arc = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED)
            count = 0
            for filename in files:
                if filename.endswith('.json') or filename.endswith('.txt'):
                    arc_name = filename.replace(data_path, '')[1:]
                    arc.write(filename, arc_name)
                    count += 1
            arc.close()
            future.set_result(count)

        def download():
            future = Future()
            IOLoop.current().add_callback(compress, future)
            return future

        base_path = path.dirname(path.dirname(__file__))
        static_path = path.join(base_path, 'static')
        data_path = path.join(static_path if pos == 'txt' else path.join(static_path, 'pos'), pos, kind)
        zip_path = path.join(static_path, 'download')
        zip_file = path.join(zip_path, '%s-%s-%s.zip' % (pos, kind, get_date_time('%d%H%M')[:-1]))

        file_count = yield download()
        self.write('<a href="%s" target="_blank">%s</a> %d files' % (
            zip_file.replace(base_path, ''), zip_file.replace(zip_path, '')[1:], file_count))
        self.finish()
