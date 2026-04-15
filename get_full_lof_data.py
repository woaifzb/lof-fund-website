#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从东方财富API获取所有LOF基金数据
"""

import requests
import json
import os
from datetime import datetime

os.makedirs('data', exist_ok=True)

def get_all_funds():
    """获取所有基金列表"""
    print("正在获取所有基金数据...")
    
    url = "http://fund.eastmoney.com/js/fundcode_search.js"
    response = requests.get(url, timeout=30)
    
    # 移除BOM和变量声明
    text = response.text.replace('\ufeff', '').strip()
    # 移除 "var r = " 和最后的 ";"
    if text.startswith('var r = '):
        text = text[8:]
    if text.endswith(';'):
        text = text[:-1]
    
    # 解析JSON
    funds = json.loads(text)
    print(f"总共获取到 {len(funds)} 只基金")
    
    # 筛选LOF基金（代码以16开头）
    lof_funds = []
    for item in funds:
        code = item[0]
        name = item[2]
        fund_type = item[3]
        
        # LOF基金：16开头
        if code.startswith('16') and len(code) == 6:
            lof_funds.append({
                'code': code,
                'name': name,
                'type': fund_type
            })
    
    print(f"筛选出LOF基金（16开头）: {len(lof_funds)} 只")
    
    return lof_funds

def get_fund_nav_batch(fund_codes, batch_size=50):
    """批量获取基金净值"""
    print("正在获取基金净值...")
    
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
    all_nav_data = {}
    
    for i in range(0, len(fund_codes), batch_size):
        batch = fund_codes[i:i+batch_size]
        secids = []
        for code in batch:
            # 16开头：160-162是深市，163-165是沪市
            prefix3 = int(code[:3])
            if prefix3 <= 162:
                secids.append(f"0.{code}")
            else:
                secids.append(f"1.{code}")
        
        params = {
            'fltt': '2',
            'fields': 'f2,f3,f12,f14',
            'secids': ','.join(secids),
            '_': int(datetime.now().timestamp() * 1000)
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if 'data' in data and 'diff' in data['data']:
                for item in data['data']['diff']:
                    code = item.get('f12', '')
                    all_nav_data[code] = {
                        'nav': str(item.get('f2', '')) if item.get('f2') else 'N/A',
                        'change_pct': str(item.get('f3', '')) if item.get('f3') else 'N/A',
                    }
            
            print(f"进度: {min(i+batch_size, len(fund_codes))}/{len(fund_codes)}")
            
        except Exception as e:
            print(f"获取失败: {e}")
    
    return all_nav_data

def main():
    print("=" * 50)
    print("LOF基金数据采集系统")
    print("=" * 50)
    
    # 步骤1: 获取所有LOF基金
    lof_funds = get_all_funds()
    
    # 步骤2: 获取净值
    fund_codes = [f['code'] for f in lof_funds]
    nav_data = get_fund_nav_batch(fund_codes)
    
    # 步骤3: 合并数据
    for fund in lof_funds:
        code = fund['code']
        if code in nav_data:
            fund['nav'] = nav_data[code]['nav']
            fund['daily_change'] = nav_data[code]['change_pct'] + '%'
        else:
            fund['nav'] = 'N/A'
            fund['daily_change'] = 'N/A'
        
        fund['premium_rate'] = 'N/A'
        fund['subscription_status'] = 'open'
        fund['limit_amount'] = '无限额'
        fund['exchange'] = 'SZSE' if int(code[:3]) <= 162 else 'SSE'
    
    # 排序
    lof_funds.sort(key=lambda x: x['code'])
    
    print(f"\n总计: {len(lof_funds)} 只LOF基金")
    
    # 保存JSON
    output = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_count': len(lof_funds),
        'funds': lof_funds
    }
    with open('data/lof_funds.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("已保存 data/lof_funds.json")
    
    # 保存CSV
    import csv
    with open('data/lof_funds.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['code', 'name', 'type', 'nav', 'daily_change', 'premium_rate', 'subscription_status', 'limit_amount', 'exchange'])
        writer.writeheader()
        writer.writerows(lof_funds)
    print("已保存 data/lof_funds.csv")
    
    # 生成JS
    generate_js(lof_funds)
    
    # 显示示例
    print("\n前20只LOF基金:")
    for fund in lof_funds[:20]:
        print(f"  {fund['code']} | {fund['name']:20s} | 净值:{fund['nav']:>8s} | 涨跌:{fund['daily_change']:>8s} | {fund['exchange']}")

def generate_js(funds):
    """生成前端JS数据"""
    js = f"// LOF基金数据 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    js += f"// 基金总数: {len(funds)}\n\n"
    js += "const LOF_FUND_DATA = [\n"
    
    for i, f in enumerate(funds):
        js += "    { code: \"" + f['code'] + "\", name: \"" + f['name'] + "\", nav: \"" + f['nav'] + "\", dailyChange: \"" + f['daily_change'] + "\", premiumRate: \"" + f['premium_rate'] + "\", limitAmount: \"" + f['limit_amount'] + "\", subscriptionStatus: \"" + f['subscription_status'] + "\", exchange: \"" + f['exchange'] + "\" }"
        if i < len(funds) - 1:
            js += ","
        js += "\n"
    
    js += "];\n"
    
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("已生成 data.js")

if __name__ == '__main__':
    main()
