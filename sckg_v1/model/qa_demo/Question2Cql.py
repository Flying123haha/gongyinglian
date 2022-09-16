# encoding=utf-8
# @desc: 将自然语言转为cql查询语句

from model.qa_demo import question_template

from model.qa_demo import word_tagger



class Question2Cql:
    def __init__(self, dict_paths):
        # 获取外词典的词性
        self.tw = word_tagger.Tagger(dict_paths)
        # 获取模板规则
        self.rules = question_template.rules

    def get_cql(self, question):
        # 进行语义解析，找到匹配的模板，返回对应的SPARQL查询语句
        # 获取各个词的词性,并将其转为二进制token
        word_objects = self.tw.get_word_objects(question)
        queries = []
        result_dict = {}
        for rule in self.rules:
            result_dict, query, i = rule.apply(word_objects)
            if query and query[0]:
                queries.append(query)
                break

        return result_dict,word_objects, queries[0]



