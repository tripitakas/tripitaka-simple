#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.escape import url_escape
from controller.cut import CutHandler
import re
import json
from .layout.v1 import calc as calc1
from .layout.v2 import calc as calc2


class ProofreadHandler(CutHandler):
    URL = r'/(proof)/([A-Z]{2})/(\w{4,20})'

    def do_render(self, name, template_name, **params):
        def get_column_boxes(block_no, line_no):
            return [c for c in chars if c.get('char_id', '').startswith('b%dc%dc' % (block_no, line_no))]

        def to_int(s):
            try:
                return int(s)
            except TypeError:
                return 0

        def gen_segments(txt):
            def apply_span():
                if items:
                    segments.append(dict(block_no=1 + blk_i, line_no=line_no, type='same', ocr=items))
                    
            segments = []
            txt = re.sub(r'\s*<!--.+-->\s*\n?', '\n', txt, flags=re.M)  # 修正从其他网站贴入的音释内容
            for blk_i, block in enumerate(txt.split('\n\n\n')):
                col_diff = 1
                block = re.sub(r'\n{2}', '\n', block, flags=re.M)
                for col_i, column in enumerate(block.strip().split('\n')):
                    column = column.strip()
                    line_no = col_diff + col_i
                    if not column:
                        segments.append(dict(block_no=1 + blk_i, line_no=line_no, type='emptyline', ocr=''))
                        continue
                    while col_diff < 50 and not get_column_boxes(1 + blk_i, line_no):
                        col_diff += 1
                        line_no = col_diff + col_i
                    boxes = get_column_boxes(1 + blk_i, line_no)
                    if len(boxes) != len(re.sub(r'\s', '', column)):
                        params['mismatch_lines'].append('b%dc%d' % (1 + blk_i, line_no))
                    column = [url_escape(c) for c in list(column)]
                    items = []
                    for c in column:
                        if len(c) > 9:
                            apply_span()
                            items = []
                            segments.append(dict(block_no=1 + blk_i, line_no=line_no, type='variant', ocr=[c], cmp=''))
                        else:
                            items.append(c)
                    apply_span()
            return {'segments': segments}

        def get_char_no(c):
            p = c.get('char_id').split('c')
            return to_int(p[2]) if len(p) > 2 else 0

        def apply_new_chars():
            for c_i, c in enumerate(new_chars):
                if not c['column_order']:
                    zero_key = 'b%dc%d' % (c['block_id'], c['column_id'])
                    ids0[zero_key] = ids0.get(zero_key, 100) + 1
                    c['column_order'] = ids0[zero_key]
                chars[c_i]['char_id'] = 'b%dc%dc%d' % (c['block_id'], c['column_id'], c['column_order'])
                chars[c_i].pop('block_no', 0)
                chars[c_i].pop('line_no', 0)
                chars[c_i].pop('char_no', 0)
            params['zero_char_id'] = [c.get('char_id') for c in chars if get_char_no(c) > 100]

        chars = params['chars']
        ids0 = {}
        params['order_changed'] = len([c for c in chars if c.get('order_changed')])
        params['zero_char_id'] = []
        layout_type = params['layout_type'] = int(self.get_query_argument('layout', params.get('layout_type', 0)))
        if not params['order_changed'] or self.get_query_argument('layout', None):
            new_chars = calc2(chars, params['blocks']) if layout_type == 2 \
                else calc1(chars, params['blocks'], params['columns'])
            apply_new_chars()
        if params.get('test') and params.get('zero_char_id') and layout_type != 2:
            new_chars = calc2(chars, params['blocks'])
            apply_new_chars()
            if params['zero_char_id']:
                new_chars = calc1(chars, params['blocks'], params['columns'])
                apply_new_chars()
            else:
                layout_type = 2
                params['force_layout_type'] = layout_type
                print('%s\t0\t2' % name)

        if params.get('zero_char_id'):
            print('%s\t%d\t%s\t%d' % (name, len(params['zero_char_id']), ','.join(params['zero_char_id'][:5]), layout_type))
        params['origin_txt'] = params['txt'].strip().split('\n')
        params['mismatch_lines'] = []
        params['txt'] = json.dumps(gen_segments(params['txt']), ensure_ascii=False)
        return params if params.get('test') else self.render(template_name, **params)


class ColumnCheckHandler(CutHandler):
    URL = r'/(column)/([A-Z]{2})/(\w{4,20})'

    def do_render(self, name, template_name, **params):
        params['txt_lines'] = len([t for t in params['txt'].split('\n') if t])
        return params if params.get('test') else self.render(template_name, **params)
