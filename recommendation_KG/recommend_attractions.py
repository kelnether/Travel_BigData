# -*- coding: utf-8 -*-
from neo4j import GraphDatabase

# 连接 Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "20031129"))

# 推荐景点（基于景点相似性、用户偏好类别和用户搜索记录的模糊匹配）
def recommend_attractions(tx, user_id):
    print(f"\n🔍 查询用户 {user_id} 的推荐景点...")

    # 检查用户是否存在
    user_check_query = "MATCH (u:User {id: $user_id}) RETURN u.id LIMIT 1"
    user_check_result = tx.run(user_check_query, user_id=user_id).single()
    if not user_check_result:
        print(f"❌ 用户 {user_id} 在 Neo4j 中不存在！")
        return []

    print(f"✅ 用户 {user_id} 存在，开始模糊匹配推荐...")

    # 主推荐查询：
    # 1. 根据用户喜欢的类别与景点所属类别进行模糊匹配（距离 <= 0.15，即相似度 ≥ 0.85）。
    # 2. 排除用户已搜索过的景点（模糊匹配）。
    # 3. OPTIONAL MATCH 匹配用户搜索记录与候选景点之间的 SIMILAR 关系（无方向匹配），累计加分。
    # 4. 额外对用户搜索记录与候选景点名称进行模糊匹配，计算平均补分（1 - 距离）。
    query = """
MATCH (u:User {id: $user_id})
MATCH (a:Attraction)-[:BELONGS_TO]->(cat:Category),
      (u)-[:LIKES]->(pref:Category)
WHERE apoc.text.jaroWinklerDistance(cat.name, pref.name) <= 0.15
  AND NOT EXISTS {
      MATCH (u)-[:SEARCHED]->(s:Attraction)
      WHERE apoc.text.jaroWinklerDistance(s.name, a.name) <= 0.15
  }
OPTIONAL MATCH (u)-[:SEARCHED]->(searched:Attraction), (searched)-[sim:SIMILAR]-(a)
WITH a, a.score AS base_score, SUM(sim.weight) AS similar_bonus
OPTIONAL MATCH (u)-[:SEARCHED]->(s2:Attraction)
WHERE apoc.text.jaroWinklerDistance(s2.name, a.name) <= 0.15
WITH a, base_score, COALESCE(similar_bonus, 0) AS similar_bonus,
     AVG(1 - apoc.text.jaroWinklerDistance(s2.name, a.name)) AS search_similarity
RETURN a.name AS Recommendation, 
       (base_score + similar_bonus + COALESCE(search_similarity, 0)) AS final_score
ORDER BY final_score DESC
LIMIT 5
    """
    results = tx.run(query, user_id=user_id).data()

    # 如果主查询没有结果，则使用默认推荐（加入随机因子，避免每次固定推荐）
    if not results:
        print("❌ 未找到匹配推荐，使用默认随机推荐...")
        default_query = """
MATCH (a:Attraction)
WHERE a.score IS NOT NULL
WITH a, a.score + rand() AS combinedScore
RETURN a.name AS Recommendation, a.score AS final_score
ORDER BY combinedScore DESC
LIMIT 5
        """
        results = tx.run(default_query).data()

    recommendations = [(record["Recommendation"], record["final_score"]) for record in results]
    print(f"✅ 为用户 {user_id} 推荐的景点：{recommendations}")
    return recommendations

# 测试单一用户（确保 user_id 类型为字符串）
if __name__ == "__main__":
    user_list = ["6"]
    with driver.session() as session:
        for user in user_list:
            print("\n===============================")
            recommendations = session.execute_read(recommend_attractions, user)
            print(f"🎯 用户 {user} 推荐景点：{recommendations}")
            print("===============================\n")
    driver.close()
