# coding:utf-8
from py2neo import Graph, Node, Relationship, NodeMatcher

# 1.广州友田机电设备有限公司的经营范围（地址）是什么？
def get_attribute_bycompany(matcher,attribute,company_name):
    node = matcher.match("EnterpriseItem", name=company_name).first()
    return node[attribute]

from learn_code.QA.GongYingLian_QA import Question2Cql




if __name__ == '__main__':
    graph = Graph("http://localhost:7473",auth=("neo4j","123"))
    matcher = NodeMatcher(graph)
    q2s = Question2Cql.Question2Cql(['./qa_demo/external_dict/gongyinglian.txt'])

    my_query = None

    while True :
        # 广州友田机电设备有限公司的经营范围
        question = input()
        words, my_query = q2s.get_cql(question)

        node = graph.run(my_query[0]).data()
        if len(node) == 0:
            print('I don\'t know. :(')
        elif len(node) == 1:
            result = list(node[0].values())
            print(result[0])
        else:
            output = ''
            for n in node:
                result = list(n.values())
                output += result[0] + u'、'
            print(output[0:-1])

        # print(result)

        print ('#' * 100)

# node = matcher.match("EnterpriseItem", name="广州友田机电设备有限公司").first()
# print(get_attribute_bycompany(matcher, "business_scope","广州友田机电设备有限公司"))

# items = graph.run("MATCH (n:EnterpriseItem) RETURN n LIMIT 25").data()
# item1 = matcher.match("EnterpriseItem", i_tag="制造业,金属制品业,").first()
# item2 = matcher.match(matcher.match('EnterpriseItem').where("name = 广州友田机电设备有限公司"))
# print(item1['i_tag'])




