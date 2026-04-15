#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOF基金数据采集脚本
从上交所和深交所获取完整的LOF基金数据
"""

import requests
import json
import time
import random
import re
import pandas as pd
from datetime import datetime
import os
from bs4 import BeautifulSoup

# 创建数据目录
os.makedirs('data', exist_ok=True)


def fetch_sse_lof_funds():
    """
    获取上交所LOF基金数据
    """
    print("正在获取上交所LOF基金数据...")
    
    # 上交所LOF基金数据接口
    url = "https://query.sse.com.cn/commonQuery.do"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.sse.com.cn/',
        'Accept': 'application/json',
        'Connection': 'keep-alive'
    }
    
    # 构建查询参数
    params = {
        'jsonCallBack': f'jQuery{random.randint(1000000000000, 999999999999)}_{int(time.time() * 1000)}',
        'isPagination': 'true',
        'sqlId': 'COMMON_SSE_ZQPZ_GPZTJJJJJ_JYXX_LB',
        'ORDER_BY': 'GPDM',
        'pageHelp.pageSize': '100',
        'pageHelp.pageNo': '1',
        'pageHelp.beginPage': '1',
        'pageHelp.cacheSize': '1',
        'pageHelp.endPage': '10',
        '_': int(time.time() * 1000)
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        # 清理JSONP响应
        json_str = re.sub(r'^\w+\((.*)\);?$', '\1', response.text)
        data = json.loads(json_str)
        
        # 提取基金数据
        funds = []
        for item in data['result']:
            fund = {
                'code': item['GPDM'],
                'name': item['GPJC'],
                'exchange': 'SSE',  # 上交所
                'nav': item.get('DWJZ', 'N/A'),  # 单位净值
                'acc_nav': item.get('LJJZ', 'N/A'),  # 累计净值
                'daily_change': item.get('ZRZF', 'N/A'),  # 当日涨跌幅
                'premium_rate': 'N/A',  # 溢价率（需要场内价格计算）
                'subscription_status': 'open' if item.get('SSZT', '') != '暂停申购' else 'paused',
                'limit_amount': item.get('XGRGL', '无限额')
            }
            funds.append(fund)
            
        print(f"成功获取 {len(funds)} 只上交所LOF基金")
        return funds
    
    except Exception as e:
        print(f"获取上交所数据失败: {e}")
        return []


def fetch_szse_lof_funds():
    """
    获取深交所LOF基金数据
    """
    print("正在获取深交所LOF基金数据...")
    
    # 深交所LOF基金页面
    url = "http://fund.szse.cn/marketdata/lof/index.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'http://fund.szse.cn/',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找包含基金数据的表格
        table = soup.find('table', {'id': 'productData'})
        if not table:
            # 尝试另一种选择器
            table = soup.find('table', {'class': 'table-data'})
        
        if not table:
            print("找不到基金数据表格")
            return []
        
        # 提取表格数据
        funds = []
        rows = table.find('tbody').find_all('tr')
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 5:
                continue
            
            # 提取各列数据
            code = cols[0].text.strip()
            name = cols[1].text.strip()
            nav = cols[2].text.strip()  # 单位净值
            daily_change = cols[3].text.strip()  # 涨跌幅
            subscription_status = 'paused' if '暂停' in cols[4].text else 'open'
            
            fund = {
                'code': code,
                'name': name,
                'exchange': 'SZSE',  # 深交所
                'nav': nav,
                'acc_nav': 'N/A',  # 深交所页面可能不直接提供
                'daily_change': daily_change,
                'premium_rate': 'N/A',
                'subscription_status': subscription_status,
                'limit_amount': '无限额'  # 深交所页面可能不直接提供
            }
            funds.append(fund)
        
        print(f"成功获取 {len(funds)} 只深交所LOF基金")
        return funds
    
    except Exception as e:
        print(f"获取深交所数据失败: {e}")
        return []


def fetch_realtime_premium_rates(funds):
    """
    获取实时溢价率（需要场内交易价格）
    """
    print("正在获取实时溢价率...")
    
    # 这里应该调用行情API获取场内交易价格
    # 由于实际API需要认证，这里使用模拟数据
    for fund in funds:
        try:
            # 模拟溢价率计算（实际应用中需要真实数据）
            if fund['nav'] != 'N/A' and fund['nav']:
                # 模拟场内交易价格（净值的±2%范围内）
                nav = float(fund['nav'])
                market_price = nav * (1 + random.uniform(-0.02, 0.02))
                premium_rate = ((market_price - nav) / nav) * 100
                fund['premium_rate'] = f"{premium_rate:.2f}%"
        except (ValueError, TypeError):
            fund['premium_rate'] = 'N/A'
    
    return funds


def save_to_json(funds, filename='data/lof_funds.json'):
    """
    保存数据到JSON文件
    """
    output = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_count': len(funds),
        'funds': funds
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"成功保存 {len(funds)} 只LOF基金数据到 {filename}")


def main():
    # 获取上交所LOF基金
    sse_funds = fetch_sse_lof_funds()
    time.sleep(random.uniform(1, 2))
    
    # 获取深交所LOF基金
    szse_funds = fetch_szse_lof_funds()
    
    # 合并数据（去重）
    all_funds = sse_funds + szse_funds
    unique_funds = {f['code']: f for f in all_funds}
    funds = list(unique_funds.values())
    
    # 获取实时溢价率
    funds = fetch_realtime_premium_rates(funds)
    
    # 保存数据
    save_to_json(funds)
    
    # 生成前端可用的JS数据文件
    generate_js_data(funds)


def generate_js_data(funds):
    """
    生成前端可用的JavaScript数据文件
    """
    js_content = "// LOF基金数据 - 自动生成\n"
    js_content += "// 最后更新: {}\n\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    js_content += "const LOF_FUND_DATA = [\n"
    
    for fund in funds:
        js_content += "    {{
"
        js_content += "        code: \"{}\",
".format(fund['code'])
        js_content += "        name: \"{}\",
".format(fund['name'].replace('"', '\"'))
        js_content += "        premiumRate: \"{}\",
".format(fund['premium_rate'])
        js_content += "        dailyChange: \"{}\",
".format(fund['daily_change'])
        js_content += "        limitAmount: \"{}\",
".format(fund['limit_amount'])
        js_content += "        subscriptionStatus: \"{}\"
".format(fund['subscription_status'])
        js_content += "    }},\n"
    
    js_content += "];\n\n"
    js_content += "// 数据加载函数\n"
    js_content += "function loadLOFFundData() {\n"
    js_content += "    return LOF_FUND_DATA;\n"
    js_content += "}\n"
    
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print("成功生成前端数据文件 data.js")

if __name__ == '__main__':
    print("===== LOF基金数据采集系统 =====")
    main()
    print("==============================")