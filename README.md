# “乐游上海”--基于flask的上海旅游景点客流的分析及推荐网页

感谢 K 圣开源
## 项目综述
本项目是基于flask开发的大数据分析项目，以web为载体展示。
主体数据分为上海市内景点数据和绝大多数景点的客流量数据。
### 数据来源
```txt
景点：携程；客流量：上海市政府数据平台
```
页面内容及功能涵盖：大数据主页大屏、用户主页及登录注册、景点搜索、景点推荐（基于由搜索记录、用户偏好、景点自身数据构建的知识图谱）、deepseek对话推荐（生成的文本可自动跳转查询）、DashBoard（查看所有数据分析维度）、客流量预测。

## Requirements.txt
```txt
numpy>=1.21.0
pandas>=1.3.0
scipy>=1.7.0
matplotlib>=3.4.0
statsmodels>=0.12.2
```

# 项目各页面及对于功能介绍
## 1.大数据主页

## 2.用户主页及注册细节

## 3.景点搜索及景点详情页

## 4.景点个性化推荐及四周的推荐小窗

## 5.Deepseek对话及景点自动点击跳转

## 6.DashBoard

## 7.客流量预测【为了好写预测模型的ppt和报告硬加的】


·
·
·
# 部署流程及细节
## 景点数据爬虫
部署数据库后，运行pachong.py

## 客流量大数据分析
analysis.py【针对客流量数据的图表展示】
process_data
 
## 部署流程
程序入口：app.py
子程序（blueprint）：analysis.py



## MySQL 配置语句

以下是用于创建数据库及相关数据表的 MySQL 配置语句：

```sql
CREATE DATABASE IF NOT EXISTS ctrip_data DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ctrip_data;

CREATE TABLE IF NOT EXISTS attractions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    poiName VARCHAR(255),
    displayField VARCHAR(255),
    distanceStr VARCHAR(50),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    commentCount INT,
    commentScore FLOAT,
    heatScore FLOAT,
    coverImageUrl TEXT,
    isFree BOOLEAN,
    price DECIMAL(10,2),
    marketPrice DECIMAL(10,2),
    sightCategoryInfo VARCHAR(255),
    tagNameList TEXT,
    sightLevelStr VARCHAR(50),
    UNIQUE KEY unique_spot (city, poiName)  -- 避免插入重复数据
);

CREATE TABLE IF NOT EXISTS attraction_visits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    poiName VARCHAR(255) NOT NULL,   -- 景点名称
    visit_date DATE NOT NULL,        -- 访问日期
    visitors INT NOT NULL,           -- 游客数
    comfort_level VARCHAR(50),       -- 舒适度（如：舒适、较舒适、一般、拥挤）
    capacity INT,       -- 最大承载量（可调整）
    UNIQUE KEY (poiName, visit_date) -- 防止重复数据
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,   -- 用户编号（自动递增）
    username VARCHAR(50) NOT NULL UNIQUE, -- 用户名（唯一）
    password VARCHAR(255) NOT NULL       -- 加密后的密码
);
insert into users value (1,'userA','123456');


CREATE TABLE user_preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

drop table user_preferences;

CREATE TABLE IF NOT EXISTS user_visits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    poiName VARCHAR(255) NOT NULL,
    UNIQUE KEY (user_id, poiName)  -- 避免重复搜索记录
);


CREATE TABLE IF NOT EXISTS attractions_test (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(100),
    poiName VARCHAR(255),
    displayField VARCHAR(255),
    distanceStr VARCHAR(50),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    commentCount INT,
    commentScore FLOAT,
    heatScore FLOAT,
    coverImageUrl TEXT,
    isFree BOOLEAN,
    price DECIMAL(10,2),
    marketPrice DECIMAL(10,2),
    sightCategoryInfo VARCHAR(255),
    tagNameList TEXT,
    sightLevelStr VARCHAR(50),
    description TEXT,
    UNIQUE KEY unique_spot (city, poiName)  -- 避免插入重复数据
);

ALTER TABLE attractions
ADD COLUMN description TEXT;
```




