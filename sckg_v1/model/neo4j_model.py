from py2neo import Graph, Node, Relationship, cypher, Path, NodeMatcher

from .qa_demo import Question2Cql


class Neo4j():
    graph = None

    def __init__(self):
        print("create neo4j class ...")

    def connectDB(self):
        self.graph = Graph("http://10.23.23.17:7473", auth=("neo4j", "123"))
        print("Neo4J已连接...")

    def getQ2Cql(self):
        self.matcher = NodeMatcher(self.graph)
        # self.q2s = Question2Cql.Question2Cql(['D:/A/study/python_code/ai_study/sckg/sckg_v1/model/qa_demo/external_dict/gongyinglian.txt'])
        self.q2s = Question2Cql.Question2Cql(
            ['/tmp/pycharm_project_257/sckg_v1/model/qa_demo/external_dict/gongyinglian.txt'])

    # todo:完善查询逻辑，主要是实体-关系-实体的查询，因为，实体有多种类型，关系也有多种类型，看哪些需要补充
    def matchItembyTitle(self, value):
        sql = "MATCH (n:Item { title: '" + str(value) + "' }) return n;"
        answer = self.graph.run(sql).data()
        return answer

    def matchEnterpreisebyName(self, value):
        sql = "MATCH (entity:Enterprise { name: '" + str(value) + "' }) return entity;"
        sql = "match (entity:Enterprise) where entity.name=~'.*" + str(value) + ".*' return entity"
        print("this sql:", sql)
        answer = self.graph.run(sql).data()
        print("this answer", answer)
        return answer

    def matchAllEnterpriseName(self):
        sql = "MATCH (entity:Enterprise) return entity.name;"
        answer = self.graph.run(sql).data()
        return answer

    # 根据title值返回互动百科item
    def matchHudongItembyTitle(self, value):
        sql = "MATCH (n:HudongItem { title: '" + str(value) + "' }) return n;"
        try:
            answer = self.graph.run(sql).data()
        except:
            print(sql)
        return answer

    # SCKG:根据节点name查找节点
    def matchNodebyName(self, value):
        # sql = "MATCH (n:HudongItem { title: '" + str(value) + "' }) return n;"
        sql = "match (n{name:'" + str(value) + "'}) return n"
        sql = "match (n:Enterprise) where n.name=~'.*" + str(value) + ".*' return n"
        try:
            answer = self.graph.run(sql).data()
        except:
            print(sql)
        return answer

    # 根据entity的名称返回新闻
    def findNewsByEntity(self, entity1):
        sql = "match (n:News) where n.enterpriseName = \"" + str(entity1) + "\" return n"
        answer = self.graph.run(sql).data()
        # if(answer is None):
        # 	answer = self.graph.run("MATCH (n1:NewNode {title:\""+entity1+"\"})- [rel] -> (n2) RETURN n1,rel,n2" ).data()
        return answer

    # 根据entity的名称返回关系
    def getEntityRelationbyEntity(self, value):
        answer = self.graph.run("MATCH (entity1) - [relation] -> (entity2)  WHERE entity1.name = \"" + str(
            value) + "\" RETURN relation,entity2").data()
        return answer

    # 查找entity1及其对应的关系（与getEntityRelationbyEntity的差别就是返回值不一样）
    def findRelationByEntity(self, entity1):
        sql = "match (entity1:Enterprise)- [relation] -> (entity2) where entity1.name=~'.*" + str(entity1) + ".*' " \
                                                                                                             "RETURN entity1,relation,entity2"

        answer = self.graph.run(sql).data()
        # answer = self.graph.run("MATCH (entity1 {name:\"" + str(entity1) + "\"})- [relation] -> (entity2)"
        #                                                                    " RETURN entity1,relation,entity2").data()
        # if(answer is None):
        # 	answer = self.graph.run("MATCH (entity1:NewNode {title:\""+entity1+"\"})- [rel] -> (entity2) RETURN entity1,rel,entity2" ).data()
        return answer

    # 查找entity2及其对应的关系
    def findRelationByEntity2(self, entity1):
        sql = "match (entity1)- [relation] -> (entity2:Enterprise) where entity2.name=~'.*" + str(entity1) + ".*' " \
                                                                                                             "RETURN entity1,relation,entity2"
        answer = self.graph.run(sql).data()
        # answer = self.graph.run("MATCH (entity1)- [relation] -> (entity2 {name:\"" + str(entity1) + "\"}) RETURN entity1,relation,entity2").data()

        # if(answer is None):
        # 	answer = self.graph.run("MATCH (entity1)- [rel] -> (entity2:NewNode {title:\""+entity1+"\"}) RETURN entity1,rel,entity2" ).data()
        return answer

    # 根据entity1和关系查找enitty2
    def findOtherEntities(self, entity, relation):
        if (relation == '客户'):  # entity的客户即entity-[supply]->entity2
            relation = '竞争'
        answer = self.graph.run("MATCH (entity1 {name:\"" + str(entity) + "\"})- [relation {type:\"" + str(
            relation) + "\"}] -> (entity2) RETURN entity1,relation,entity2").data()
        # if(answer is None):
        #	answer = self.graph.run("MATCH (entity1:NewNode {title:\"" + entity + "\"})- [rel:RELATION {type:\""+relation+"\"}] -> (entity2) RETURN entity1,rel,entity2" ).data()

        return answer

    # 根据entity2和关系查找enitty1
    def findOtherEntities2(self, entity, relation):
        if (relation == '竞争'):  # 查询entity1-[竞争]->entity2的结果是一致的
            answer = self.graph.run("MATCH (entity1 {name:\"" + str(entity) + "\"})- [relation {type:\"" + str(
                relation) + "\"}] -> (entity2) RETURN entity1,relation,entity2").data()
        else:
            if (relation == '客户'):  # 这里的逻辑是entity1-[supply]->entity 谁的客户是entity 即谁供应entity
                relation = '供应'
            answer = self.graph.run(
                "MATCH (entity1)- [relation {type:\"" + str(relation) + "\"}] -> (entity2 {name:\"" + str(
                    entity) + "\"}) RETURN entity1,relation,entity2").data()
        return answer

    # 根据两个实体查询它们之间的最短路径
    def findRelationByEntities(self, entity1, entity2):
        answer = self.graph.run("MATCH (p1{name:\"" + str(entity1) + "\"}),(p2{name:\"" + str(
            entity2) + "\"}),p=shortestpath((p1)-[relation:RELATION*]-(p2)) RETURN relation").evaluate()
        # answer = self.graph.run("MATCH (p1:HudongItem {title:\"" + entity1 + "\"})-[rel:RELATION]-(p2:HudongItem{title:\""+entity2+"\"}) RETURN p1,p2").data()

        if (answer is None):
            answer = self.graph.run(
                "MATCH (p1{title:\"" + str(entity1) + "\"}),(p2:NewNode {title:\"" + str(
                    entity2) + "\"}),p=shortestpath((p1)-[relation:RELATION*]-(p2)) RETURN p").evaluate()
        if (answer is None):
            answer = self.graph.run("MATCH (p1:NewNode {title:\"" + str(entity1) + "\"}),(p2:HudongItem{title:\"" + str(
                entity2) + "\"}),p=shortestpath((p1)-[relation:RELATION*]-(p2)) RETURN p").evaluate()
        if (answer is None):
            answer = self.graph.run("MATCH (p1:NewNode {title:\"" + str(entity1) + "\"}),(p2:NewNode {title:\"" + str(
                entity2) + "\"}),p=shortestpath((p1)-[relation:RELATION*]-(p2)) RETURN p").evaluate()
        # answer = self.graph.data("MATCH (entity1:HudongItem {title:\"" + entity1 + "\"})- [rel] -> (entity2:HudongItem{title:\""+entity2+"\"}) RETURN entity1,rel,entity2" )
        # if(answer is None):
        #	answer = self.graph.data("MATCH (entity1:HudongItem {title:\"" + entity1 + "\"})- [rel] -> (entity2:NewNode{title:\""+entity2+"\"}) RETURN entity1,rel,entity2" )
        # if(answer is None):
        #	answer = self.graph.data("MATCH (entity1:NewNode {title:\"" + entity1 + "\"})- [rel] -> (entity2:HudongItem{title:\""+entity2+"\"}) RETURN entity1,rel,entity2" )
        # if(answer is None):
        #	answer = self.graph.data("MATCH (entity1:NewNode {title:\"" + entity1 + "\"})- [rel] -> (entity2:NewNode{title:\""+entity2+"\"}) RETURN entity1,rel,entity2" )
        relationDict = []
        if (answer is not None):
            for x in answer:
                tmp = {}
                start_node = x.start_node
                end_node = x.end_node
                tmp['entity1'] = start_node
                tmp['entity2'] = end_node
                tmp['relation'] = x
                relationDict.append(tmp)
        return relationDict

    # 查询数据库中是否有对应的实体-关系匹配
    def findEntityRelation(self, entity1, relation, entity2):

        answer = self.graph.run(
            "MATCH (entity1:HudongItem {title:\"" + str(entity1) + "\"})- [relation:RELATION {type:\"" + str(
                relation) + "\"}] -> (entity2:HudongItem{title:\"" + entity2 + "\"}) RETURN entity1,relation,entity2").data()
        if (answer is None):
            answer = self.graph.run(
                "MATCH (entity1:HudongItem {title:\"" + str(entity1) + "\"})- [relation:RELATION {type:\"" + str(
                    relation) + "\"}] -> (entity2:NewNode{title:\"" + entity2 + "\"}) RETURN entity1,relation,entity2").data()
        if (answer is None):
            answer = self.graph.run(
                "MATCH (entity1:NewNode {title:\"" + str(entity1) + "\"})- [relation:RELATION {type:\"" + str(
                    relation) + "\"}] -> (entity2:HudongItem{title:\"" + entity2 + "\"}) RETURN entity1,relation,entity2").data()
        if (answer is None):
            answer = self.graph.run(
                "MATCH (entity1:NewNode {title:\"" + str(entity1) + "\"})- [relation:RELATION {type:\"" + str(
                    relation) + "\"}] -> (entity2:NewNode{title:\"" + entity2 + "\"}) RETURN entity1,relation,entity2").data()

        return answer

    def anwserQA(self, question):
        ontology, words, my_query = self.q2s.get_cql(question)

        node = self.graph.run(my_query).data()
        result = []
        if len(node) == 0:
            result.append('I don\'t know. :(')
        elif len(node) == 1:
            result = list(node[0].values())
            print(result)
        else:
            for n in node:
                output = list(n.values())
                result.append(output[0])
                # output += result[0] + u'、'
            # result = output[0:-1]

        return ontology, result

    def getNews(self, entity):
        sql = " match (n:Enterprise{name:\"" + str(entity) + "\"})-[relation]->(s:N_news) return s"
        answer = self.graph.run(sql).data()
        return answer
