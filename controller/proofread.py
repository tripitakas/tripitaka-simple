#!/usr/bin/env python
# -*- coding: utf-8 -*-

from controller.cut import CutHandler


class ProofreadHandler(CutHandler):
    URL = r'/(proof)/([A-Z]{2})/(\w{4,20})'

    def do_render(self, name, template_name, **params):
        def gen_segments(txt):
            segments = []
            for blk_i, block in enumerate(txt.split('\n\n\n')):
                col_diff = 1
                for col_i, column in enumerate(block.strip().split('\n')):
                    line_no = col_diff + col_i
                    while not [c for c in chars if c['char_id'].startswith('b%dc%dc' % (1 + blk_i, line_no))]:
                        col_diff += 1
                        line_no = col_diff + col_i
                    ln = dict(block_no=1 + blk_i, line_no=line_no, type='same', ocr=column)
                    segments.append(ln)
            return {'segments': segments}

        def get_img(p):
            return '/static/' + '/'.join(['img', *p.split('_')[:-1], p + '.jpg'])

        chars = params['chars']
        params['get_img'] = get_img
        params['txt'] = gen_segments(params['txt'])
        return self.render(template_name, **params)
