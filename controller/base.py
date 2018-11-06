#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.web import RequestHandler
import logging
from os import path
import json
import re
from datetime import datetime


def load_json(filename):
    if path.exists(filename):
        try:
            with open(filename, 'rb') as f:
                return json.load(f)
        except Exception as e:
            logging.error('%s: %s' % (str(e), filename))


def save_json(obj, filename, sort_keys=False):
    with open(filename, 'w') as f:
        json.dump(obj, f, ensure_ascii=False, sort_keys=sort_keys)


def get_date_time(fmt=None):
    return datetime.now().strftime(fmt or '%Y-%m-%d %H:%M:%S')


class BaseHandler(RequestHandler):
    def set_default_headers(self):
        h = 'Content-Type,Host,X-Forwarded-For,X-Requested-With,User-Agent,Cache-Control,Cookies'
        self.set_header('Cache-Control', 'no-cache')
        self.set_header('Access-Control-Allow-Headers', h)

    @property
    def current_user(self):
        return self.get_cookie('cut-user', '')

    def render(self, template_name, **kwargs):
        kwargs['user'] = self.current_user or '匿名'
        return super(BaseHandler, self).render(template_name, **kwargs)

    def get_ip(self):
        ip = self.request.headers.get('x-forwarded-for') or self.request.remote_ip
        return ip and re.sub(r'^::\d$', '', ip[:15]) or 'localhost'
