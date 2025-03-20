from pymongo import MongoClient
# 设置字体，不然无法显示中文
from pylab import *

mpl.rcParams['font.sans-serif'] = ['SimHei']

conn = MongoClient('localhost', port=27017)
db = conn.QuNaEr # 库
table = db.qunaer_51 # 表

result = table.find().sort([('count', -1)]).limit(15)
# x,y轴数据
x_arr = []  # 景区名称
y_arr = []  # 销量
for i in result:
    x_arr.append(i['name'])
    y_arr.append(i['count'])

"""
去哪儿月销量排行榜
"""
plt.bar(x_arr, y_arr, color='rgb')  # 指定color，不然所有的柱体都会是一个颜色
plt.gcf().autofmt_xdate() # 旋转x轴，避免重叠
plt.xlabel(u'景点名称')  # x轴描述信息
plt.ylabel(u'月销量')  # y轴描述信息
plt.title(u'拉钩景点月销量统计表')  # 指定图表描述信息
plt.ylim(0, 4000)  # 指定Y轴的高度
plt.savefig('去哪儿月销售量排行榜')  # 保存为图片
plt.show()
