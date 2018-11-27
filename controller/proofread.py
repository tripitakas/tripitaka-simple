#!/usr/bin/env python
# -*- coding: utf-8 -*-

from controller.base import BaseHandler, load_json, save_json, get_date_time
from os import path

BASE_DIR = path.dirname(path.dirname(__file__))


class ProofreadHandler(BaseHandler):
    URL = r'/proof'

    def get(self):
        info = dict(name='QL_24_31', width=1200, height=1670, image='static/img/QL_24_31.jpg',
                    cutdata=load_json(path.join(BASE_DIR, 'data', 'QL_24_31.cut')),
                    cmpdata=load_json(path.join(BASE_DIR, 'data', 'QL_24_31.json')))
        self.render('proofread.html', **info)
