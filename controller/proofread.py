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

        def is_contained_in(A, B):
            threshold = 0
            if (A['x'] + A['w'] - B['x'] <= threshold) or (A['x'] - B['x'] - B['w'] >= threshold) \
                    or (A['y'] - B['y'] - B['h'] >= threshold) or (A['y'] + A['h'] - B['y'] <= threshold):
                return False
            return True

        def find_nearest_box(box, boxes):
            min_d = 1e7
            ret = -1
            for i, b in enumerate(boxes):
                if box['y2'] > b['y'] and box['y'] < b['y'] + b['h']:
                    dx = abs((box['x'] + box['x2']) / 2 - b['x'] - b['w'] / 2)
                    if min_d > dx:
                        min_d = dx
                        ret = i
            return ret

        def has_note_in_column(chars_in):
            return [c for c in chars_in if c['subcolumn_id']]

        def apply_new_chars(_layout_type):
            # 对于新算法，先比较列框个数：新算法得到的列框个数 > 列框校对后列框个数
            if _layout_type == 2:
                column_ids = ['b%dc%02d' % (c['block_id'], c['column_id']) for i, c in enumerate(new_chars)]
                new_columns = sorted(list(set(column_ids)))
                if len(new_columns) > len(params['columns']):
                    # 合并新算法得到的列框
                    column_boxes = {}
                    for i, (column_id, c) in enumerate(zip(column_ids, chars)):
                        if column_id not in column_boxes:
                            column_boxes[column_id] = dict(x=c['x'], y=c['y'], x2=c['x'] + c['w'], y2=c['y'] + c['h'])
                        else:
                            column_boxes[column_id]['x'] = min(column_boxes[column_id]['x'], c['x'])
                            column_boxes[column_id]['y'] = min(column_boxes[column_id]['y'], c['y'])
                            column_boxes[column_id]['x2'] = max(column_boxes[column_id]['x2'], c['x'] + c['w'])
                            column_boxes[column_id]['y2'] = max(column_boxes[column_id]['y2'], c['y'] + c['h'])

                    # 判断新算法得到的各列所在的列框校对后的列框索引
                    index_column = [find_nearest_box(column_boxes[c], params['columns']) for c in new_columns]

                    # 判断新算法得到的列数据是否存在下列情况：相邻的两个仅包含大字的列有相同的列框索引
                    block_no, column_no, chars_prev = None, 0, []
                    for i, idx in enumerate(index_column):
                        chars_cur = [c for ci, c in enumerate(new_chars) if column_ids[ci] == new_columns[i]]
                        if block_no != chars_cur[0]['block_id']:
                            block_no = chars_cur[0]['block_id']
                            column_no = 0
                            chars_prev = []
                        column_no += 1
                        if chars_prev and idx >= 0 and idx == index_column[i - 1] \
                            and not has_note_in_column(chars_cur) \
                                and not has_note_in_column(chars_prev):
                            print('%s merge columns: %s %s' % (name, new_columns[i], new_columns[i - 1]))
                            column_no -= 1
                            for ci, c in enumerate(chars_cur):
                                c['column_order'] = len(chars_prev) + ci + 1
                            chars_cur = chars_prev + chars_cur
                        for ci, c in enumerate(chars_cur):
                            c['column_id'] = column_no
                        chars_prev = chars_cur

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

        chars = params['chars'] = [c for c in params['chars'] if c['x'] < float(params['imgsize']['width'])
                                   and c['y'] < float(params['imgsize']['height'])]
        ids0 = {}
        params['order_changed'] = len([c for c in chars if c.get('order_changed')])
        params['zero_char_id'] = []
        layout_type = params['layout_type'] = int(self.get_query_argument('layout', params.get('layout_type', 0)))
        if not params['order_changed'] or self.get_query_argument('layout', None):
            new_chars = calc2(chars, params['blocks']) if layout_type == 2 \
                else calc1(chars, params['blocks'], params['columns'])
            apply_new_chars(layout_type)
        if params.get('test') and params.get('zero_char_id') and layout_type != 2:
            new_chars = calc2(chars, params['blocks'])
            apply_new_chars(2)
            if params['zero_char_id']:
                new_chars = calc1(chars, params['blocks'], params['columns'])
                apply_new_chars(1)
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
