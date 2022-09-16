# encoding=utf-8

"""
@desc:
设置问题模板，为每个模板设置对应的SPARQL语句。demo提供如下模板：

"""
from refo import finditer, Predicate, Star, Any, Disjunction
import re

class W(Predicate):
    def __init__(self, token=".*", pos=".*"):
        self.token = re.compile(token + "$")
        self.pos = re.compile(pos + "$")
        super(W, self).__init__(self.match)

    def match(self, word):
        m1 = self.token.match(word.token.decode("utf-8"))
        m2 = self.pos.match(word.pos)
        return m1 and m2


class Rule(object):
    def __init__(self, condition_num, condition=None, action=None):
        assert condition and action
        self.condition = condition
        self.action = action
        self.condition_num = condition_num

    def apply(self, sentence):
        matches = []
        for m in finditer(self.condition, sentence):
            # condition为rule的实体规则，sentence为这个句子
            # m为refo.match.Match对象,i和j为start和end，对应着句子中匹配到condition的初始位置和结束位置
            i, j = m.span()
            # matches存放了与模板相对应的实体类型之间的句子，以及token
            matches.extend(sentence[i:j])

        result_dict, cql = self.action(matches)

        return result_dict, cql, self.condition_num


class QuestionSet:
    def __init__(self):
        pass

    @staticmethod
    def get_attribute_bycompany(word_object):
        # 1. 你好，请问深圳市艾特软件有限公司的经营范围（地址）是什么？
        attribute_dict = {"经营范围": "business_scope", "标签": "i_tag", "地址": "address"}
        cql = None
        result_dict = {}

        company_name = None
        attribute = ""
        for w in word_object:
            if w.pos == pos_company:
                company_name = w.token.decode('utf-8')
            if w.pos == pos_comAttribute:
                attribute = w.token.decode('utf-8')

        if attribute:
            cql = u"MATCH (n:Enterprise{name:'" + company_name + "'}) RETURN n." + attribute_dict[attribute]
        result_dict['ontology'] = company_name
        result_dict['rel'] = attribute
        return result_dict ,cql

    @staticmethod
    def get_relation_company(word_object):
#         2. 跟普元信息技术股份有限公司具有合作关系公司有哪些？
#       MATCH (a:Enterprise{name:"普元信息技术股份有限公司"})-[:cooperation]-(cooper) RETURN cooper.name
        relation_dict = {"Compete": "竞争关系", "cooperation":"合作关系"}
        cql = None

        result_dict = {}
        company_name = None
        relation = ""
        for w in word_object:
            if w.pos == pos_company:
                company_name = w.token.decode('utf-8')
            if w.pos == pos_rel_cpt:
                relation = "Compete"
            if w.pos == pos_rel_prv:
                relation = "cooperation"

        if relation:
            cql = u"MATCH (n:Enterprise{name:'" + company_name + "'}) -[:" + relation +"]-(a) RETURN a.name"
            result_dict['rel'] = relation_dict[relation]

        result_dict['ontology'] = company_name
        return  result_dict, cql

    @staticmethod
    def get_companies_byindustry(word_object):
#         3. 跟建筑业相关的公司有哪些？
#           match (entity:Enterprise) where entity.i_tag=~'.*建筑业.*' return entity limit 30
        cql = None

        result_dict = {}
        industry = ""
        for w in word_object:
            if w.pos == pos_industry:
                industry = w.token.decode('utf-8')

        cql = u"match (entity:Enterprise) where entity.i_tag=~'.*" + industry + ".*' return entity.name limit 30"

        result_dict['ontology'] = industry
        result_dict['rel'] = "相关"
        return  result_dict, cql



# TODO 定义关键词
pos_company = "company"
pos_comAttribute = "comattr"
pos_rel_cpt = "compete"
pos_rel_prv = "cooperation"
pos_industry = "industry"

company_entity = (W(pos=pos_company))
comAttribute_entity = (W(pos=pos_comAttribute))
industry_entity = (W(pos=pos_industry))

singer = (W("歌手") | W("歌唱家") | W("艺术家") | W("艺人") | W("歌星"))
album = (W("专辑") | W("合辑") | W("唱片"))
song = (W("歌") | W("歌曲"))

category = (W("类型") | W("种类"))
several = (W("多少") | W("几部"))

higher = (W("大于") | W("高于"))
lower = (W("小于") | W("低于"))
compare = (higher | lower)

birth = (W("生日") | W("出生") + W("日期") | W("出生"))
birth_place = (W("出生地") | W("出生"))
english_name = (W("英文名") | W("英文") + W("名字"))
introduction = (W("介绍") | W("是") + W("谁") | W("简介"))
person_basic = (birth | birth_place | english_name | introduction)

song_content = (W("歌词") | W("歌") | W("内容"))
release = (W("发行") | W("发布") | W("发表") | W("出"))
movie_basic = (introduction | release)

when = (W("何时") | W("时候"))
where = (W("哪里") | W("哪儿") | W("何地") | W("何处") | W("在") + W("哪"))

com_attribute = (W("地址") | W("经营范围") | W("标签"))
com_relation = (W("竞争关系") | W("合作关系") | W("供应商关系"))
# TODO 问题模板/匹配规则

"""
1.周杰伦的专辑都有什么？
2.晴天的歌词是什么？
3.周杰伦的生日是哪天？
4.以父之名是哪个专辑里的歌曲？
5.叶惠美是哪一年发行的？

1. 广州友田机电设备有限公司的经营范围（地址）是什么？
2. 跟湖南汉华京电清洁能源科技有限公司具有竞争关系的公司有哪些？
3. 跟建筑业相关的公司有哪些？
"""
rules = [
    # Rule(condition_num=2, condition=person_entity + Star(Any(), greedy=False) + album + Star(Any(), greedy=False), action=QuestionSet.has_album),
    # Rule(condition_num=2, condition=song_entity + Star(Any(), greedy=False) + song_content + Star(Any(), greedy=False),
    #      action=QuestionSet.has_content),
    # Rule(condition_num=2, condition=person_entity + Star(Any(), greedy=False) + introduction + Star(Any(), greedy=False),
    #      action=QuestionSet.person_inroduction),
    # Rule(condition_num=2, condition=song_entity + Star(Any(), greedy=False) + album + Star(Any(), greedy=False),
    #      action=QuestionSet.stay_album),
    # Rule(condition_num=2, condition=song_entity + Star(Any(), greedy=False) + release + Star(Any(), greedy=False),
    #      action=QuestionSet.release_album),
    Rule(condition_num=2,
         condition=company_entity + Star(Any(), greedy=False) + com_attribute + Star(Any(), greedy=False),
         action=QuestionSet.get_attribute_bycompany),
    Rule(condition_num=2,
         condition=company_entity + Star(Any(), greedy=False) + com_relation + Star(Any(), greedy=False),
         action=QuestionSet.get_relation_company),
    Rule(condition_num=1,
         condition=industry_entity + Star(Any(), greedy=False),
         action=QuestionSet.get_companies_byindustry)

]

if __name__ == '__main__':
    question = input()
    result = com_relation.match(question)
    print(result)

