import sys
sys.path.append('../')
from neo_db.config import graph

q_word = [
    ['妻子','老婆','妻','夫人'],
    ['丈夫','老公','夫','生父'],
    ['父亲','爸爸','父','生父'],
    ['母亲','妈妈','母','生母'],
    ['祖父','爷爷'],
    ['祖母','奶奶'],
    ['儿子'],
    ['女儿'],
    ['孩子'],
    ['弟弟','弟'],
    ['妹妹','妹']
]

search_word = [
    ['妻子','老婆','妻','夫人'],
    ['丈夫','老公','夫','生父'],
    ['父亲','爸爸','父','生父'],
    ['母亲','妈妈','母','生母'],
    ['祖父', '爷爷'],
    ['祖母','奶奶'],
    ['儿子','长子','次子','幺子','子'],
    ['女儿','长女','次女','幺女'],
    ['孩子','儿子','长子','次子','幺子','女儿','长女','次女','幺女'],
    ['弟弟', '弟'],
    ['妹妹', '妹']
]

def query(name):
    data = graph.run(
    "match(p )-[r]->(n:Entity{Name:'%s'}) return  p.Name,r.relation,n.Name\
        Union all\
    match(p:Entity {Name:'%s'}) -[r]->(n) return p.Name, r.relation, n.Name"
        % (name, name)
    )
    data = list(data)
    return get_json_data(data)


def get_json_data(data):
    json_data={'data':[],"links":[]}
    d=[]
    for i in data:
        d.append(i['p.Name'])
        d.append(i['n.Name'])
        d=list(set(d))
    name_dict={}
    count=0
    for j in d:
        j_array=j.split("_")
    
        data_item={}
        name_dict[j_array[0]]=count
        count+=1
        data_item['name']=j_array[0]
        json_data['data'].append(data_item)
    for i in data:
        link_item = {}
        link_item['source'] = name_dict[i['p.Name']]
        link_item['target'] = name_dict[i['n.Name']]
        link_item['value'] = i['r.relation']
        json_data['links'].append(link_item)

    return json_data


def get_KGQA_answer(array):
    # print('array', array)
    data_array=[]
    for i in range(1):
        if i==0:
            name=array[0]
        else:
            name=data_array[-1]['p.Name']
        flag = False
        for k in range(0,len(q_word)):
            for word in q_word[k]:
                if word==array[i+1]:
                    for search in search_word[k]:
                        data = graph.run(
                            "match(n:Entity)-[:`%s`]->(m:Entity) where m.Name='%s' return n.Name" % (
                                search, name)
                        )
                        data = list(data)
                        data_array.extend(data)
                    flag = True
                    break
            if flag==True:
                break
        if flag==False:
            data = graph.run(
                "match(n:Entity)-[:`%s`]->(m:Entity) where m.Name='%s' return n.Name" % (
                    array[i+1], name)
            )
            data = list(data)
            data_array.extend(data)
        # print("data", data)
        # print("==="*36)

    return data_array


if __name__ == '__main__':
    a1 = ['贾宝玉', '爷爷', '的']
    res = get_KGQA_answer(a1)
    for i in res:
        print(i[0])
