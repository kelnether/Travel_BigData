# -*- coding: utf-8 -*-
import pymysql

# 连接 MySQL
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    database="ctrip_data",
    charset="utf8mb4"
)
cursor = conn.cursor()

# 用户 A 选择 天文
user_id = "UserB"
favorite_categories = ["天文馆"]

# 插入用户偏好
insert_sql = """
INSERT INTO user_preferences (user_id, category)
VALUES (%s, %s)
ON DUPLICATE KEY UPDATE category=VALUES(category);
"""

for category in favorite_categories:
    cursor.execute(insert_sql, (user_id, category))

conn.commit()
cursor.close()
conn.close()

print("✅ 用户喜好已存入 MySQL！")
