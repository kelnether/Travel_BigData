#wjz快来学
#感谢K圣开源

#mysql配置语句如下：
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


