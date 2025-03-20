# -*- coding: utf-8 -*-
import requests
import pymysql
import time

# 配置 MySQL 数据库连接
db = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    database="ctrip_data",
    charset="utf8mb4"
)
cursor = db.cursor()

# 携程 API URL
url = 'https://m.ctrip.com/restapi/soa2/18109/json/getAttractionList?_fxpcqlniredt=09031109416854393090&x-traceID=09031109416854393090-1741158088753-267417'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
}

# 设定爬取参数
max_pages = 50
count_per_page = 10
district_id = 2  # 修改为想爬取的地区 ID

# **更新 SQL 语句，增加 description**
insert_sql = """
INSERT INTO attractions_test (
    city, poiName, displayField, distanceStr, latitude, longitude, commentCount, commentScore, heatScore,
    coverImageUrl, isFree, price, marketPrice, sightCategoryInfo, tagNameList, sightLevelStr, description
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
) ON DUPLICATE KEY UPDATE
    commentCount=VALUES(commentCount), commentScore=VALUES(commentScore), heatScore=VALUES(heatScore),
    price=VALUES(price), marketPrice=VALUES(marketPrice), coverImageUrl=VALUES(coverImageUrl),
    description=VALUES(description);
"""

# 爬取多页数据并写入 MySQL
for page in range(1, max_pages + 1):
    print(f"正在爬取第 {page} 页数据...")

    data = {
        "index": page,
        "count": count_per_page,
        "sortType": 1,
        "isShowAggregation": True,
        "districtId": district_id,
        "scene": "DISTRICT",
        "pageId": "214062",
        "traceId": "14f9745c-92ad-f5c5-07bb-171293c80647",
        "extension": [
            {"name": "osVersion", "value": "10"},
            {"name": "deviceType", "value": "windows"}
        ],
        "filter": {"filterItems": []},
        "crnVersion": "2020-09-01 22:00:45",
        "isInitialState": True,
        "head": {
            "cid": "09031015313388236487",
            "ctok": "",
            "cver": "1.0",
            "lang": "01",
            "sid": "8888",
            "syscode": "09",
            "auth": "",
            "xsid": "",
            "extension": []
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        html = response.json()

        attractionList = html.get('attractionList', [])

        if not attractionList:
            print("数据为空，可能到达最后一页。停止爬取。")
            break

        for attraction in attractionList:
            data = attraction.get('card', {})

            city = data.get('districtName', '')
            poiName = data.get('poiName', '')
            displayField = data.get('displayField', '')
            distanceStr = data.get('distanceStr', '')

            coordinate_dict = data.get('coordinate', {})
            latitude = coordinate_dict.get('latitude', None)
            longitude = coordinate_dict.get('longitude', None)

            commentCount = data.get('commentCount', 0)
            commentScore = data.get('commentScore', 0)
            heatScore = data.get('heatScore', 0)
            coverImageUrl = data.get('coverImageUrl', '')

            isFree = data.get('isFree', False)
            price = 0 if isFree else data.get('price', 0)
            marketPrice = 0 if isFree else data.get('marketPrice', 0)

            sightCategoryInfo = data.get('sightCategoryInfo', '')
            tagNameList = ', '.join(data.get('tagNameList', []))
            sightLevelStr = data.get('sightLevelStr', '')

            # **尝试获取 `description`**
            description = data.get('description', 'No description available')

            # 执行 SQL 插入
            cursor.execute(insert_sql, (
                city, poiName, displayField, distanceStr, latitude, longitude, commentCount,
                commentScore, heatScore, coverImageUrl, isFree, price, marketPrice,
                sightCategoryInfo, tagNameList, sightLevelStr, description
            ))

        # 提交事务
        db.commit()

        print(f"第 {page} 页数据写入成功！")
        time.sleep(2)  # 适当延迟，防止被封

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        break

# 关闭数据库连接
cursor.close()
db.close()
print("爬取完成，数据库已更新。")
