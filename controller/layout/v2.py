import json
# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg

# from check_mulsubcol import check_multiple_subcolumns
# from mark_mulsubcol import mark_subcolumns
# from use_noteid import calc_order

# ----------------------------------------------------------------------------------------#
# A 是否包含在B当中


def is_contained_in(A, B, threshold=0, ignore_y=False):
    threshold = threshold or max(20, B['w'] * 0.25)
    if A['x'] - B['x'] >= -threshold:
        if A['x'] + A['w'] - B['x'] - B['w'] <= threshold:
            if ignore_y or A['y'] - B['y'] >= -threshold:
                if ignore_y or A['y'] + A['h'] - B['y'] - B['h'] <= threshold:
                    return True
    return False


# ----------------------------------------------------------------------------------------#
# 计算各字框之间的链接关系


def calc_connections(coordinate, indices, connection):
    # 字框重合比例超过ratio，认为有效
    ratio = 0.3
    # 字框高度差比例超过ratio_h，认为字框在另一字框下方
    ratio_h = 0.3
    # 逐字框处理
    for i in range(0, len(indices)):
        a = coordinate[indices[i]]
        # 定义距离: {'index':,'y_diff':,'x_overlap_left':,'x_overlap_left'}
        dist = []
        # 计算距离，并确定下方字框
        for j in range(0, len(indices)):
            if j == i:
                continue
            b = coordinate[indices[j]]
            # 仅考虑比a低的字框
            if b['y'] < a['y']:
                continue
            # 仅考虑与a的x坐标有重合的字框
            if (b['x'] > a['x'] + a['w']) or (b['x'] + b['w'] < a['x']):
                continue
            # 计算纵向距离
            y_diff = b['y'] - a['y'] - a['h']
            # 计算左重合点
            x_overlap_left = max(a['x'], b['x'])
            # 计算右重合点
            x_overlap_right = min(a['x'] + a['w'], b['x'] + b['w'])
            # 计算重合长度
            w_overlap = x_overlap_right - x_overlap_left
            # 仅考虑重合比例超过门限的字框
            if (w_overlap > ratio * a['w']) or (w_overlap > ratio * b['w']):
                dist.append({'index': indices[j],
                             'y_diff': y_diff,
                             'x_overlap_left': x_overlap_left,
                             'x_overlap_right': x_overlap_right})
        # 确定相邻下方字框
        down_neighbor = []
        for j in range(0, len(dist)):
            candidate_flag = True
            for k in range(0, len(dist)):
                if k == j:
                    continue
                # overlap是否重合
                if (dist[j]['x_overlap_left'] > dist[k]['x_overlap_right']) \
                        or (dist[k]['x_overlap_left'] > dist[j]['x_overlap_right']):
                    pass
                else:
                    # 是否在j对应字框上方
                    if dist[j]['y_diff'] > dist[k]['y_diff'] + ratio_h * coordinate[dist[k]['index']]['h']:
                        candidate_flag = False
            if candidate_flag:
                down_neighbor.append(dist[j]['index'])
        # 更新链接关系
        for j in down_neighbor:
            connection[indices[i]]['Down'].append(j)
            connection[j]['Up'].append(indices[i])
    return


# ----------------------------------------------------------------------------------------#


# 对同列的字框标上列序号
def mark_column_id(char_list, connection, coordinate_char_list, idx, marker, direction):
    A = char_list[idx]
    a_c = connection[idx]
    if A['column_id'] != 0:
        return
    A['column_id'] = marker
    # 向下搜索
    if direction == 0 or direction == 1:
        if len(a_c['Down']) == 0:
            if direction == 1:
                return
        elif len(a_c['Down']) == 1:
            next_idx = a_c['Down'][0]
            mark_column_id(char_list, connection, coordinate_char_list, next_idx, marker, 1)
            B = char_list[next_idx]
            b_c = connection[next_idx]
            if len(b_c['Up']) >= 2:
                idx_sorted = sorted(range(len(b_c['Up'])),
                                    key=lambda k: coordinate_char_list[b_c['Up'][k]]['x']
                                                  + coordinate_char_list[b_c['Up'][k]]['w'],
                                    reverse=True)
                for i in range(0, len(idx_sorted)):
                    subidx = b_c['Up'][idx_sorted[i]]
                    mark_subcolumn_id(char_list, connection, subidx, i + 1, -1)
                    if subidx != idx:
                        mark_column_id(char_list, connection, coordinate_char_list, subidx, marker, -1)
        elif len(a_c['Down']) >= 2:
            idx_sorted = sorted(range(len(a_c['Down'])),
                                key=lambda k: coordinate_char_list[a_c['Down'][k]]['x']
                                              + coordinate_char_list[a_c['Down'][k]]['w'],
                                reverse=True)
            for i in range(0, len(idx_sorted)):
                subidx = a_c['Down'][idx_sorted[i]]
                mark_subcolumn_id(char_list, connection, subidx, i + 1, 1)
                mark_column_id(char_list, connection, coordinate_char_list, subidx, marker, 1)
        else:
            # 异常情况
            return
    # 向上搜索
    if direction == 0 or direction == -1:
        if len(a_c['Up']) == 0:
            return
        elif len(a_c['Up']) == 1:
            next_idx = a_c['Up'][0]
            mark_column_id(char_list, connection, coordinate_char_list, next_idx, marker, -1)
            B = char_list[next_idx]
            b_c = connection[next_idx]
            if len(b_c['Down']) >= 2:
                idx_sorted = sorted(range(len(b_c['Down'])),
                                    key=lambda k: coordinate_char_list[b_c['Down'][k]]['x']
                                                  + coordinate_char_list[b_c['Down'][k]]['w'],
                                    reverse=True)
                for i in range(0, len(idx_sorted)):
                    subidx = b_c['Down'][idx_sorted[i]]
                    mark_subcolumn_id(char_list, connection, subidx, i + 1, 1)
                    if subidx != idx:
                        mark_column_id(char_list, connection, coordinate_char_list, subidx, marker, 1)
        elif len(a_c['Up']) >= 2:
            idx_sorted = sorted(range(len(a_c['Up'])),
                                key=lambda k: coordinate_char_list[a_c['Up'][k]]['x']
                                              + coordinate_char_list[a_c['Up'][k]]['w'],
                                reverse=True)
            for i in range(0, len(idx_sorted)):
                subidx = a_c['Up'][idx_sorted[i]]
                mark_subcolumn_id(char_list, connection, subidx, i + 1, -1)
                mark_column_id(char_list, connection, coordinate_char_list, subidx, marker, -1)

        else:
            # 异常情况
            return


# ----------------------------------------------------------------------------------------#


# 标记夹注子列的序号
def mark_subcolumn_id(char_list, connection, idx, marker, direction):
    A = char_list[idx]
    a_c = connection[idx]
    if A['subcolumn_id'] != 0:
        return
    A['subcolumn_id'] = marker
    # 向下搜索
    if direction == 1:
        if len(a_c['Down']) == 0:
            return
        elif len(a_c['Down']) == 1:
            next_idx = a_c['Down'][0]
            b_c = connection[next_idx]
            if len(b_c['Up']) == 1:
                mark_subcolumn_id(char_list, connection, next_idx, marker, 1)
            elif len(b_c['Up']) >= 2:
                return
        else:
            return
    # 向上搜索
    if direction == -1:
        if len(a_c['Up']) == 0:
            return
        elif len(a_c['Up']) == 1:
            next_idx = a_c['Up'][0]
            b_c = connection[next_idx]
            if len(b_c['Down']) == 1:
                mark_subcolumn_id(char_list, connection, next_idx, marker, -1)
            elif len(b_c['Down']) >= 2:
                return
        else:
            return


# ----------------------------------------------------------------------------------------#


# 标记列内ch_id
def mark_ch_id(char_list, connection, idx, marker):
    A = char_list[idx]
    a_c = connection[idx]
    if A['ch_id'] != 0:
        return
    else:
        A['ch_id'] = marker
        if len(a_c['Down']) == 0:
            return
        elif len(a_c['Down']) == 1:
            next_idx = a_c['Down'][0]
            mark_ch_id(char_list, connection, next_idx, marker + 1)
        else:
            for j in a_c['Down']:
                #                mark_ch_id(char_list, j, marker)
                char_list[j]['ch_id'] = marker
                mark_note_id(char_list, connection, j, 1)
    return


# ----------------------------------------------------------------------------------------


# 标记subcolumn内的note_id
def mark_note_id(char_list, connection, idx, marker):
    A = char_list[idx]
    a_c = connection[idx]
    # print(idx)
    # print(connection[idx])
    A['note_id'] = marker
    if len(a_c['Down']) == 0:
        return
    elif len(a_c['Down']) == 1:
        next_idx = a_c['Down'][0]
        B = char_list[next_idx]
        b_c = connection[next_idx]
        if len(b_c['Up']) == 1:
            B['ch_id'] = A['ch_id']
            mark_note_id(char_list, connection, next_idx, marker + 1)
        else:
            if B['ch_id'] == 0:
                mark_ch_id(char_list, connection, next_idx, A['ch_id'] + 1)
    else:
        # 夹注出现夹注，异常情况
        return
    return


# ----------------------------------------------------------------------------------------#
# 根据列号、子列号等，计算列内序号
def calc_order(char_list, indices):
    candidates = [{'ch_id': 0, 'subcolumn_id': 1, 'note_id': 1},
                  {'ch_id': 1, 'subcolumn_id': 0, 'note_id': 0}]
    for order in range(0, len(indices)):
        flag = 0
        for cnddt in candidates:
            for i in indices:
                if char_list[i]['ch_id'] == cnddt['ch_id'] and char_list[i]['subcolumn_id'] == cnddt['subcolumn_id'] and \
                                char_list[i]['note_id'] == cnddt['note_id']:
                    flag = 1
                    char_list[i]['column_order'] = order + 1
                    if cnddt['subcolumn_id'] != 0:
                        # 这个字是小字
                        candidates = [{'ch_id': char_list[i]['ch_id'], 'subcolumn_id': char_list[i]['subcolumn_id'],
                                       'note_id': char_list[i]['note_id'] + 1},
                                      {'ch_id': char_list[i]['ch_id'], 'subcolumn_id': char_list[i]['subcolumn_id'] + 1,
                                       'note_id': 1},
                                      {'ch_id': char_list[i]['ch_id'] + 1, 'subcolumn_id': 0, 'note_id': 0},
                                      {'ch_id': char_list[i]['ch_id'] + 1, 'subcolumn_id': 1, 'note_id': 1}]
                    else:
                        candidates = [{'ch_id': char_list[i]['ch_id'], 'subcolumn_id': 1, 'note_id': 1},
                                      {'ch_id': char_list[i]['ch_id'] + 1, 'subcolumn_id': 0, 'note_id': 0},
                                      {'ch_id': char_list[i]['ch_id'] + 1, 'subcolumn_id': 1, 'note_id': 1}]
                    break
            if flag:
                break


# ----------------------------------------------------------------------------------------#
# 显示字框
def show(char_list, coordinate_char_list, indices, ax, filename):
    for i in indices:
        xleft = coordinate_char_list[i]['x']
        xright = xleft + coordinate_char_list[i]['w']
        yup = coordinate_char_list[i]['y']
        ydown = yup + coordinate_char_list[i]['h']
        A = char_list[i]
        if A['subcolumn_id'] == 0:
            # plt.plot([xleft,xright],[yup,yup],'r-')
            # plt.plot([xleft, xright], [ydown, ydown], 'r-')
            # plt.plot([xleft, xleft], [yup, ydown], 'r-')
            # plt.plot([xright, xright], [yup, ydown], 'r-')
            rect = plt.Rectangle((xleft, yup), coordinate_char_list[i]['w'], coordinate_char_list[i]['h'], color='r',
                                 alpha=0.1)
            ax.add_patch(rect)
        else:
            radius = min([coordinate_char_list[i]['h'], coordinate_char_list[i]['w']]) / 2
            circ = plt.Circle(((xleft + xright) / 2, (yup + ydown) / 2), radius, color='g', alpha=0.5)  # 圆心，半径，颜色，α
            ax.add_patch(circ)
        #        plt.text(xleft,-ydown,str(i)+','+str(A['Up'])+','+str(A['Down']))
        #        plt.text(xleft,-ydown,str(A['column_id'])+'-'+str(A['ch_id'])+'-'+str(A['subcolumn_id'])+'-'+str(A['note_id']))
        #        plt.text(xleft, ydown,str(A['column_order']))
    plt.savefig(filename, dpi=300)

    #    plt.show()
    # 显示字框
    def show(char_list, coordinate_char_list, indices, ax, filename):
        for i in indices:
            xleft = coordinate_char_list[i]['x']
            xright = xleft + coordinate_char_list[i]['w']
            yup = coordinate_char_list[i]['y']
            ydown = yup + coordinate_char_list[i]['h']
            A = char_list[i]
            if A['subcolumn_id'] == 0:
                # plt.plot([xleft,xright],[yup,yup],'r-')
                # plt.plot([xleft, xright], [ydown, ydown], 'r-')
                # plt.plot([xleft, xleft], [yup, ydown], 'r-')
                # plt.plot([xright, xright], [yup, ydown], 'r-')
                rect = plt.Rectangle((xleft, yup), coordinate_char_list[i]['w'], coordinate_char_list[i]['h'],
                                     color='r', alpha=0.1)
                ax.add_patch(rect)
            else:
                radius = min([coordinate_char_list[i]['h'], coordinate_char_list[i]['w']]) / 2
                circ = plt.Circle(((xleft + xright) / 2, (yup + ydown) / 2), radius, color='g', alpha=0.5)  # 圆心，半径，颜色，α
                ax.add_patch(circ)
        # plt.text(xleft,-ydown,str(i)+','+str(A['Up'])+','+str(A['Down']))
        #        plt.text(xleft,-ydown,str(A['column_id'])+'-'+str(A['ch_id'])+'-'+str(A['subcolumn_id'])+'-'+str(A['note_id']))
        #        plt.text(xleft, ydown,str(A['column_order']))
        plt.savefig(filename, dpi=300)

    #    plt.show()
    return


# ----------------------------------------------------------------------------------------#

# 显示字框
def show2(char_list, coordinate_char_list, indices, ax, filename):
    for i in indices:
        xleft = coordinate_char_list[i]['x']
        xright = xleft + coordinate_char_list[i]['w']
        yup = coordinate_char_list[i]['y']
        ydown = yup + coordinate_char_list[i]['h']
        A = char_list[i]
        if A['subcolumn_id'] == 0:
            plt.plot([xleft, xright], [-yup, -yup], 'r-')
            plt.plot([xleft, xright], [-ydown, -ydown], 'r-')
            plt.plot([xleft, xleft], [-yup, -ydown], 'r-')
            plt.plot([xright, xright], [-yup, -ydown], 'r-')
            # rect = plt.Rectangle((xleft, yup), coordinate_char_list[i]['w'], coordinate_char_list[i]['h'], color='r', alpha=0.1)
            # ax.add_patch(rect)
        else:
            radius = min([coordinate_char_list[i]['h'], coordinate_char_list[i]['w']]) / 2
            circ = plt.Circle(((xleft + xright) / 2, (-yup - ydown) / 2), radius, color='g', alpha=0.5)  # 圆心，半径，颜色，α
            ax.add_patch(circ)
        # plt.text(xleft,-ydown,str(A['column_id'])+'-'+str(A['ch_id'])+'-'+str(A['subcolumn_id'])+'-'+str(A['note_id']))
        # plt.text(xright, -ydown, str(i))
        # plt.text(xright, -ydown, str(A['column_order']))
        plt.text(xleft, -ydown, str(A['column_id']) + '-' + str(A['column_order']))


# plt.savefig(filename, dpi = 300)
#    plt.show()

# ----------------------------------------------------------------------------------------#



# 显示连线
def show_connection(char_list, coordinate_char_list, indices):
    for order in range(1, len(indices)):
        for i in indices:
            if char_list[i]['column_order'] == order:
                A = coordinate_char_list[i]
            if char_list[i]['column_order'] == order + 1:
                B = coordinate_char_list[i]
        Ax = A['x'] + A['w'] * 3 / 4
        Ay = A['y'] + A['h'] * 3 / 4
        Bx = B['x'] + B['w'] * 3 / 4
        By = B['y'] + B['h'] * 1 / 4
        if Ay < By:
            plt.plot([Ax, Bx], [Ay, By], 'g-')
            # plt.arrow(Ax,Ay, Bx-Ax, By-Ay, color='g', linestyle='-')
        else:
            plt.plot([Ax, Bx], [Ay, By], 'r-')
    return


def calc(chars, blocks):
    # 定义新的字框数据结构
    char_list = []
    connections = []
    for i in range(0, len(chars)):
        char_list.append(
            {'block_id': 0, 'column_id': 0, 'ch_id': 0, 'subcolumn_id': 0, 'note_id': 0, 'column_order': 0})
        connections.append({'Up': [], 'Down': []})
    # 标记栏框
    for i in range(0, len(chars)):
        for i_b in range(0, len(blocks)):

            if is_contained_in(chars[i], blocks[i_b], ignore_y=len(blocks) < 2):
                char_list[i]['block_id'] = i_b + 1
                # -------------------------
                # 检查是否存在没有标记栏序的字框
                # 云贵师兄： 能否完善该部分？
                # -------------------------
                ##########################################################################
    # 逐栏处理
    for i_b in range(0, len(blocks)):
        # 统计列内字框的索引
        char_indices_in_block = []
        for i in range(0, len(chars)):
            if char_list[i]['block_id'] == i_b + 1:
                char_indices_in_block.append(i)
        calc_connections(chars, char_indices_in_block, connections)
        # print(connections)
        # print(connections[2])
        # print(connections[3])
        # print(connections[8])
        # 对字框从右到左排序
        idx_sorted = sorted(range(len(char_indices_in_block)),
                            key=lambda k: chars[char_indices_in_block[k]]['x'],
                            reverse=True)
        # 标记列号
        column_marker = 1
        for i in idx_sorted:
            idx = char_indices_in_block[i]
            if char_list[idx]['column_id'] == 0:
                mark_column_id(char_list, connections, chars, idx, column_marker, 0)
                column_marker = column_marker + 1
            else:
                continue
        # -------------------------
        # 检查是否存在没有标记列号的字框
        # 云贵师兄： 能否完善该部分？
        # -------------------------
        # 对列内字号、夹注号进行标注
        for i in char_indices_in_block:
            A = char_list[i]
            a_c = connections[i]
            if A['block_id'] == 0:
                # 异常情况
                continue
            else:
                # 列内首字开始编号
                if len(a_c['Up']) == 0:
                    if A['subcolumn_id'] == 0:
                        mark_ch_id(char_list, connections, i, 1)
                    else:
                        mark_note_id(char_list, connections, i, 1)
                else:
                    continue
        # 根据列号，子列号等，进行列内排序
        for i in range(1, column_marker):
            char_indices_in_column = []
            for k in char_indices_in_block:
                if char_list[k]['column_id'] == i:
                    char_indices_in_column.append(k)
            calc_order(char_list, char_indices_in_column)
            # -------------------------
            # 检查是否存在没有标记列内序号的字框
            # 云贵师兄： 能否完善该部分？
            # -------------------------
    # 输出数据
    return char_list

# ----------------------------------------------------------------------------------------#

# main 函数
#########################################################################
if __name__ == '__main__':
    # 文件路径
    # 师兄只需要看这几个页面："JX_245_2_155", "JX_245_3_67", "JX_245_3_87", "JX_254_5_218", "JX_260_1_206", "JX_260_1_241", "JX_260_1_256"
    # tempfilename = "JX_165_7_12"
    # tempfilename = "JX_254_5_218"
    # tempfilename = "JX_260_1_74"
    # tempfilename = "JX_245_2_155"
    # tempfilename = "JX_245_3_67"
    # tempfilename = "JX_260_1_126"
    # tempfilename = "JX_245_3_87" # 三列夹注小字
    tempfilename = "JX_254_5_218"
    # tempfilename = "JX_260_1_206"
    # tempfilename = "JX_260_1_241"
    # tempfilename = "JX_260_1_256"
    filename = "data/" + tempfilename
    # 加载字框数据
    with open(filename + ".json", 'r', encoding='UTF-8') as load_f:
        data_dict = json.load(load_f)
        coordinate_char_list = data_dict['chars']
    # 加载栏框和列框数据
    with open(filename + "_column" + ".json", 'r') as load_f:
        data_dict = json.load(load_f)
        coordinate_block_list = data_dict['blocks']
        # coordinate_column_list = data_dict['columns']

    # 保存数据
    py2json = {}
    py2json['char_list'] = calc(coordinate_char_list, coordinate_block_list)
    json_str = json.dumps(py2json)
    # print(char_list)
    # print(json_str)
    ###################################################################################
    # 以下为显示部分 可以忽略

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    show2(char_list, coordinate_char_list, [n for n in range(0, len(char_list))], ax=ax,
          filename=filename + '_note.jpg')
    plt.show()

    # print(char_list)
    # 读取图片
    pic = mpimg.imread(filename + ".jpg")
    fig, ax = plt.subplots()
    im = ax.imshow(pic, cmap='gray')
    plt.axis('off')
    show(char_list, coordinate_char_list, [n for n in range(0, len(char_list))], ax=ax, filename=filename + '_note.jpg')

    # fig, ax = plt.subplots()
    # im = ax.imshow(pic, cmap='gray')
    # plt.axis('off')
    for i_b in range(0, len(coordinate_block_list)):
        for i_c in range(0, len(coordinate_char_list)):
            # 统计列内字框的索引
            char_indices_in_column = []
            for i in range(0, len(coordinate_char_list)):
                if char_list[i]['column_id'] == i_c + 1 and char_list[i]['block_id'] == i_b + 1:
                    char_indices_in_column.append(i)
            if len(char_indices_in_column) > 0:
                show_connection(char_list, coordinate_char_list, char_indices_in_column)
            else:
                break
    plt.savefig(filename + '_lines.jpg', dpi=300)
    plt.show()
