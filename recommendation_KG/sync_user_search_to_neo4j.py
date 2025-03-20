# -*- coding: utf-8 -*-
import pymysql
from neo4j import GraphDatabase

# 连接 Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "20031129"))

# 连接 MySQL
conn = pymysql.connect(host="localhost", user="root", password="123456", database="ctrip_data", charset="utf8mb4")
cursor = conn.cursor()

# 获取用户搜索历史
cursor.execute("SELECT user_id, poiName FROM user_visits")
user_searches = cursor.fetchall()
cursor.close()
conn.close()

# 插入用户搜索历史到 Neo4j
def add_user_search(tx, user_id, poiName):
    query = """
    MERGE (u:User {id: $user_id})
    MERGE (a:Attraction {name: $poiName})
    MERGE (u)-[:SEARCHED]->(a)
    """
    tx.run(query, user_id=user_id, poiName=poiName)

with driver.session() as session:
    for user_id, poiName in user_searches:
        # 转换 user_id 为字符串，确保类型一致
        session.write_transaction(add_user_search, str(user_id), poiName)

print("✅ 用户搜索记录已同步到 Neo4j！")
driver.close()
