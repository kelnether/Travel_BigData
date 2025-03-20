# bigdata.py
# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, jsonify, request
import pandas as pd
import os

# 创建 Blueprint，设置 URL 前缀为 /bigdata
bigdata_bp = Blueprint('bigdata', __name__, url_prefix='/bigdata',
                         template_folder='templates', static_folder='static')

# 数据文件夹路径（可根据项目结构调整）
DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data_visitors_flowrate')

# 加载历史数据 CSV 文件（确保文件结构和列名一致）
data_july = pd.read_csv(os.path.join(DATA_FOLDER, '2018.7.csv'), encoding='gb18030')
data_aug = pd.read_csv(os.path.join(DATA_FOLDER, '2018.8.csv'), encoding='gb18030')
data_sep = pd.read_csv(os.path.join(DATA_FOLDER, '2018.9.csv'), encoding='gb18030')
data_all = pd.concat([data_july, data_aug, data_sep], ignore_index=True)
#predicted_data = pd.read_csv(os.path.join(DATA_FOLDER, 'prediction.csv'), encoding='gb18030')




@bigdata_bp.route('/')
def index():
    # 渲染大数据展示的子页面模板
    return render_template('bigdata_index.html')

@bigdata_bp.route('/api/history', methods=['GET'])
def get_history():
    # 支持通过 URL 参数过滤数据（例如：?date=2018-09-01 或 ?scenic=xxx）
    date = request.args.get('date')
    scenic = request.args.get('scenic')
    df = data_all.copy()
    if date:
        df = df[df['date'] == date]
    if scenic:
        df = df[df['scenic'] == scenic]
    return jsonify(df.to_dict(orient='records'))

