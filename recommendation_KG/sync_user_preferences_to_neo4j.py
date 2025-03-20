# -*- coding: utf-8 -*-
import pymysql
from neo4j import GraphDatabase

# 连接 Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "20031129"))

# 连接 MySQL
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    database="ctrip_data",
    charset="utf8mb4"
)
cursor = conn.cursor()

# 获取用户偏好
cursor.execute("SELECT user_id, category FROM user_preferences")
user_preferences = cursor.fetchall()
cursor.close()
conn.close()

# 插入数据到 Neo4j
def add_user_preference(tx, user_id, category):
    query = """
    MERGE (u:User {id: $user_id})
    MERGE (c:Category {name: $category})
    MERGE (u)-[:LIKES]->(c)
    """
    tx.run(query, user_id=user_id, category=category)

with driver.session() as session:
    for user_id, category in user_preferences:
        # 同样转换 user_id 为字符串
        session.write_transaction(add_user_preference, str(user_id), category)

print("✅ 用户偏好已同步到 Neo4j！")
driver.close()
