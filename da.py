from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS

spark = SparkSession.builder.appName("TourAnalysis").getOrCreate()
# 假设有用户-景点评分数据 user_ratings.csv -> (userId, spotId, rating)
data = spark.read.csv("hdfs://.../user_ratings.csv", header=True, inferSchema=True)
# 协同过滤训练推荐模型
als = ALS(userCol="userId", itemCol="spotId", ratingCol="rating", coldStartStrategy="drop")
model = als.fit(data)
# 为指定用户生成前5个景点推荐
user_id = 123
recommendations = model.recommendForAllUsers(5).filter(f"userId = {user_id}")
recommendations.show()
# 输出: [userId=123, recommendations=[(spotA, scoreA), (spotB, scoreB), ...]]
