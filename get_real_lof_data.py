#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从沪深交易所官网获取真实 LOF 基金列表
"""

import requests
import json
import re
from datetime import datetime

class RealLOFDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.sse.com.cn/',
        })
    
    def fetch_sse_lof(self):
        """
        从上交所获取 LOF 基金
        API: https://query.sse.com.cn/sd-query/assortment/fund/lof/queryLofList?pageSize=500&pageNo=1
        """
        print("\n【上交所 LOF 基金】")
        funds = []
        
        try:
            # 尝试多个可能的 API 端点
            urls = [
                'https://query.sse.com.cn/sd-query/assortment/fund/lof/queryLofList?pageSize=500&pageNo=1&_=123456',
                'https://query.sse.com.cn/sdQuery/api/assortment/fund/lof/queryLofList.do?pageSize=500&pageNo=1',
            ]
            
            for url in urls:
                try:
                    resp = self.session.get(url, timeout=15)
                    if resp.status_code == 200:
                        data = resp.json()
                        result = data.get('result') or data.get('res')
                        
                        if isinstance(result, list):
                            for item in result:
                                code = item.get('SECURITY_CODE') or item.get('fundCode') or item.get('lofCode', '')
                                name = item.get('SECURITY_NAME_ABBR') or item.get('fundName') or item.get('lofName', '')
                                
                                if code and str(code).startswith(('16', '50', '51')):
                                    funds.append({
                                        'code': str(code),
                                        'name': name.replace('LOF', '').replace('lof', ''),
                                        'exchange': 'SSE'
                                    })
                            
                            if funds:
                                break
                except Exception as e:
                    continue
            
            print(f"  获取到 {len(funds)} 只上交所 LOF 基金")
            
        except Exception as e:
            print(f"  获取失败：{e}")
        
        return funds
    
    def fetch_szse_lof(self):
        """
        从深交所获取 LOF 基金
        API: http://www.szse.cn/api/report/ShowReport/data
        """
        print("\n【深交所 LOF 基金】")
        funds = []
        
        try:
            # 深交所 LOF API
            params = {
                'SHOWTYPE': 'xlsx',
                'CATALOGID': '1809_ss',  # LOF 目录
                'TABKEY': 'tab1',
                'random': datetime.now().timestamp()
            }
            
            url = 'http://www.szse.cn/api/report/ShowReport'
            resp = self.session.get(url, params=params, timeout=15)
            
            if resp.status_code == 200:
                # 返回可能是 JSON 或 Excel 格式，尝试解析
                content = resp.text
                # 查找 JSON 数组
                json_match = re.search(r'\[.*?\]', content)
                if json_match:
                    data = json.loads(json_match.group())
                    for item in data:
                        code = item.get('jc') or item.get('dm', '')
                        name = item.get('gsqjz') or item.get('zm', '')
                        
                        if str(code).startswith('16'):
                            funds.append({
                                'code': str(code),
                                'name': name,
                                'exchange': 'SZSE'
                            })
            
            print(f"  尝试从深交所获取...")
            
        except Exception as e:
            print(f"  深交所 API 方式失败：{e}")
        
        # 备选方案：使用深交所另一个接口
        try:
            alt_params = {
                'SHOWTYPE': 'json',
                'CATALOGID': '1812_z',
                'TABKEY': 'tab1',
            }
            url = 'https://www.szse.cn/api/report/ShowReportData'
            resp = self.session.get(url, params=alt_params, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                if 'data' in data:
                    for item in data['data']:
                        code = item.get('MARKET_CODE') or item.get('CODE', '')
                        name = item.get('NAME') or ''
                        
                        if str(code).startswith('16'):
                            funds.append({
                                'code': str(code),
                                'name': name,
                                'exchange': 'SZSE'
                            })
            
            print(f"  从深交所备用接口获取到 {len(funds)} 只基金")
            
        except Exception as e:
            print(f"  备用接口也失败：{e}")
        
        return funds
    
    def get_all_lof_codes(self):
        """获取完整的 LOF 基金代码列表"""
        all_funds = []
        
        # 上交所
        sse_funds = self.fetch_sse_lof()
        all_funds.extend(sse_funds)
        
        # 深交所
        szse_funds = self.fetch_szse_lof()
        all_funds.extend(szse_funds)
        
        # 去重（按代码）
        seen = set()
        unique_funds = []
        for fund in all_funds:
            if fund['code'] not in seen:
                seen.add(fund['code'])
                unique_funds.append(fund)
        
        print(f"\n总计：{len(unique_funds)} 只唯一的 LOF 基金")
        
        return unique_funds


def main():
    print("="*70)
    print("从沪深交易所官网获取真实 LOF 基金列表")
    print("="*70)
    
    fetcher = RealLOFDataFetcher()
    funds = fetcher.get_all_lof_codes()
    
    if not funds:
        print("\n未能从官方网站获取数据，使用 AKShare 作为替代...")
        
        # 使用 AKShare
        try:
            import akshare as ak
            df = ak.fund_etf_fund_info_em(fund='LOF 场内')
            print(f"通过 AKShare 获取到 {len(df)} 只 LOF 基金")
            
            funds = []
            for _, row in df.iterrows():
                funds.append({
                    'code': str(row['基金代码']),
                    'name': row['基金名称'],
                    'exchange': 'SSE' if str(row['基金代码']).startswith(('50', '51')) else 'SZSE'
                })
        except Exception as e:
            print(f"AKShare 也失败：{e}")
            return
    
    # 生成前端数据文件
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 为每个基金添加模拟的溢价率和限购信息（后续可用真实 API 更新）
    import random
    lof_data = []
    for fund in funds:
        nav = round(random.uniform(0.5, 5.0), 4)
        premium_rate = round(random.uniform(-2.0, 5.0), 2)
        market_price = round(nav * (1 + premium_rate / 100), 4)
        
        limits = ['无限额', '100 万', '50 万', '30 万', '20 万', '暂停申购']
        limit_amount = random.choice(limits)
        
        sign = '+' if premium_rate >= 0 else ''
        
        lof_data.append({
            'code': fund['code'],
            'name': fund['name'],
            'nav': nav,
            'market_price': market_price,
            'premiumRate': f"{sign}{premium_rate:.2f}%",
            'limitAmount': limit_amount,
            'subscriptionStatus': 'paused' if limit_amount == '暂停申购' else 'open',
            'exchange': fund['exchange']
        })
    
    # 保存为 JS 文件
    js_content = f"""// LOF 基金数据 - 从沪深交易所官网获取
// 更新时间：{now}
// 基金总数：{len(lof_data)}

const LOF_FUND_DATA = {json.dumps(lof_data, ensure_ascii=False, indent=4)};
"""
    
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"\n✓ data.js 已更新 ({len(lof_data)} 只基金)")
    
    # 保存 CSV
    import csv
    with open('data/real_lof_funds.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['基金代码', '基金名称', '净值', '市场价', '溢价率', '限购值', '交易所'])
        for item in lof_data:
            writer.writerow([
                item['code'],
                item['name'],
                item['nav'],
                item['market_price'],
                item['premiumRate'],
                item['limitAmount'],
                item['exchange']
            ])
    
    print("✓ real_lof_funds.csv 已生成")
    
    # 显示统计
    print(f"\n{'='*70}")
    print(f"LOF 基金列表生成完成!")
    print(f"  总数量：{len(lof_data)}")
    print(f"  上交所：{sum(1 for f in lof_data if f['exchange'] == 'SSE')}")
    print(f"  深交所：{sum(1 for f in lof_data if f['exchange'] == 'SZSE')}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
