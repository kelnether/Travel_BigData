import sys
from py2neo import Graph, Node, Relationship, NodeMatcher
from neo_db.config import *

with open("../raw_data/relations.txt") as f:
    graph.delete_all()  # 删除已有的所有内容
    for line in f.readlines():
        rela_array = line.strip("\n").split(",")
        print(rela_array)
        rela_array = [rela_array[0], rela_array[-1], rela_array[1]]
        graph.run("MERGE(p: Entity{Name: '%s'})" % (rela_array[0]))
        graph.run("MERGE(p: Entity{Name: '%s'})" % (rela_array[2]))
        graph.run(
            "MATCH(e: Entity), (cc: Entity) \
            WHERE e.Name='%s' AND cc.Name='%s'\
            CREATE(e)-[r:%s{relation: '%s'}]->(cc)\
            RETURN r" % (rela_array[0], rela_array[2], rela_array[1], rela_array[1])
        )
    data = graph.run("match(n) return n.Name")
    data = list(data)
    print(data)
