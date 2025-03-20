import requests
import csv
import time

# 目标 URL
url = 'https://m.ctrip.com/restapi/soa2/18109/json/getAttractionList?_fxpcqlniredt=09031109416854393090&x-traceID=09031109416854393090-1741158088753-267417'

# 请求头，包含 User-Agent 和 Cookies（建议抓包获取最新 Cookie）
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
}

# 保存数据的文件路径
csv_file = '/Users/kevinkel/PycharmProjects/pythonProject9/total.csv'

# 打开 CSV 文件（追加模式 "a"）
with open(csv_file, 'w', encoding="utf-8", newline='') as f:
    csvwrite = csv.writer(f)
    # 写入表头
    csvwrite.writerow([
        '城市', '景点名', '地点', '距离', '坐标', '评论数', '评论分', '热评分', '封面', '是否免费',
        '价格', '原价', '类别信息', '标签', '是否5A'
    ])

# 爬取多页数据
max_pages = 50  # 设定最大爬取页数（可以调整）
count_per_page = 10  # 每页最大记录数
district_id = 2  # 地区 ID，2 代表某个特定地区（可修改）

for page in range(1, max_pages + 1):
    print(f"正在爬取第 {page} 页数据...")

    # 组装 POST 请求参数
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
        # 发送请求
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()  # 检查 HTTP 响应码
        html = response.json()

        # 获取数据列表
        attractionList = html.get('attractionList', [])

        # 判断是否爬取到数据
        if not attractionList:
            print("数据为空，可能到达最后一页。停止爬取。")
            break  # 退出循环

        # 追加写入 CSV 文件
        with open(csv_file, 'a', encoding="utf-8", newline='') as f:
            csvwrite = csv.writer(f)

            for attraction in attractionList:
                data = attraction.get('card', {})

                city = data.get('districtName', '')
                poiName = data.get('poiName', '')
                displayField = data.get('displayField', '')
                distanceStr = data.get('distanceStr', '')

                coordinate_dict = data.get('coordinate', {})
                latitude = coordinate_dict.get('latitude', '')
                longitude = coordinate_dict.get('longitude', '')
                coordinate = f"{latitude}, {longitude}"  # 转换为字符串

                commentCount = data.get('commentCount', 0)
                commentScore = data.get('commentScore', 0)
                heatScore = data.get('heatScore', '')
                coverImageUrl = data.get('coverImageUrl', '')

                isFree = data.get('isFree', False)
                price = 0 if isFree else data.get('price', 0)
                marketPrice = 0 if isFree else data.get('marketPrice', 0)

                sightCategoryInfo = data.get('sightCategoryInfo', '')
                tagNameList = ', '.join(data.get('tagNameList', []))  # 转换为字符串
                sightLevelStr = data.get('sightLevelStr', '')

                csvwrite.writerow([
                    city, poiName, displayField, distanceStr, coordinate,
                    commentCount, commentScore, heatScore, coverImageUrl,
                    isFree, price, marketPrice, sightCategoryInfo, tagNameList, sightLevelStr
                ])

        print(f"第 {page} 页数据写入成功！")

        # 适当延迟，防止被封
        time.sleep(2)

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        break  # 发生错误时终止爬取
