import subprocess  # 📌 用于运行外部 Python 文件
import sys

import bcrypt
import pymysql
from flask import Flask, redirect, url_for, render_template, request, jsonify, session

from ai_recommendation import generate_recommendation
from analysis import analysis_bp
from bigdata import bigdata_bp

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Flask session


# 📌 连接 MySQL
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="123456",
        database="ctrip_data",
        charset="utf8mb4"
    )


# 确保 Python 解释器使用 UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

app.register_blueprint(bigdata_bp)
app.register_blueprint(analysis_bp)


# 📌 1. 直接运行 Neo4j 相关 Python 文件
def run_script(script_name):
    try:
        result = subprocess.run(["python", script_name], capture_output=True, text=True, check=True)
        print(f"✅ 运行 {script_name} 成功")
        return result.stdout  # 获取脚本返回结果
    except subprocess.CalledProcessError as e:
        print(f"❌ 运行 {script_name} 失败: {e}")
        return None


@app.context_processor
def inject_logged_in():
    return dict(logged_in=("user_id" in session))


# 📌 2. 主页（带导航栏）
@app.route('/')
def index_tem():
    return redirect('http://localhost:3001/#/index')


'''
def index():
    return render_template("index.html", logged_in="user_id" in session)
'''


@app.route('/index_vue')
def index_vue():
    return render_template("index_vue.html", logged_in="user_id" in session)


# 📌 3. 渲染注册页面
@app.route('/register')
def register_page():
    return render_template("register.html")


@app.route('/register_api', methods=['POST'])
def register_api():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    preferences = data.get("preferences")  # 确保接收的是列表

    if not username or not password or not preferences:
        return jsonify({"error": "用户名、密码和偏好不能为空"}), 400

    # 📌 加密密码
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # **1. 插入用户信息**
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        conn.commit()

        # **2. 获取用户 ID**
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]

        # **3. 确保 `preferences` 为列表**
        if isinstance(preferences, str):
            preferences = [preferences]  # 如果是单个值，转换为列表

        # **4. 插入用户偏好（多条数据）**
        for category in preferences:
            cursor.execute("INSERT INTO user_preferences (user_id, category) VALUES (%s, %s)", (user_id, category))

        conn.commit()
    except pymysql.IntegrityError:
        return jsonify({"error": "❌ 用户名已存在！"}), 409
    finally:
        cursor.close()
        conn.close()

    print(f"✅ 用户 {username} 注册成功，偏好类别: {preferences}")

    # **5. 运行同步脚本，将偏好存入 Neo4j**
    run_script("recommendation_KG/sync_user_preferences_to_neo4j.py")

    return jsonify({"message": "✅ 注册成功！"}), 201


# 📌 4. 渲染登录页面
@app.route('/login')
def login_page():
    return render_template("login.html")


@app.route('/login_api', methods=['POST'])
def login_api():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
        session["user_id"] = user[0]
        return jsonify({"message": "✅ 登录成功！", "user_id": user[0]}), 200
    else:
        return jsonify({"error": "❌ 用户名或密码错误！"}), 401


# 📌 5. 处理用户登出
@app.route('/logout')
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))


# 📌 6. 渲染搜索页面（仅登录用户可访问）
@app.route('/search', methods=['GET'])
def search_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))

    # 从 URL 查询参数中获取景点名称
    poiName = request.args.get("poiName", "").strip()

    # 如果存在查询内容，则进行搜索
    if poiName:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT poiName, sightCategoryInfo, commentScore, coverImageUrl 
            FROM attractions 
            WHERE poiName LIKE %s 
            LIMIT 5;
        """
        cursor.execute(query, (f"%{poiName}%",))
        spot_info_list = cursor.fetchall()
        cursor.close()
        conn.close()
        # 渲染模板时将查询条件和结果传入
        return render_template("search.html", poiName=poiName, results=spot_info_list)
    else:
        # 没有查询内容，显示空白的搜索页面
        return render_template("search.html", results=[])


# 📌 7. 处理搜索 API，返回搜索结果和推荐
@app.route('/search_api', methods=['POST'])
def search_api():
    if "user_id" not in session:
        return jsonify({"error": "未登录用户无法搜索！"}), 403

    data = request.get_json()
    user_id = session["user_id"]
    poiName = data.get("poiName").strip()  # 去除前后空格

    if not poiName:
        return jsonify({"error": "请输入景点名称"}), 400

    print(f"🔍 用户 {user_id} 搜索景点: {poiName}")  # Debug 输出

    conn = get_db_connection()
    cursor = conn.cursor()

    # **1. 记录搜索历史**
    insert_sql = """
    INSERT INTO user_visits (user_id, poiName)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE poiName=VALUES(poiName);
    """
    cursor.execute(insert_sql, (user_id, poiName))
    conn.commit()

    # **2. 进行模糊查询**
    select_sql = """
    SELECT poiName, sightCategoryInfo, commentScore, coverImageUrl, id 
    FROM attractions 
    WHERE poiName LIKE %s 
    LIMIT 5;
    """
    cursor.execute(select_sql, (f"%{poiName}%",))
    spot_info_list = cursor.fetchall()
    cursor.close()
    conn.close()

    # **3. 运行外部推荐脚本**
    run_script("recommendation_KG/sync_user_search_to_neo4j.py")  # 更新搜索历史
    recommendation_output = run_script("recommendation_KG/recommend_attractions.py")  # 获取推荐列表

    # **4. 解析推荐景点**
    recommended_spots = []
    if recommendation_output:
        lines = recommendation_output.split("\n")
        for line in lines:
            if "✅ 为" in line and "推荐的景点" in line:
                raw_list = line.split("：")[-1].strip()
                try:
                    recommended_spots = eval(raw_list)  # 解析成 Python 列表
                except Exception as e:
                    print("❌ 解析推荐列表失败", e)
                break

    recommended_spot_names = [spot[0] for spot in recommended_spots]  # 提取景点名称

    # **5. 从数据库获取推荐景点完整信息**
    conn = get_db_connection()
    cursor = conn.cursor()
    recommendations_info = []

    if recommended_spot_names:
        placeholders = ', '.join(['%s'] * len(recommended_spot_names))  # 适配 SQL 语法
        query = f"""
        SELECT poiName, sightCategoryInfo, commentScore, coverImageUrl, id 
        FROM attractions 
        WHERE poiName IN ({placeholders});
        """
        cursor.execute(query, tuple(recommended_spot_names))
        recommendations_info = cursor.fetchall()

    cursor.close()
    conn.close()

    # **6. 返回 JSON 结果**
    return jsonify({
        "message": f"✅ 搜索成功，找到 {len(spot_info_list)} 个相关景点。",
        "found": bool(spot_info_list),
        "spots": [
            {
                "name": spot[0],
                "category": spot[1],
                "score": spot[2],
                "image": spot[3],
                "id": spot[4]
            }
            for spot in spot_info_list
        ],
        "recommendations": [
            {
                "name": rec[0],
                "category": rec[1],
                "score": rec[2],
                "image": rec[3],
                "id": rec[4]
            }
            for rec in recommendations_info
        ]
    }), 200


# 在你的 app.py 中添加下面的路由：
@app.route('/recommendations')
def recommendations_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("recommendations.html")


# 📌 7.1 添加推荐映射 API（单独推荐页面调用）
@app.route('/recommendations_api', methods=['POST'])
def recommendations_api():
    if "user_id" not in session:
        return jsonify({"error": "未登录用户无法获取推荐！"}), 403

    user_id = session["user_id"]

    # 运行推荐脚本获取推荐列表
    recommendation_output = run_script("recommendation_KG/recommend_attractions.py")

    recommended_spots = []
    if recommendation_output:
        lines = recommendation_output.split("\n")
        for line in lines:
            if "✅ 为" in line and "推荐的景点" in line:
                raw_list = line.split("：")[-1].strip()
                try:
                    recommended_spots = eval(raw_list)
                except Exception as e:
                    print("❌ 解析推荐列表失败", e)
                break

    recommended_spot_names = [spot[0] for spot in recommended_spots]

    # 从数据库获取推荐景点完整信息
    conn = get_db_connection()
    cursor = conn.cursor()
    recommendations_info = []
    if recommended_spot_names:
        placeholders = ', '.join(['%s'] * len(recommended_spot_names))
        query = f"""
        SELECT poiName, sightCategoryInfo, commentScore, coverImageUrl, id
        FROM attractions
        WHERE poiName IN ({placeholders});
        """
        cursor.execute(query, tuple(recommended_spot_names))
        recommendations_info = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify({
        "recommendations": [
            {
                "name": rec[0],
                "category": rec[1],
                "score": rec[2],
                "image": rec[3],
                "id": rec[4]
            }
            for rec in recommendations_info
        ]
    }), 200


# 📌 8. 景点详情页面
@app.route("/attraction/<int:spot_id>")
def attraction_page(spot_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT id, poiName, sightCategoryInfo, commentScore, coverImageUrl, description
        FROM attractions 
        WHERE id = %s 
        LIMIT 1
    """
    cursor.execute(query, (spot_id,))
    spot_info = cursor.fetchone()
    cursor.close()
    conn.close()

    if not spot_info:
        return "❌ 景点信息未找到！", 404

    attraction_data = {
        "id": spot_info[0],
        "name": spot_info[1],
        "category": spot_info[2],
        "score": spot_info[3],
        "image": spot_info[4],
        "description": spot_info[5] or "暂无介绍。"
    }

    return render_template("attraction.html", attraction=attraction_data)


# 渲染提问页面
# 📌 新增：渲染 AI 推荐页面
@app.route('/recommendation_ai')
def recommendation_ai_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("recommendation_ai.html")


# 📌 新增：处理 AI 推荐 API 调用
@app.route('/recommendation_ai_api', methods=['POST'])
def recommendation_ai_api():
    if "user_id" not in session:
        return jsonify({"error": "未登录用户无法调用推荐！"}), 403

    data = request.get_json()
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "提示不能为空！"}), 400

    # 调用 AI 生成旅游推荐
    recommendation = generate_recommendation(prompt)
    return jsonify({"recommendation": recommendation}), 200


def get_user_preferences_from_mysql(user_id):
    """从 MySQL 查询用户偏好，并构造偏好相关的节点和边"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT category FROM user_preferences WHERE user_id = %s", (user_id,))
    preferences = cursor.fetchall()
    cursor.close()
    conn.close()

    nodes = []
    edges = []
    for row in preferences:
        category = row[0]
        cat_node_id = f"cat_{category}"
        # 避免重复添加相同类别节点
        if not any(n["data"]["id"] == cat_node_id for n in nodes):
            nodes.append({"data": {"id": cat_node_id, "label": category}})
        edges.append({
            "data": {
                "id": f"user_{user_id}_{cat_node_id}",
                "source": f"user_{user_id}",
                "target": cat_node_id
            }
        })
    return nodes, edges

def get_user_searches_from_mysql(user_id):
    """从 MySQL 查询用户搜索记录，并构造搜索记录相关的节点和边"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT poiName FROM user_visits WHERE user_id = %s", (user_id,))
    searches = cursor.fetchall()
    cursor.close()
    conn.close()

    nodes = []
    edges = []
    for row in searches:
        poi = row[0]
        poi_node_id = f"poi_{poi}"
        # 避免重复添加相同景点节点
        if not any(n["data"]["id"] == poi_node_id for n in nodes):
            nodes.append({"data": {"id": poi_node_id, "label": poi}})
        edges.append({
            "data": {
                "id": f"user_{user_id}_{poi_node_id}",
                "source": f"user_{user_id}",
                "target": poi_node_id
            }
        })
    return nodes, edges


@app.route('/profile')
def profile():
    if "user_id" not in session:
        return redirect(url_for("login_page"))

    user_id = session["user_id"]
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取用户基本信息（仅有 id, username, password）
        cursor.execute(
            "SELECT id, username, password FROM users WHERE id = %s",
            (user_id,)
        )
        user_row = cursor.fetchone()
        if not user_row:
            cursor.close()
            conn.close()
            return "用户信息不存在", 404

        # 由于数据库中没有 email、registration_date、avatar_url、bio 字段，设置默认值
        user_data = {
            "id": user_row[0],
            "username": user_row[1],
            "email": "未提供",  # 默认邮箱
            "registration_date": "未知",  # 默认注册日期
            "avatar_url": "static/pic/HEIF Image.png",  # 默认头像路径
            "bio": "暂无简介"  # 默认个人简介
        }

        # -----------------------
        # 1. 获取搜索记录(用于“浮动气泡”)
        # -----------------------
        # 这里以 user_visits 表中的 poiName 为用户搜索过的景点关键字
        cursor.execute(
            "SELECT poiName FROM user_visits WHERE user_id = %s ORDER BY id DESC LIMIT 20",
            (user_id,)
        )
        visits = cursor.fetchall() or []
        # 将搜索关键词提取出来，供前端的气泡展示
        user_data["search_history"] = [row[0] for row in visits]

        # -----------------------
        # 2. 获取其他动态信息(右侧显示)
        # -----------------------
        # 也可以直接复用上面的 visits 数据
        # 这里示例：把前 10 条记录当作“活动动态”
        user_data["activities"] = [
            {"description": "搜索景点：" + row[0]}
            for row in visits[:10]
        ]

        # 如果有旧的 favorites 等，也可在此处设置为空或在数据库中查询
        user_data["favorites"] = []

        # 如果需要知识图谱数据
        graph_preferences = get_user_preferences_from_mysql(user_id)
        graph_searches = get_user_searches_from_mysql(user_id)

    except Exception as e:
        print("Error loading profile:", e)
        return "服务器内部错误", 500
    finally:
        cursor.close()
        conn.close()

    print(graph_preferences)
    print(graph_searches)

    # 在渲染模板时，将 search_history 传给前端
    return render_template(
        "profile.html",
        user=user_data,
        graph_preferences=graph_preferences,
        graph_searches=graph_searches
    )

if __name__ == '__main__':
    app.run(debug=True)
