#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 旅游推荐模块：调用 OpenAI API 生成旅游景点推荐。
"""

import os
from openai import OpenAI


def generate_recommendation(prompt):
    """
    根据用户输入的提示生成旅游景点推荐。
    使用 OpenAI 的 GPT 模型完成推荐生成。
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    # 示例中直接写入 api_key（建议配置为环境变量）
    api_key = "sk-ff81ddd218354252a57622881af85bb8"
    if not api_key:
        return "未设置 OPENAI_API_KEY，请在环境变量中配置。"

    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"请根据以下提示为用户生成旅游景点推荐：{prompt}。同时确保在文本最后另起一行，在‘【推荐列表】：’的后面输出你推荐的所有的景点，以json数组格式"},
                {"role": "user", "content": f"请为旅游推荐生成景点建议，考虑景点特色和用户体验：{prompt}。同时确保在文本最后另起一行，在‘【推荐列表】：’的后面输出你推荐的所有的景点，以json数组格式"}
            ],
            temperature=1.5,
            stream=False
        )
        recommendation = response.choices[0].message.content
        return recommendation
    except Exception as e:
        return f"生成旅游推荐时出错：{str(e)}"
