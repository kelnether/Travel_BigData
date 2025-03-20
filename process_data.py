# -*- coding: utf-8 -*-
import pandas as pd
import os


def preprocess_data():
    """
    1. 读取 GB18030 编码的 CSV 文件（包含 2018.7, 2018.8, 2018.9 三个文件）
    2. 合并数据并重命名列
    3. 将“时间”字段转换为 datetime 类型，并提取出日期和小时
    4. 清洗数据：删除缺失关键字段的记录、转换客流数为数值型
    5. 按景点和小时聚合客流数
    """
    # 数据文件所在文件夹路径
    DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data_visitors_flowrate')

    # 读取 CSV 数据（GB18030 编码）
    data_july = pd.read_csv(os.path.join(DATA_FOLDER, '2018.7.csv'), encoding='gb18030')
    data_aug = pd.read_csv(os.path.join(DATA_FOLDER, '2018.8.csv'), encoding='gb18030')
    data_sep = pd.read_csv(os.path.join(DATA_FOLDER, '2018.9.csv'), encoding='gb18030')

    # 合并所有数据
    data_all = pd.concat([data_july, data_aug, data_sep], ignore_index=True)

    # 重命名列，将中文列名转换为英文以便后续处理
    data_all = data_all.rename(columns={
        '景区名称': 'scenic',
        '客流数': 'visitor_count',
        '时间': 'time'
    })

    # 将 time 列转换为 datetime 类型
    data_all['time'] = pd.to_datetime(data_all['time'], errors='coerce')

    # 清洗数据：删除缺失 scenic、visitor_count 或 time 的记录
    data_all = data_all.dropna(subset=['scenic', 'visitor_count', 'time'])

    # 将 visitor_count 转换为数值型（如遇异常数据会转为 NaN，然后删除）
    data_all['visitor_count'] = pd.to_numeric(data_all['visitor_count'], errors='coerce')
    data_all = data_all.dropna(subset=['visitor_count'])

    # 生成日期和小时字段
    data_all['date'] = data_all['time'].dt.date.astype(str)  # 日期字段转为字符串形式
    data_all['hour'] = data_all['time'].dt.hour

    # 按景点和小时聚合数据：统计每个景点各小时的总客流数
    aggregated = data_all.groupby(['scenic', 'hour'])['visitor_count'].sum().reset_index()

    return data_all, aggregated


# 调试：独立运行该模块测试预处理结果
if __name__ == '__main__':
    raw_data, agg_data = preprocess_data()
    print("预处理后的原始数据:")
    print(raw_data.head())
    print("\n按景点和小时聚合的数据:")
    print(agg_data.head())
