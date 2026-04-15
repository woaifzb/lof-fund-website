#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取完整LOF基金数据
从东方财富API获取上交所和深交所所有LOF基金
"""

import akshare as ak
import pandas as pd
import json
import sys
import os
from datetime import datetime

os.makedirs('data', exist_ok=True)

def get_lof_funds():
    """获取所有LOF基金数据"""
    all_funds = []
    
    # 获取上交所LOF基金
    print('正在获取上交所LOF基金...', flush=True)
    try:
        sse_lof = ak.fund_etf_fund_info_em(fund='上交所LOF')
        print(f'上交所LOF基金数量: {len(sse_lof)}', flush=True)
        print(f'列名: {sse_lof.columns.tolist()}', flush=True)
        
        for _, row in sse_lof.iterrows():
            fund = {
                'code': str(row.get('代码', row.get('基金代码', ''))).strip(),
                'name': str(row.get('名称', row.get('基金简称', ''))).strip(),
                'nav': str(row.get('最新净值', row.get('单位净值', ''))).strip(),
                'daily_change': str(row.get('日增长率', row.get('增长率', ''))).strip(),
                'exchange': 'SSE',
                'subscription_status': 'open',  # 默认开放
                'limit_amount': '无限额',
                'premium_rate': 'N/A'
            }
            if fund['code']:
                all_funds.append(fund)
    except Exception as e:
        print(f'上交所获取失败: {e}', flush=True)
    
    # 获取深交所LOF基金  
    print('正在获取深交所LOF基金...', flush=True)
    try:
        szse_lof = ak.fund_etf_fund_info_em(fund='深交所LOF')
        print(f'深交所LOF基金数量: {len(szse_lof)}', flush=True)
        print(f'列名: {szse_lof.columns.tolist()}', flush=True)
        
        for _, row in szse_lof.iterrows():
            fund = {
                'code': str(row.get('代码', row.get('基金代码', ''))).strip(),
                'name': str(row.get('名称', row.get('基金简称', ''))).strip(),
                'nav': str(row.get('最新净值', row.get('单位净值', ''))).strip(),
                'daily_change': str(row.get('日增长率', row.get('增长率', ''))).strip(),
                'exchange': 'SZSE',
                'subscription_status': 'open',
                'limit_amount': '无限额',
                'premium_rate': 'N/A'
            }
            if fund['code']:
                all_funds.append(fund)
    except Exception as e:
        print(f'深交所获取失败: {e}', flush=True)
    
    # 去重
    unique_funds = {f['code']: f for f in all_funds}
    all_funds = list(unique_funds.values())
    all_funds.sort(key=lambda x: x['code'])
    
    print(f'总LOF基金数量: {len(all_funds)}', flush=True)
    
    # 保存CSV
    df = pd.DataFrame(all_funds)
    df.to_csv('data/lof_funds_full.csv', index=False, encoding='utf-8-sig')
    print('已保存到 data/lof_funds_full.csv', flush=True)
    
    # 生成JSON
    output = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_count': len(all_funds),
        'funds': all_funds
    }
    with open('data/lof_funds.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print('已保存到 data/lof_funds.json', flush=True)
    
    # 生成前端JS数据
    generate_js(all_funds)
    
    return all_funds

def generate_js(funds):
    """生成前端可用的JS数据"""
    js_content = "// LOF基金完整数据 - 自动生成\n"
    js_content += f"// 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    js_content += f"// 基金总数: {len(funds)}\n\n"
    js_content = "const LOF_FUND_DATA = [\n"
    
    for i, fund in enumerate(funds):
        js_content += "    {\n"
        js_content += f"        code: \"{fund['code']}\",\n"
        js_content += f"        name: \"{fund['name']}\",\n"
        js_content += f"        nav: \"{fund['nav']}\",\n"
        js_content += f"        dailyChange: \"{fund['dailyChange']}\",\n"
        js_content += f"        limitAmount: \"{fund['limitAmount']}\",\n"
        js_content += f"        subscriptionStatus: \"{fund['subscriptionStatus']}\",\n"
        js_content += f"        exchange: \"{fund['exchange']}\"\n"
        js_content += "    }" + ("," if i < len(funds) - 1 else "") + "\n"
    
    js_content += "];\n"
    
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print('已生成 data.js', flush=True)

if __name__ == '__main__':
    print("=" * 50, flush=True)
    print("LOF基金数据采集系统", flush=True)
    print("=" * 50, flush=True)
    get_lof_funds()
    print("完成!", flush=True)
