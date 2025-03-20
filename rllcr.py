import pandas as pd
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

# 读取 CSV 文件
file_path = "data_visitors_flowrate/2018.7.csv"
df = pd.read_csv(file_path, encoding="GB18030")

# 转换时间格式

# 确保时间格式正确
df["时间"] = pd.to_datetime(df["时间"], errors="coerce")

# 填充缺失值
df["客流数"].fillna(0, inplace=True)
df["舒适度"].fillna("未知", inplace=True)
print(df.head())

# 遍历 DataFrame 插入数据
insert_sql = """
INSERT INTO attraction_visits (poiName, visit_date, visitors, comfort_level, capacity)
VALUES (%s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE visitors=VALUES(visitors), comfort_level=VALUES(comfort_level);
"""

for _, row in df.iterrows():
    print(row)
    cursor.execute(insert_sql, (
        row["景区名称"],  # poiName
        row["时间"].date(),  # visit_date
        row["客流数"],  # visitors
        row["舒适度"],  # comfort_level
        0
    ))

# 提交事务
conn.commit()
cursor.close()
conn.close()

print("数据已成功插入 MySQL！")
