import os,sys
sys.path.append('../')

from toolkit.pre_load import neo_con, leafList

def graph_view(dict, answer):
    list = []
    for ans in answer:
        list.append({'entity1': dict['ontology'], 'rel': dict['rel'], 'entity2': ans, 'entity1_type': '植物', 'entity2_type': '类型'})

    return list

# 问题模板：
# 1. 你好，请问广州友田机电设备有限公司的经营范围是什么？（地址）
# 2. 跟湖南汉华京电清洁能源科技有限公司具有竞争关系的公司有哪些？
# 3. 跟建筑业相关的公司有哪些？
if __name__ == '__main__':
    db = neo_con
    while True:
        print("==============请输入问题========================")
        question = input()
        result_dict, answer = db.anwserQA(question)

        print("==============结果输出为============================")
        print(result_dict)
        print(answer)
