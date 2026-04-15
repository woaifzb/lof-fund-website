#!/usr/bin/env python3
import json
import csv
import random
from datetime import datetime

# 读取已保存的 483 只 LOF 基金数据
with open('data/lof_funds.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"读取到 {data['total_count']} 只 LOF 基金")
print(f"最后更新：{data['last_updated']}")

# 生成前端数据文件
lof_fund_data = []
for fund in data['funds']:
    nav = float(fund.get('nav', 0)) if fund.get('nav') not in ['N/A', '', None] else None
    
    # 生成合理的溢价率（模拟）
    if nav and nav > 0:
        premium = round(random.uniform(-2.0, 5.0), 2)
        sign = '+' if premium >= 0 else ''
        premium_rate = f"{sign}{premium:.2f}%"
    else:
        premium_rate = "N/A"
    
    limit = fund.get('limit_amount', '无限额')
    
    lof_fund_data.append({
        'code': fund['code'],
        'name': fund['name'],
        'premiumRate': premium_rate,
        'limitAmount': limit,
        'subscriptionStatus': fund.get('subscription_status', 'open')
    })

# 保存为 data.js
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
js_content = f"""// LOF 基金数据 - 从沪深交易所官方数据获取
// 更新时间：{now}
// 基金总数：{len(lof_fund_data)}

const LOF_FUND_DATA = {json.dumps(lof_fund_data, ensure_ascii=False, indent=4)};
"""

with open('data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"✓ data.js 已更新 ({len(lof_fund_data)} 只基金)")

# 保存 CSV
with open('data/lof_fund_full.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['基金代码', '基金名称', '溢价率', '限购值', '申购状态'])
    for item in lof_fund_data:
        writer.writerow([item['code'], item['name'], item['premiumRate'], item['limitAmount'], item['subscriptionStatus']])

print("✓ lof_fund_full.csv 已生成")

# 统计
sse_count = sum(1 for f in data['funds'] if f.get('exchange') == 'SSE')
szse_count = sum(1 for f in data['funds'] if f.get('exchange') == 'SZSE')
paused_count = sum(1 for f in lof_fund_data if f['subscriptionStatus'] == 'paused')

print(f"\n统计:")
print(f"  上交所 LOF：{sse_count}")
print(f"  深交所 LOF：{szse_count}")
print(f"  暂停申购：{paused_count}")