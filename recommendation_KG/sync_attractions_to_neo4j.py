# -*- coding: utf-8 -*-
import pymysql
from neo4j import GraphDatabase

# 连接 Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "20031129"))

# 连接 MySQL
conn = pymysql.connect(host="localhost", user="root", password="123456", database="ctrip_data", charset="utf8mb4")
cursor = conn.cursor()

# 获取景点类别和评分
cursor.execute("SELECT poiName, tagNameList, commentScore FROM attractions")
attractions = cursor.fetchall()
cursor.close()
conn.close()

# 插入景点数据到 Neo4j
def add_attraction(tx, poiName, category, score):
    category = category if category else "其他"  # 确保类别不为空
    query = """
    MERGE (a:Attraction {name: $poiName})
    MERGE (c:Category {name: $category})
    MERGE (a)-[:BELONGS_TO]->(c)
    SET a.score = $score
    """
    tx.run(query, poiName=poiName, category=category, score=score)

with driver.session() as session:
    for poiName, category, score in attractions:
        session.execute_write(add_attraction, poiName, category, score)

print("✅ 景点数据（包含评分）已同步到 Neo4j！")

# 创建景点相似性关系
def create_similarity_edges(tx):
    query = """
   MATCH (a1:Attraction)-[:BELONGS_TO]->(c:Category),
      (a2:Attraction)-[:BELONGS_TO]->(c)
WHERE id(a1) < id(a2)  
MERGE (a1)-[r:SIMILAR]->(a2)
ON CREATE SET r.weight = (a1.score + a2.score) / 2 

    """
    tx.run(query)

with driver.session() as session:
    session.execute_write(create_similarity_edges)

print("✅ 已创建景点相似性关系！")
driver.close()
