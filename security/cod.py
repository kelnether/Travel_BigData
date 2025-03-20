# -*- coding: utf-8 -*-
import pymysql
import bcrypt

# 连接数据库
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    database="ctrip_data",
    charset="utf8mb4"
)
cursor = conn.cursor()

# 读取所有用户
cursor.execute("SELECT id, password FROM users")
users = cursor.fetchall()

for user_id, plain_password in users:
    if not plain_password.startswith("$2b$12$"):  # 仅对未加密的密码进行加密
        hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))

conn.commit()
cursor.close()
conn.close()

print("✅ 所有密码已加密更新！")
