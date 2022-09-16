import sys
import os
sys.path.append('..')
from model.neo4j_model import Neo4j
from toolkit.tree_API import TREE

neo_con = Neo4j()   #预加载neo4j
neo_con.connectDB()
neo_con.getQ2Cql()

filePath = os.getcwd()

enterprises = neo_con.matchAllEnterpriseName()
leafList = []
for e in enterprises:
    leafList.append(e['entity.name'])

# 读取农业层次树
tree = TREE()
# tree.read_edge(filePath + '/toolkit/micropedia_tree.txt')
# tree.read_leaf(filePath + '/toolkit/leaf_list.txt')

print('level tree load over~~~')
