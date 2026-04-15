#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从上交所和深交所官方API获取LOF基金数据
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import os

os.makedirs('data', exist_ok=True)

# 上交所LOF基金API
SSE_URL = "https://query.sse.com.cn/commonQuery.do"

# 深交所LOF基金API
SZSE_URL = "http://fund.szse.cn/api/report/ShowReport/data"

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.sse.com.cn/assortment/fund/lof/home/",
    "Accept": "application/json"
}

# 深交所请求头
SZSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "http://fund.szse.cn/marketdata/lof/index.html",
    "Accept": "application/json"
}

def get_sse_lof_funds():
    """获取上交所LOF基金数据"""
    print("正在获取上交所LOF基金...")
    
    all_data = []
    page_no = 1
    
    while True:
        params = {
            "jsonCallBack": f"jQuery{int(datetime.now().timestamp() * 1000)}",
            "isPagination": "true",
            "sqlId": "COMMON_SSE_ZQPZ_ETF_LOF_LB",
            "ORDER_BY": "GPDM",
            "pageHelp.pageSize": "200",
            "pageHelp.pageNo": str(page_no),
            "_": int(datetime.now().timestamp() * 1000)
        }
        
        try:
            response = requests.get(SSE_URL, params=params, headers=HEADERS, timeout=15)
            # 移除JSONP包装
            content = response.text
            if content.startswith('jQuery') and content.endswith(');'):
                start = content.find('(')
                end = content.rfind(')')
                content = content[start+1:end]
            
            data = json.loads(content)
            
            if 'pageHelp' in data and 'data' in data['pageHelp']:
                page_data = data['pageHelp']['data']
                total_count = data['pageHelp'].get('total', 0)
                
                for item in page_data:
                    fund = {
                        'code': item.get('GPDM', '').strip(),
                        'name': item.get('GPJC', '').strip(),
                        'exchange': 'SSE',
                        'nav': item.get('DWJZ', ''),
                        'daily_change': item.get('ZRZZL', ''),
                        'premium_rate': item.get('YJL', ''),
                        'limit_amount': item.get('XSGZ', ''),
                        'subscription_status': 'paused' if '暂停' in item.get('SSZT', '') else 'open'
                    }
                    if fund['code']:
                        all_data.append(fund)
                
                print(f"上交所第{page_no}页: {len(page_data)} 只基金")
                
                # 判断是否还有下一页
                if len(page_data) < 200 or len(all_data) >= total_count:
                    break
                
                page_no += 1
                time.sleep(1)  # 避免请求过快
            else:
                print("上交所返回数据格式异常")
                break
                
        except Exception as e:
            print(f"上交所获取失败: {e}")
            break
    
    print(f"上交所共获取到 {len(all_data)} 只LOF基金")
    return all_data

def get_szse_lof_funds():
    """获取深交所LOF基金数据"""
    print("正在获取深交所LOF基金...")
    
    all_data = []
    page_no = 1
    
    while True:
        params = {
            "SHOWTYPE": "JSON",
            "CATALOGID": "main_szzl/LOF_INDEX",
            "TABKEY": "tab1",
            "PAGENO": str(page_no),
            "PAGECOUNT": "200"
        }
        
        try:
            response = requests.get(SZSE_URL, params=params, headers=SZSE_HEADERS, timeout=15)
            data = response.json()
            
            if data.get('error') is None and len(data) > 0 and isinstance(data[0], dict):
                metadata = data[0].get('metadata', {})
                page_data = data[0].get('data', [])
                
                for item in page_data:
                    # 提取字段
                    code = ''
                    name = ''
                    nav = ''
                    daily_change = ''
                    premium_rate = ''
                    limit_amount = ''
                    subscription_status = 'open'
                    
                    # 不同的深交所数据结构处理
                    if isinstance(item, list):
                        # 处理列表格式
                        if len(item) >= 9:
                            code = str(item[0]).strip()
                            name = str(item[1]).strip()
                            nav = str(item[2]).strip()
                            daily_change = str(item[3]).strip()
                            premium_rate = str(item[4]).strip()
                            limit_amount = str(item[5]).strip()
                            status_text = str(item[8]).strip()
                            subscription_status = 'paused' if '暂停' in status_text else 'open'
                    elif isinstance(item, dict):
                        # 处理字典格式
                        code = str(item.get('col1', '')).strip()
                        name = str(item.get('col2', '')).strip()
                        nav = str(item.get('col3', '')).strip()
                        daily_change = str(item.get('col4', '')).strip()
                        premium_rate = str(item.get('col5', '')).strip()
                        limit_amount = str(item.get('col6', '')).strip()
                        status_text = str(item.get('col9', '')).strip()
                        subscription_status = 'paused' if '暂停' in status_text else 'open'
                    
                    if code:
                        fund = {
                            'code': code,
                            'name': name,
                            'exchange': 'SZSE',
                            'nav': nav,
                            'daily_change': daily_change,
                            'premium_rate': premium_rate,
                            'limit_amount': limit_amount,
                            'subscription_status': subscription_status
                        }
                        all_data.append(fund)
                
                print(f"深交所第{page_no}页: {len(page_data)} 只基金")
                
                # 检查是否有更多数据
                if len(page_data) < 200:
                    break
                
                page_no += 1
                time.sleep(1)
            else:
                print("深交所返回数据异常")
                break
                
        except Exception as e:
            print(f"深交所获取失败: {e}")
            break
    
    print(f"深交所共获取到 {len(all_data)} 只LOF基金")
    return all_data

def merge_funds(sse_funds, szse_funds):
    """合并两个交易所的数据"""
    # 使用字典去重
    merged = {}
    
    # 添加上交所数据
    for fund in sse_funds:
        code = fund['code']
        if code not in merged:
            merged[code] = fund
    
    # 添加深交所数据（优先使用非空值）
    for fund in szse_funds:
        code = fund['code']
        if code in merged:
            # 合并数据，优先保留非空值
            existing = merged[code]
            for key, value in fund.items():
                if value and not existing[key]:
                    existing[key] = value
        else:
            merged[code] = fund
    
    # 转换为列表并排序
    result = list(merged.values())
    result.sort(key=lambda x: x['code'])
    
    return result

def save_data(funds):
    """保存数据到各种格式"""
    if not funds:
        print("没有数据可保存")
        return
    
    # 创建DataFrame
    df = pd.DataFrame(funds)
    
    # 保存CSV
    df.to_csv('data/lof_funds_full.csv', index=False, encoding='utf-8-sig')
    print("已保存 data/lof_funds_full.csv")
    
    # 保存JSON
    output = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_count': len(funds),
        'funds': funds
    }
    with open('data/lof_funds.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("已保存 data/lof_funds.json")
    
    # 生成前端JS文件
    generate_js(funds)
    
    return output

def generate_js(funds):
    """生成前端可用的JS数据"""
    js_content = "// LOF基金数据 - 官方来源\n"
    js_content += f"// 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    js_content += f"// 基金总数: {len(funds)}\n\n"
    js_content += "const LOF_FUND_DATA = [\n"
    
    for i, fund in enumerate(funds):
        js_content += "    {\n"
        js_content += f"        code: \"{fund['code']}\",\n"
        js_content += f"        name: \"{fund['name']}\",\n"
        js_content += f"        nav: \"{fund['nav']}\",\n"
        
        # 格式化涨跌幅
        change = fund['daily_change']
        if change and change != 'N/A':
            if change.startswith(('+', '-', '±')):
                pass
            elif change.replace('.', '').isdigit():
                change = '+' + change
            change += '%'
        else:
            change = 'N/A'
        js_content += f"        dailyChange: \"{change}\",\n"
        
        # 溢价率
        premium = fund['premium_rate']
        if premium and premium != 'N/A':
            if premium.replace('.', '').replace('-', '').isdigit():
                premium += '%'
        else:
            premium = 'N/A'
        js_content += f"        premiumRate: \"{premium}\",\n"
        
        # 限购数量
        limit = fund['limit_amount']
        if not limit or limit == 'N/A':
            limit = '无限额'
        js_content += f"        limitAmount: \"{limit}\",\n"
        
        # 申购状态
        status = fund['subscription_status']
        if status == 'paused':
            js_content += f"        subscriptionStatus: \"paused\"\n"
        else:
            js_content += f"        subscriptionStatus: \"open\"\n"
        
        js_content += "    }" + ("," if i < len(funds) - 1 else "") + "\n"
    
    js_content += "];\n"
    
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("已生成 data.js")

def main():
    print("=" * 60)
    print("LOF基金数据采集系统 - 官方API版")
    print("=" * 60)
    
    # 获取上交所数据
    sse_funds = get_sse_lof_funds()
    
    # 获取深交所数据
    szse_funds = get_szse_lof_funds()
    
    # 合并数据
    all_funds = merge_funds(sse_funds, szse_funds)
    print(f"\n合并后总计: {len(all_funds)} 只LOF基金")
    
    # 保存数据
    save_data(all_funds)
    
    # 显示前20只
    print("\n前20只LOF基金:")
    for fund in all_funds[:20]:
        print(f"  {fund['code']} | {fund['name']:20s} | 净值:{fund['nav']:>8s} | 涨跌:{fund['daily_change']:>8s}% | {fund['exchange']}")
    
    print("\n数据采集完成！")

if __name__ == '__main__':
    main()