import os, sys

sys.path.append('..')
from django.shortcuts import render
from django.http import HttpResponse
import json
from pypinyin import lazy_pinyin, Style
from toolkit.pre_load import neo_con, leafList
from toolkit.pre_load import tree


# Create your views here.

def index(request):
    context = {'title': '测试模版数据'}
    print(request)
    return render(request, 'demo/index.html', context)


def search_entity(request):
    ctx = {}
    # 根据传入的实体名称搜索出关系 这里关系是指双边关系
    # entity-[rel]->[entity2] && entity2-[rel]->entity
    # 应该在这边完成配对
    if request.GET:
        entity = request.GET['user_text']
        # 连接数据库
        db = neo_con
        case = db.matchEnterpreisebyName(entity)
        e1Re2 = db.findRelationByEntity(entity)
        e2Re1 = db.findRelationByEntity2(entity)
        e1News = db.findNewsByEntity(entity)

        # if len(e1Re2) == 0 and len(e2Re1) == 0:
        if len(case) == 0:
            # 若数据库中无法找到该实体，则返回数据库中无该实体
            ctx = {'title': '<h1>数据库中暂未添加该实体</h1>'}
            return render(request, 'demo/entity.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})
        else:
            # 返回查询结果
            ctx = getNodeCard(entity)
            news_list = []
            e1Re2_list = []
            e2Re1_list = []
            print(e1News)
            for d in e1Re2:
                print(d)
                if (d['relation']['supply_product']):
                    e1Re2_list.append(d)
                # if (d['relation']['type'] in ['新闻动态']):
                #     news_list.append(d)
            for d in e2Re1:
                d['relation']['supply_product']
                e2Re1_list.append(d)
                # if(d['relation']['type'] in ['竞争','供应']):
                #     pass
                # if (d['relation']['type'] in ['新闻动态']):
                #     news_list.append(d)
            for d in e1News:
                pass

            ctx['e1Re2'] = json.dumps(e1Re2_list, ensure_ascii=False)
            ctx['e2Re1'] = json.dumps(e2Re1_list, ensure_ascii=False)
            if (len(news_list) > 0):
                ctx['entityNews'] = json.dumps(news_list, ensure_ascii=False)
            return render(request, 'demo/entity.html', ctx)

    return render(request, "demo/entity.html", {'ctx': ctx})


def search_relation(request):
    # todo:完善这边的查询逻辑
    ctx = {}
    if (request.GET):
        db = neo_con
        print("request : ")

        entity1 = request.GET['entity1_text']
        relation = request.GET['relation_name_text']
        entity2 = request.GET['entity2_text']
        print("entity1: {}, relation:{}, entity2: {}".format(entity1, relation, entity2))
        relation = relation.lower()
        searchResult = {}
        # 若只输入entity1,则输出与entity1有直接关系的实体和关系
        if (len(entity1) != 0 and len(relation) == 0 and len(entity2) == 0):
            searchResult = db.findRelationByEntity(entity1)
            searchResult = filter_rel(searchResult)
            if (len(searchResult) > 0):
                return render(request, 'demo/relation.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})

        # 若只输入entity2则,则输出与entity2有直接关系的实体和关系
        if (len(entity2) != 0 and len(relation) == 0 and len(entity1) == 0):
            searchResult = db.findRelationByEntity2(entity2)
            searchResult = filter_rel(searchResult)
            if (len(searchResult) > 0):
                return render(request, 'demo/relation.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})
        # 若输入entity1和relation，则输出与entity1具有relation关系的其他实体
        if (len(entity1) != 0 and len(relation) != 0 and len(entity2) == 0):
            searchResult = db.findOtherEntities(entity1, relation)
            # searchResult = sortDict(searchResult)
            if (len(searchResult) > 0):
                print(searchResult[0])
                return render(request, 'demo/relation.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})
        # 若输入entity2和relation，则输出与entity2具有relation关系的其他实体
        if (len(entity2) != 0 and len(relation) != 0 and len(entity1) == 0):
            searchResult = db.findOtherEntities2(entity2, relation)
            # searchResult = sortDict(searchResult)
            if (len(searchResult) > 0):
                return render(request, 'demo/relation.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})
        # 若输入entity1和entity2,则输出entity1和entity2之间的最短路径
        if (len(entity1) != 0 and len(relation) == 0 and len(entity2) != 0):
            searchResult = db.findRelationByEntities(entity1, entity2)
            if (len(searchResult) > 0):
                print(searchResult)
                # searchResult = sortDict(searchResult)
                return render(request, 'demo/relation.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})
        # 若输入entity1,entity2和relation,则输出entity1、entity2是否具有相应的关系
        if (len(entity1) != 0 and len(entity2) != 0 and len(relation) != 0):
            searchResult = db.findEntityRelation(entity1, relation, entity2)
            if (len(searchResult) > 0):
                return render(request, 'demo/relation.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})
        # 全为空
        if (len(entity1) != 0 and len(relation) != 0 and len(entity2) != 0):
            pass
        ctx = {'title': '<h1>暂未找到相应的匹配</h1>'}
        return render(request, 'demo/relation.html', {'ctx': ctx})

    return render(request, 'demo/relation.html', {'ctx': ctx})


# 概览界面
# 目前只展示所有的企业，按拼音排序
def show_overview(request):
    ctx = {}

    if 'node' in request.GET:
        node = request.GET['node']
        print("node: " + str(node))
        # fatherList = tree.get_father(node)
        # branchList = tree.get_branch(node)
        # leafList = tree.get_leaf(node)
        fatherList = []
        branchList = []
        ctx['node'] = "分类专题：[" + "企业" + "]"
        db = neo_con
        enterprises = db.matchAllEnterpriseName()
        leafList = []
        for e in enterprises:
            leafList.append(e['entity.name'])
        print(e)

        rownum = 4  # 一行的词条数量
        leaf = ""

        alpha_table = {}
        for alpha in range(ord('A'), ord('Z') + 1):
            alpha_table[chr(alpha)] = []

        for p in leafList:
            if p == None:
                continue
            py = ''.join(lazy_pinyin(p, style=Style.FIRST_LETTER)).upper()
            alpha = ord('A')
            for s in py:
                t = ord(s)
                if t >= ord('a') and t <= ord('z'):
                    t = t + ord('A') - ord('a')
                if t >= ord('A') and t <= ord('Z'):
                    alpha = t
                    break
            alpha_table[chr(alpha)].append(p)

        for kk in range(ord('A'), ord('Z') + 1):
            k = chr(kk)
            v = alpha_table[k]
            if len(v) == 0:
                continue
            add_num = rownum - len(v) % rownum  # 填充的数量
            add_num %= rownum
            for i in range(add_num):  # 补充上多余的空位
                v.append('')
            leaf += '<div><span class="label label-warning">&nbsp;&nbsp;' + k + '&nbsp;&nbsp;</span></div><br/>'
            for i in range(len(v)):
                if i % rownum == 0:
                    leaf += "<div class='row'>"
                leaf += '<div class="col-md-3">'
                leaf += '<p><a href="search_entity?user_text=' + v[i] + '">'
                if len(v[i]) > 10:
                    leaf += v[i][:10] + '...'
                else:
                    leaf += v[i]
                leaf += '</a></p>'
                leaf += '</div>'
                if i % rownum == rownum - 1:
                    leaf += "</div>"
            leaf += '<br/>'
        ctx['leaf'] = leaf

        # 父节点列表
        father = '<ul class="nav nav-pills nav-stacked">'
        for p in fatherList:
            father += '<li role="presentation"> <a href="overview?node='
            father += p + '">'
            father += '<i class="fa fa-hand-o-right" aria-hidden="true"></i>&nbsp;&nbsp;' + p + '</a></li>'
        father += '</ul>'
        if len(fatherList) == 0:
            father = '<p>已是最高级分类</p>'
        ctx['father'] = father

        # 非叶子节点列表
        branch = '<ul class="nav nav-pills nav-stacked">'
        for p in branchList:
            branch += '<li role="presentation"> <a href="overview?node='
            branch += p + '">'
            branch += '<i class="fa fa-hand-o-right" aria-hidden="true"></i>&nbsp;&nbsp;' + p + '</a></li>'
        branch += '</ul>'
        if len(branchList) == 0:
            branch = '<p>已是最低级分类</p>'
        ctx['branch'] = branch

        # 分类树构建
        # level_tree = tree.create_UI(node)
        level_tree = []
        ctx['level_tree'] = level_tree

    return render(request, "demo/overview.html", ctx)


#     # return HttpResponse("kkkkf")

def getNodeCard(name):
    db = neo_con
    answer = db.matchNodebyName(name)
    ctx = {}
    if answer == None:
        return ctx

    if len(answer) > 0:
        answer = answer[0]['n']
    else:
        ctx['title'] = '实体条目出现未知错误'
        return ctx
    print("answer is : " + answer['name'])

    # 获得企业的各种标签：i_tag p_tag business_scope website name等
    attributeDict = {"企业名称": 'name'}

    for item in answer.items():
        key = answer[item[0]]
        ctx[item[0]] = answer[item[0]]
    # ctx['企业名称'] = answer['name']
    # ctx['经营状态'] = answer['status']
    # ctx['地址'] = answer['address']
    # ctx['官方网站'] = answer['website']
    # ctx['经营范围'] = answer['business_scope']
    # ctx['detail'] = '企业简介'  #
    # ctx['i_tag'] = answer['i_tag']
    # ctx['p_tag'] = answer['p_tag']
    image = answer['image']

    ctx['image'] = '<img src="' + str(image) + '" alt="该条目无图片" height="100%" width="100%" >'

    text = ""  # 存的是baseInfoTable
    list = []
    if (answer['i_tag'] is not None):
        list += answer['i_tag'].split(',')
    if (answer['p_tag'] is not None):
        list += answer['p_tag'].split(',')
    for p in list:
        text += '<span class="badge bg-important">' + str(p) + '</span> '
    ctx['openTypeList'] = text  # 标签

    text = '<table class="table table-striped table-advance table-hover"> <tbody>'  # 卡片标签
    i = 0
    keyList = []
    for item in ctx.items():
        keyList.append(item[0])
    while i < len(keyList):
        # 因为是双栏展示，所以这里两次重复
        value = " "
        if i < len(keyList):
            value = ctx[keyList[i]]
        text += "<tr>"
        text += '<td><strong>' + keyList[i] + '</strong></td>'
        text += '<td>' + value + '</td>'
        i += 1

        if i < len(keyList):
            value = ctx[keyList[i]]
        if i < len(keyList):
            text += '<td><strong>' + keyList[i] + '</strong></td>'
            text += '<td>' + value + '</td>'
        else:
            text += '<td><strong>' + '</strong></td>'
            text += '<td>' + '</td>'
        i += 1
        text += "</tr>"
    text += " </tbody> </table>"
    ctx['baseInfoTable'] = text
    ctx['searchName'] = name
    return ctx


def filter_rel(res):
    ans = []
    for d in res:
        if (d['relation']['type']) in ['供应', '投资','合作','专利']:
            ans.append(d)
    return ans


def showdetail(request):
    ctx = {}
    if 'title' in request.GET:  # title待修改为name
        # 连接数据库
        # db = neo_con
        #
        # name = request.GET['title']
        # answer=db.matchNodebyName(name)
        # if answer == None:
        #     return render(request, "demo/404.html", ctx)
        #
        # if len(answer) > 0:
        #     answer = answer[0]['n']
        # else:
        #     ctx['title'] = '实体条目出现未知错误'
        #     return
        #
        # # 获得企业的各种标签：i_tag p_tag business_scope website name等
        # ctx['企业名称'] = answer['name']
        # ctx['经营状态'] = answer['status']
        # ctx['地址'] = answer['address']
        # ctx['官方网站'] = answer['website']
        # ctx['经营范围'] = answer['business_scope']
        # ctx['detail'] = '企业简介' #
        # # ctx['i_tag'] = answer['i_tag']
        # # ctx['p_tag'] = answer['p_tag']
        # image = answer['image']
        #
        # ctx['image'] = '<img src="' + str(image) + '" alt="该条目无图片" height="100%" width="100%" >'
        #
        # text = "" # 存的是baseInfoTable
        # list=answer['i_tag'].split(',')
        # list+=answer['p_tag'].split(',')
        # for p in list:
        #     text += '<span class="badge bg-important">' + str(p) + '</span> '
        # ctx['openTypeList'] = text # 标签
        #
        # text = '<table class="table table-striped table-advance table-hover"> <tbody>' # 卡片标签
        # i = 0
        # keyList = ['企业名称','经营状态','地址','官方网站','经营范围']
        # while i < len(keyList):
        #     # 因为是双栏展示，所以这里两次重复
        #     value = " "
        #     if i < len(keyList):
        #         value = ctx[keyList[i]]
        #     text += "<tr>"
        #     text += '<td><strong>' + keyList[i] + '</strong></td>'
        #     text += '<td>' + value + '</td>'
        #     i += 1
        #
        #     if i < len(keyList):
        #         value = ctx[keyList[i]]
        #     if i < len(keyList):
        #         text += '<td><strong>' + keyList[i] + '</strong></td>'
        #         text += '<td>' + value + '</td>'
        #     else:
        #         text += '<td><strong>' + '</strong></td>'
        #         text += '<td>' + '</td>'
        #     i += 1
        #     text += "</tr>"
        # text += " </tbody> </table>"
        # ctx['baseInfoTable'] = text

        # 获取词云 todo
        name = request.GET['title']
        ctx = getNodeCard(name)
        tagcloud = ""
        # taglist = wv_model.get_simi_top(answer['title'], 10)
        # for tag in taglist:
        #     tagcloud += '<a href= "./detail.html?title=' + str(tag) + '"> '
        #     tagcloud += str(tag) + "</a>"
        #			print(tag)
        ctx['tagcloud'] = tagcloud

        # 获取标签
        agri_type = ""
        # ansList = tree.get_path(answer['title'], True)
        ansList = []
        for List in ansList:
            agri_type += '<p >'
            flag = 1
            for p in List:
                if flag == 1:
                    flag = 0
                else:
                    agri_type += ' / '
                agri_type += str(p)
            agri_type += '</p>'
        if len(ansList) == 0:
            agri_type = '<p > 暂无农业类型</p>'
        ctx['agri_type'] = agri_type

        entity_type = ""
        # explain = get_explain(predict_labels[answer['title']])
        # detail_explain = get_detail_explain(predict_labels[answer['title']])
        # entity_type += '<p > [' + explain + "]: "
        # entity_type += detail_explain + "</p>"
        ctx['entity_type'] = entity_type

    else:
        return render(request, "demo/404.html", ctx)

    return render(request, "demo/detail.html", ctx)


def question_answering(request):
    ret_dict = {}
    print("question_answering")
    # 为post方法的话
    if request.GET:
        question = request.GET['question']
        db = neo_con
        result_dict, answer = db.anwserQA(question)

        ret_dict['answer'] = answer
        ret_dict['question'] = question
        ret_dict['list'] = graph_view(result_dict, answer)

        print("===========rec_dict===============")
        print(ret_dict)
    return render(request, "demo/agrquestion_answering.html", {'ret': ret_dict})


def graph_view(dict, answer):
    list = []
    for ans in answer:
        list.append({'entity1': dict['ontology'], 'rel': dict['rel'], 'entity2': ans, 'entity1_type': '植物',
                     'entity2_type': '类型'})

    return list
