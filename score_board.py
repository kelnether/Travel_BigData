import pymysql
import pandas as pd

# 建立数据库连接
conn = pymysql.connect(host='localhost', user='user', password='password', db='your_db', charset='utf8mb4')

# 查询数据
query = "SELECT id, city, poiName, sightLevelStr, commentScore, heatScore, maxCapacity, trafficAccessibility FROM attractions"
df = pd.read_sql(query, conn)

# 关闭数据库连接
conn.close()

# 景区等级转换函数
def convert_sight_level(level):
    mapping = {'5A': 100, '4A': 80, '3A': 60, '2A': 40, '1A': 20}
    return mapping.get(level, 0)

# 应用转换函数
df['sightLevelScore'] = df['sightLevelStr'].apply(convert_sight_level)

# 指标标准化处理（用户评分、最大承载量、交通通达度）
df['userScore'] = df['commentScore'] / 5.0 * 100  # 用户评分最大5.0标准化到100

df['historicalVisitorFlowScore'] = df['heatScore']  

df['capacityScore'] = (df['maxCapacity'] / df['maxCapacity'].max()) * 100

df['trafficScore'] = (df['trafficAccessibility'] / df['trafficAccessibility'].max()) * 100

# 计算综合热度得分
df['comprehensiveHeatScore'] = (
    df['sightLevelScore'] * 0.30 +
    df['userScore'] * 0.25 +
    df['historicalVisitorFlowScore'] * 0.20 +
    df['capacityScore'] * 0.15 +
    df['trafficScore'] * 0.10
)

# 显示结果
print(df[['id', 'city', 'poiName', 'comprehensiveHeatScore']])
