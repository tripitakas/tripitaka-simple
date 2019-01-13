#!/usr/bin/env python
# -*- coding: utf-8 -*-

from controller.base import load_json, save_json, get_date_time, BaseHandler
from tornado.options import options
import logging
from os import path, listdir, remove
import json
import random
import time
import codecs

BASE_DIR = path.dirname(path.dirname(__file__))
pos_types = dict(block='切栏', column='切列', char='切字', proof='文字')
kind_types = {'GL': '高丽藏', 'JX': '嘉兴藏', 'QL': '乾隆藏', 'YB': '永乐北藏'}
indexes = load_json(path.join('static', 'index.json'))
kinds = {k: {t: kind_types[t] for t in v} for k, v in indexes.items()}

invalids = '''GL_1260_4_3	1
GL_166_2_5	1
GL_1056_3_2	1
GL_78_9_18	1
GL_807_1_24	1
GL_1454_3_12	1
GL_923_2_9	1
GL_143_1_22	1
GL_1418_4_9	1
GL_70_1_8	1
GL_1442_1_8	1
GL_1047_1_34	1
GL_807_2_8	1
GL_1054_5_5	1
GL_1051_8_11	1
GL_1047_1_15	1
GL_63_1_23	1
GL_1260_3_8	1
GL_1056_1_27	1
GL_1260_10_7	1
GL_1056_5_13	1
GL_78_6_13	1
GL_924_2_21	1
GL_1260_7_9	1
GL_1434_5_10	1
GL_1049_1_4	1
GL_1056_2_6	2
GL_174_3_3	2
GL_1048_1_39	2
GL_129_3_27	2
GL_1054_4_4	2
GL_61_1_15	2
GL_914_9_20	2
GL_1486_17_9	2
GL_959_3_15	2
GL_82_1_5	2
GL_74_4_16	2
GL_914_1_16	2
GL_914_8_15	2
GL_1260_5_3	2
GL_1454_3_6	2
GL_167_1_25	2
GL_1054_1_23	2
GL_922_1_8	2
GL_1260_11_11	2
GL_1442_1_14	2
GL_807_1_12	3
GL_807_2_14	3
GL_1462_2_4	3
GL_1462_2_5	3
GL_1260_8_8	3
GL_78_2_15	3
GL_1418_4_7	3
GL_57_1_29	3
GL_1056_2_4	3
GL_1056_5_12	3
GL_1260_1_3	3
GL_1418_4_3	4
GL_1454_2_14	4
GL_127_7_11	4
GL_914_9_17	4
GL_1454_1_9	4
GL_9_1_16	4
GL_1434_5_11	4
GL_1054_1_19	4
GL_128_3_15	4
GL_1056_1_28	5
GL_1439_1_9	5
GL_9_1_9	5
GL_1054_5_13	5
GL_1056_2_3	5
GL_9_1_13	6
GL_1486_20_6	6
GL_1426_2_8	6
GL_1054_3_20	6
GL_1056_4_16	6
GL_1056_1_8	6
GL_1454_3_13	6
GL_807_1_18	6
GL_1054_3_2	6
GL_1056_2_10	6
GL_1418_4_10	6
GL_1260_10_10	6
GL_1260_9_7	7
GL_1454_3_15	7
GL_924_2_5	7
GL_1048_2_59	7
GL_1462_2_6	7
GL_128_3_13	7
GL_1452_2_9	7
GL_1049_1_27	7
GL_924_1_2	7
GL_1054_2_11	8
GL_923_1_23	8
GL_1260_2_4	8
GL_923_1_14	8
GL_1056_2_18	8
GL_1047_2_17	8
GL_914_5_18	8
GL_1054_4_2	8
GL_1481_18_5	8
GL_922_1_16	8
GL_914_4_3	8
GL_1434_5_5	9
GL_914_1_20	9
GL_923_2_7	9
GL_1456_1_12	9
GL_923_1_36	9
GL_1440_1_6	10
GL_1260_8_3	10
GL_1260_8_4	10
GL_924_2_13	10
GL_924_2_17	10
GL_1056_2_22	11
GL_1454_2_13	11
GL_1434_4_15	11
GL_914_10_7	12
GL_143_2_19	12
GL_1056_2_24	12
GL_922_2_32	12
GL_1056_2_26	13
GL_924_1_12	14
GL_922_1_34	14
GL_914_2_2	14
GL_1056_1_20	14
GL_1054_4_7	14
GL_1260_7_11	15
GL_1054_1_13	15
GL_1260_5_7	16
GL_1056_5_6	16
GL_82_2_8	17
GL_1260_4_2	18
GL_127_6_17	19
GL_1056_1_22	19
GL_1260_3_3	19
GL_807_1_9	20
GL_924_2_23	20
GL_922_1_24	20
GL_922_1_18	20
GL_922_1_21	20
GL_1047_1_21	21
GL_924_2_30	21
GL_1260_9_5	21
GL_922_1_10	21
GL_807_1_14	22
GL_1260_8_11	22
GL_1054_6_2	23
GL_1056_2_20	23
GL_1260_1_11	24
GL_1054_1_12	25
GL_924_2_35	27
GL_922_2_28	27
GL_923_1_11	27
GL_1049_1_10	28
GL_923_2_30	28
GL_922_1_30	28
GL_922_1_12	31
GL_922_1_17	41
GL_1260_5_4	44
GL_922_1_5	47
GL_1054_1_4	49
GL_1047_1_5	51
GL_922_1_29	53
GL_1056_2_21	53
GL_924_1_10	56
GL_922_2_21	61
GL_922_1_6	116
GL_922_1_4	134
YB_34_151	76
YB_33_308	17
YB_24_119	14
YB_26_172	14
YB_24_259	14
YB_32_967	13
YB_27_531	11
YB_29_32	11
YB_30_623	10
YB_29_124	9
YB_28_615	9
YB_32_117	8
YB_24_204	8
YB_30_159	8
YB_30_774	7
YB_33_776	7
YB_24_522	6
YB_29_277	6
YB_28_515	6
YB_28_885	6
YB_28_890	6
YB_26_959	6
YB_29_269	6
YB_30_507	5
YB_24_400	5
YB_23_890	5
YB_24_215	5
YB_28_524	4
YB_33_858	4
YB_32_27	4
YB_29_677	3
YB_31_297	3
YB_32_698	3
YB_24_210	3
YB_24_251	3
YB_29_361	3
YB_30_708	3
YB_22_816	2
YB_24_667	2
YB_24_132	2
YB_30_80	2
YB_26_607	2
YB_32_438	2
YB_24_219	2
YB_24_262	2
YB_25_692	1
YB_26_463	1
YB_27_480	1
YB_33_525	1
YB_25_474	1
YB_23_721	1
YB_29_347	1
YB_33_418	1
YB_29_234	1
YB_29_130	1
YB_27_772	1
YB_23_727	1
YB_29_245	1
YB_32_346	1'''.split('\n')
invalids = {s.split('\t')[0]: s.split('\t')[1] for s in invalids}


class MainHandler(BaseHandler):
    URL = r'/'

    def get(self):
        if 0:
            with open('page_codes.txt') as f:
                lines = f.read().split('\n')
            proof = {"QL": [], "YB": []}
            for t in lines:
                proof[t[:2]].append(t)
            save_json(proof, 'proof.json')
        self.render('index.html', kinds=kinds, index=indexes, pos='char')


class PagesHandler(BaseHandler):
    URL = [r'/(block|column|char|proof)/([A-Z]{2}|me)/?',
           r'/(block|column|char|proof)/(me)/(\w+)']

    @staticmethod
    def get_my_pages(pos, username):
        pages = []
        me = '\n' + username + '\n'
        lock_path = path.join(BASE_DIR, 'data', 'lock', pos)
        for fn in listdir(lock_path):
            filename = path.join(lock_path, fn)
            if '_' in fn and '.' not in fn:
                with open(filename) as f:
                    text = f.read()
                if me in text and fn not in pages:
                    pages.append(fn)
        return sorted(pages)

    def get(self, pos, kind, username=None):
        def get_icon(p):
            if options.debug:
                return '/static/' + '/'.join(['img', *p.split('_')[:-1], p + '.jpg'])
            base_url = 'http://tripitaka-img.oss-cn-beijing.aliyuncs.com/page'
            url = '/'.join([base_url, *p.split('_')[:-1], p + '_' + page_codes.get(p) + '.jpg'])
            return url + '?x-oss-process=image/resize,m_lfit,h_300,w_300'

        def get_info(p):
            filename = path.join(BASE_DIR, 'static', 'pos', pos, *p.split('_')[:-1], p + '.json')
            return load_json(filename)

        page_codes = load_json(path.join(BASE_DIR, 'static/pagecode_hash.json'))
        pos_type = pos_types[pos]
        cur_user = self.current_user or self.get_ip()
        username = username or cur_user
        me = '\n' + username + '\n'
        self.unlock_timeout(pos, me)

        if kind == 'me':
            pages = self.get_my_pages(pos, username)
            return self.render('my_pages.html', kinds=kinds, pages=pages, count=len(pages), username=username,
                               pos_type=pos_type, pos=pos, kind=kind, get_icon=get_icon, get_info=get_info)

        field = pos + ('_invalid' if self.get_query_argument('invalid', 0) == '1' else '')
        pages, count = self.pick_pages(pos, indexes[field].get(kind, []), 12)
        html = 'block_pages.html' if pos == 'block' else 'char_pages.html'
        if pos == 'block':
            [CutHandler.lock_page(self, pos, name) for name in pages]

        self.render(html, kinds=kinds, pages=pages, count=count, username=username, invalids=invalids,
                    pos_type=pos_type, pos=pos, kind=kind, get_icon=get_icon, get_info=get_info)

    @staticmethod
    def unlock_timeout(pos, me):
        lock_path = path.join(BASE_DIR, 'data', 'lock', pos)
        now = time.time()
        for fn in listdir(lock_path):
            filename = path.join(lock_path, fn)
            if '_' in fn and '.' not in fn:
                with open(filename) as f:
                    text = f.read()
                if 'saved' not in text:
                    t = path.getctime(filename)
                    if now - t > 60 * 30 or me in text:
                        remove(filename)
                        logging.warning('%s unlocked: %s' % (fn, text.replace('\n', '|')))

    @staticmethod
    def get_lock_file(pos, name):
        return path.join(BASE_DIR, 'data', 'lock', pos, name)

    @staticmethod
    def pick_pages(pos, pages, count):
        pages = [p for p in pages if not path.exists(PagesHandler.get_lock_file(pos, p))]
        random.shuffle(pages)
        return sorted(pages[:count]), len(pages)


class CutHandler(BaseHandler):
    URL = r'/(block|char)/([A-Z]{2})/(\w{4,20}|all)'
    html_files = dict(block='block_cut.html', column='column_cut.html', char='char_cut.html', proof='proofread.html')

    def get(self, pos, kind, name):
        # 获取page_code对应的文本
        def get_txt(p):
            txt_path = '/'.join(['./static/txt', *p.split('_')[:-1], p + '.txt'])
            if not path.exists(txt_path):
                return 'file not exist.'
            with codecs.open(txt_path, 'r', 'utf-8') as f:
                return ''.join(f.readlines())
        
        # 获取page_code对应的hash值
        def get_hash(p):
            with open('./static/pagecode_hash.json', 'r') as f:
                dct = json.load(f)
            return dct.get(p)

        # 获取page_code对应的图像路径
        def get_img(p):
            if options.debug:
                return '/static/' + '/'.join(['img', *p.split('_')[:-1], p + '.jpg'])
            base_url = 'http://tripitaka-img.oss-cn-beijing.aliyuncs.com/page'
            return '/'.join([base_url, *p.split('_')[:-1], p+'_'+get_hash(p)+'.jpg'])

        def load_render(p):
            if not p.startswith(kind):
                p = kind + '_' + p
            filename = path.join(BASE_DIR, 'static', 'pos', pos, *p.split('_')[:-1], p + '.json')
            page = load_json(filename)
            if not page:
                return self.write('error: {0} 页面不存在'.format(p))
            if pos in 'char|column|block':
                if pos + 's' in page:
                    page[pos + 's'] = json.dumps(page[pos + 's'])
                else:
                    page[pos + 's'] = []

            readonly = test or self.get_query_argument('readonly', None) or self.lock_page(self, pos, p, False) != p
            p = self.do_render(p, self.html_files[pos], pos_type=pos_types[pos], readonly=readonly, test=test,
                               page=page, pos=pos, kind=kind, **page, get_img=get_img, txt=get_txt(p))
            if isinstance(p, dict) and 'force_layout_type' in p:
                page = load_json(filename)
                page['layout_type'] = p['force_layout_type']
                save_json(page, filename)

        test = self.get_query_argument('all', 0) == '1'
        if test:
            pages = indexes[pos][kind] + indexes.get(pos + '_invalid', {}).get(kind, [])
            for name in pages:  # 在 do_render 中传入 test=True 可遍历所有页面
                load_render(name)
        else:
            load_render(name)

    def do_render(self, name, template_name, **params):
        self.render(template_name, **params)

    @staticmethod
    def lock_page(self, pos, name, fail_write=True):
        lock_file = PagesHandler.get_lock_file(pos, name)
        if path.exists(lock_file):
            with open(lock_file) as f:
                text = f.read()
                if text and self.get_ip() not in text and (self.current_user or '匿名') not in text \
                        and 'saved' not in text:
                    return fail_write and self.write('error:别人已锁定了本页面，请返回选择其他页面。')
        if not path.exists(lock_file):
            with open(lock_file, 'w') as f:
                f.write('\n'.join([self.get_ip(), self.current_user, get_date_time()]))
        return name

    def post(self, pos, kind, name):
        """
        保存一个或多个页面的切分校对数据.
        保存一个页面时 name 为页名，请求体中需要有 boxes 框数组. 保存多个页面时 name 为空，请求体的 boxes 为[页,框数组]的数组.
        如果在请求体中指定了 submit 属性，则会输出下一个校对任务的页名（jump:name 格式，无藏别）.
        :param pos: 校对类型，block 为栏切分，column 为列切分，char 为字框切分
        :param kind: 藏别，例如 GL、JX
        :param name: 页名，例如 GL_1047_1_5，请求体中需要有 boxes 框数组. 如果页名为空，则 boxes 为[[name,boxes], ...]数组
        :return: None
        """
        submit = self.get_body_argument('submit', 0)
        rollback = submit == 'rollback'
        submit = submit == 'true'
        layout_type = int(self.get_body_argument('layout_type', 0))

        if rollback:
            lock_file = PagesHandler.get_lock_file(pos, name)
            if path.exists(lock_file):
                with open(lock_file) as f:
                    text = f.read()
                if 'saved' not in text:
                    remove(lock_file)
                    logging.info('%s unlocked' % lock_file)
        else:
            boxes = json.loads(self.get_body_argument('boxes', '[]'))
            assert name or type(boxes) == dict
            if name == 'all':
                for name, arr in boxes:
                    self.save(kind, pos, name, arr)
            else:
                field = self.get_body_argument('is_column', 0) and 'columns' or \
                        self.get_body_argument('is_block', 0) and 'blocks'
                self.save(kind, pos, name, boxes, field, layout_type=layout_type)

            txt = self.get_body_argument('txt', 0)
            txt = json.loads(txt) if txt and txt.startswith('"') else txt
            if txt:
                with codecs.open('/'.join(['./static/txt/', *name.split('_')[:-1], name + '.txt']), 'w', 'utf-8') as f:
                    f.write(txt.strip('\n'))

        if submit:
            pages = PagesHandler.pick_pages(pos, indexes[pos][kind], 1)[0]
            self.write('jump:' + pages[0][3:] if pages else 'error:本类切分已全部校对完成。')
        self.write('')

    def save(self, kind, pos, name, boxes, field=None, layout_type=0):
        filename = path.join(BASE_DIR, 'static', 'pos', pos, *name.split('_')[:-1], name + '.json')
        page = load_json(filename)
        assert page and isinstance(boxes, list)
        field = field or ('chars' if pos == 'proof' else pos + 's')
        saved = page.get('layout_type', 0) != layout_type or (page[field] != boxes and boxes)
        if layout_type:
            page['layout_type'] = layout_type
        if page[field] != boxes and boxes:
            page[field] = boxes
        if saved:
            save_json(page, filename)
            logging.info('%d boxes saved: %s' % (len(boxes), name))

        lock_file = PagesHandler.get_lock_file(pos, name)
        text = []
        if path.exists(lock_file):
            with open(lock_file) as f:
                text = f.read()
                if 'saved' in text:
                    text = text.split('\n')
                else:
                    text = []
        with open(lock_file, 'w') as f:
            text += [self.get_ip(), self.current_user, get_date_time(), 'saved']
            f.write('\n'.join(text))
