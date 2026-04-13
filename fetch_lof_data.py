#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOF基金数据抓取脚本
从天天基金网获取LOF基金数据
"""

import requests
import json
import time
import random
from datetime import datetime

def fetch_lof_funds():
    """
    获取LOF基金数据
    """
    # 天天基金LOF基金接口（示例）
    urls = [
        'http://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx?t=1&lx=2&letter=&gsid=&text=&sort=zdf,desc&page=1,100&feature=|&dt=123456789',
        'http://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx?t=1&lx=2&letter=&gsid=&text=&sort=zdf,desc&page=2,100&feature=|&dt=123456789'
    ]
    
    all_funds = []
    
    for url in urls:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'http://fund.eastmoney.com/lof.html'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            # 解析返回的数据
            content = response.text
            if content.startswith('var db='):
                # 提取JSON数据部分
                start = content.find('datas:') + 7
                end = content.find('];', start) + 1
                data_str = content[start:end]
                
                # 转换为Python对象
                funds_data = json.loads(data_str)
                all_funds.extend(funds_data)
                
            time.sleep(random.uniform(1, 2))  # 避免请求过于频繁
            
        except Exception as e:
            print(f"获取数据失败: {e}")
            continue
    
    return all_funds

def format_fund_data(funds):
    """
    格式化基金数据为前端需要的格式
    """
    formatted_funds = []
    
    for fund in funds:
        try:
            fund_info = {
                'code': fund[0],  # 基金代码
                'name': fund[1],  # 基金名称
                'nav': float(fund[3]),  # 单位净值
                'acc_nav': float(fund[4]),  # 累计净值
                'daily_change': float(fund[8]),  # 当日涨跌幅
                'premium_rate': round((float(fund[3]) - float(fund[6])) / float(fund[6]) * 100, 2) if float(fund[6]) > 0 else 0,  # 溢价率估算
                'limit_amount': '暂无限制'  # 限购数量（需要额外接口获取）
            }
            formatted_funds.append(fund_info)
        except (IndexError, ValueError, TypeError):
            continue
    
    return formatted_funds

def save_to_json(funds_data, filename='lof_funds.json'):
    """
    保存数据到JSON文件
    """
    output = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_count': len(funds_data),
        'funds': funds_data
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"成功保存 {len(funds_data)} 只LOF基金数据到 {filename}")

if __name__ == '__main__':
    print("正在获取LOF基金数据...")
    funds = fetch_lof_funds()
    formatted_funds = format_fund_data(funds)
    save_to_json(formatted_funds, 'data/lof_funds.json')
    print("数据获取完成！")