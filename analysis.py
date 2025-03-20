from flask import Blueprint, render_template, jsonify, request
import pandas as pd
import os
from process_data import preprocess_data  # 假设预处理函数在 process_data.py 中

analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis',
                         template_folder='templates', static_folder='static')

# 预处理数据并缓存
raw_data, aggregated_data = preprocess_data()

@analysis_bp.route('/')
def index():
    return render_template('analysis_index.html')

@analysis_bp.route('/api/history', methods=['GET'])
def get_history():
    """
    返回预处理后的历史数据，可通过 URL 参数进行过滤，例如：?date=2018-08-31 或 ?scenic=东方假日田园
    """
    date = request.args.get('date')
    scenic = request.args.get('scenic')
    df = raw_data.copy()
    if date:
        df = df[df['date'] == date]
    if scenic:
        df = df[df['scenic'] == scenic]
    return jsonify(df.to_dict(orient='records'))

@analysis_bp.route('/api/aggregated', methods=['GET'])
def get_aggregated():
    """
    返回按景点和小时聚合的客流数据
    """
    return jsonify(aggregated_data.to_dict(orient='records'))

@analysis_bp.route('/api/scenic_names', methods=['GET'])
def get_scenic_names():
    """
    返回所有的景点名称列表，用于前端下拉选择
    """
    scenic_names = raw_data['scenic'].unique().tolist()
    return jsonify(scenic_names)

@analysis_bp.route('/api/daily_total', methods=['GET'])
def daily_total():
    """
    返回按日期聚合的总客流量，如果传入景点参数，则统计该景点每日的客流量趋势
    """
    df = raw_data.copy()
    scenic = request.args.get('scenic')
    if scenic:
        df = df[df['scenic'] == scenic]
    daily_total = df.groupby('date')['visitor_count'].sum().reset_index()
    return jsonify(daily_total.to_dict(orient='records'))

@analysis_bp.route('/api/scenic_distribution', methods=['GET'])
def scenic_distribution():
    """
    返回各景点的总客流量分布（所有日期合计），用于展示各景点占比情况
    """
    df = raw_data.copy()
    scenic_total = df.groupby('scenic')['visitor_count'].sum().reset_index()
    return jsonify(scenic_total.to_dict(orient='records'))
