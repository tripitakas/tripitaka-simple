#!/usr/bin/env python
# -*- coding: utf-8 -*-

from controller.cut import CutHandler
import re


class ProofreadHandler(CutHandler):
    URL = r'/(proof)/([A-Z]{2})/(\w{4,20})'

    def do_render(self, name, template_name, **params):
        def gen_segments(txt):
            segments = []
            txt = re.sub(r'\S*<!--.+-->\S*', '\n', txt, flags=re.S)  # 修正从其他网站贴入的音释内容
            for blk_i, block in enumerate(txt.split('\n\n\n')):
                col_diff = 1
                for col_i, column in enumerate(block.strip().split('\n')):
                    line_no = col_diff + col_i
                    while col_diff < 50 and not [c for c in chars if c['char_id'].startswith('b%dc%dc' % (1 + blk_i, line_no))]:
                        col_diff += 1
                        line_no = col_diff + col_i
                    ln = dict(block_no=1 + blk_i, line_no=line_no, type='same', ocr=column)
                    segments.append(ln)
            return {'segments': segments}

        chars = params['chars']
        params['origin_txt'] = params['txt'].strip().split('\n')
        params['txt'] = gen_segments(params['txt'])
        return self.render(template_name, **params)
