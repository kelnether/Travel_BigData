import requests
import csv
url = 'https://m.ctrip.com/restapi/soa2/18109/json/getAttractionList?_fxpcqlniredt=09031109416854393090&x-traceID=09031109416854393090-1741158088753-267417'
data = {"index":1,"count":10,"sortType":1,"isShowAggregation":True,"districtId":1,"scene":"DISTRICT","pageId":"214062","traceId":"14f9745c-92ad-f5c5-07bb-171293c80647","extension":[{"name":"osVersion","value":"10"},{"name":"deviceType","value":"windows"}],"filter":{"filterItems":[]},"crnVersion":"2020-09-01 22:00:45","isInitialState":True,"head":{"cid":"09031015313388236487","ctok":"","cver":"1.0","lang":"01","sid":"8888","syscode":"09","auth":"","xsid":"","extension":[]}}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
    'Cookie':"'UBT_VID=1740017699369.0c3bpfhGNb55; Hm_lvt_a8d6737197d542432f4ff4abc6e06384=1740017699; Hm_lpvt_a8d6737197d542432f4ff4abc6e06384=1740017699; HMACCOUNT=4FA425AF4B977771; GUID=09031109416854393090; MKT_CKID=1740017699505.fafcx.9myc; _gcl_aw=GCL.1740017700.CjwKCAiAn9a9BhBtEiwAbKg6fg4ox2y5rHhiOhkZHMjNbA9k-xYJbwhRbXGv3Ta7pTawJRwJMmsH-xoC_1MQAvD_BwE; _gcl_dc=GCL.1740017700.CjwKCAiAn9a9BhBtEiwAbKg6fg4ox2y5rHhiOhkZHMjNbA9k-xYJbwhRbXGv3Ta7pTawJRwJMmsH-xoC_1MQAvD_BwE; _gcl_gs=2.1.k1$i1740017698$u167964915; _jzqco=%7C%7C%7C%7C1740017699645%7C1.981415477.1740017699506.1740017699506.1740017699506.1740017699506.1740017699506.0.0.0.1.1; _RSG=KOKcPGrJWY73REV3_fGREA; _RDG=2817e0fa81ed5c2c3133e7a228da9b28e4; _RGUID=78a04f54-1999-4614-a39b-429fc37ce6c3; manualclose=1; ibulanguage=CN; ibulocale=zh_cn; cookiePricesDisplayed=CNY; _ga_9BZF483VNQ=GS1.1.1740017699.1.0.1740017710.0.0.0; nfes_isSupportWebP=1; _RF1=112.64.195.42; _ga=GA1.2.539513455.1740017700; _gid=GA1.2.1260133094.1741158004; _lizard_LZ=WDJRQUL02IuPmdOCjprhw+YFNoeZM5gl4fnB6HEbTa8q1XSyGKVxAkst-i397czv; login_type=0; login_uid=8219C8DE1059DB05D910340AAE7C1F1F; DUID=u=8B025069FDAA69D9ED4EB42CE1ADEA25&v=0; IsNonUser=F; AHeadUserInfo=VipGrade=10&VipGradeName=%BB%C6%BD%F0%B9%F3%B1%F6&UserName=&NoReadMessageCount=0; _ga_5DVRDQD429=GS1.2.1741158004.2.1.1741158069.0.0.0; _ga_B77BES1Z8Z=GS1.2.1741158004.2.1.1741158069.60.0.0; _ubtstatus=%7B%22vid%22%3A%221740017699369.0c3bpfhGNb55%22%2C%22sid%22%3A5%2C%22pvid%22%3A9%2C%22pid%22%3A0%7D; _pd=%7B%22_o%22%3A2%2C%22s%22%3A5%2C%22_s%22%3A0%7D; _bfa=1.1740017699369.0c3bpfhGNb55.1.1741158082514.1741158088725.5.11.214062'"
}

html = requests.post(url, headers=headers, json=data).json()
attractionList = html['attractionList']
print(attractionList)
for attraction in attractionList:
    data = attraction['card']
    print(data)
    commentCount = data['commentCount']
    commentScore = data['commentScore']
    coordinate = [data['coordinate']['latitude'], data['coordinate']['longitude']]
    coverImageUrl = data.get('coverImageUrl', '')
    # 距离
    distanceStr = data.get('distanceStr', '')
    # 地点
    displayField = data.get('displayField', None)
    heatScore = data.get('heatScore', '')
    # 景点名
    poiName = data['poiName']
    isFree = data['isFree']
    if isFree:
        price = 0
        # 原价
        marketPrice = 0
    else:
        price = data.get('price', 0)
        # 原价
        marketPrice = data.get('marketPrice', 0)
    # 类别信息
    sightCategoryInfo = data.get('sightCategoryInfo', '')
    # 标签
    tagNameList = data.get('tagNameList', '')
    # 5a
    sightLevelStr = data.get('sightLevelStr', None)

f = open('csv/全国各景点全.csv', 'w', encoding="utf-8", newline='')
csvwrite = csv.writer(f)
csvwrite.writerow(['城市', '景点名', '地点', '距离', '坐标', '评论数','评论分','热评分','封面','是否免费','价格','原价','类别信息','标签','是否5A'])
#csvwrite.writerow([city,poiName,displayField,distanceStr,coordinate,commentCount,commentScore,heatScore,coverImageUrl,isFree,price,marketPrice,sightCategoryInfo,tagNameList,sightLevelStr])