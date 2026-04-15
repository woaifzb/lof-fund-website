#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOF 基金溢价率计算 - 使用模拟浏览器请求
"""

import requests
import json
import time
import re
from datetime import datetime

class LOFPremiumFetcher:
    def __init__(self):
        # 完整的 headers 来模拟真实浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_nav_from_tiantian(self, fund_code):
        """从天天基金获取净值"""
        try:
            url = f'http://fundgz.1234567.com.cn/js/{fund_code}.js'
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                match = re.search(r'jsonpgz\((\{.*?\})\)', resp.text)
                if match:
                    data = json.loads(match.group(1))
                    return float(data.get('gsz')), data.get('gztime')
        except Exception as e:
            print(f"  [ERROR] 净值获取失败：{e}")
        return None, None
    
    def get_market_price_eastmoney_web(self, fund_code):
        """从东方财富网页解析市场价格"""
        try:
            # 确定交易所
            prefix = 'SZ' if fund_code.startswith(('16', '15')) else 'SH'
            
            # 东方财富个股页面
            url = f'http://quote.eastmoney.com/{prefix}{fund_code}.html'
            resp = self.session.get(url, timeout=15)
            
            if resp.status_code == 200:
                # 在 HTML 中寻找最新价数据
                content = resp.text
                
                # 方法 1: 查找最新价的 JSON 数据
                match = re.search(r'"price":\s*"?([\d.]+)"?', content)
                if match:
                    return float(match.group(1))
                
                # 方法 2: 查找当前价格字段
                match = re.search(r'"f52"\s*:\s*"([\d.]+)"', content)
                if match:
                    return float(match.group(1))
                    
        except Exception as e:
            print(f"  [ERROR] 东方财富网页解析失败：{e}")
        
        return None
    
    def get_market_price_from_api(self, fund_code):
        """尝试多个 API 源获取市场价格"""
        
        sources = [
            ('东方财富 API', lambda: self._dfcf_api(fund_code)),
            ('同花顺 API', lambda: self._ths_api(fund_code)),
        ]
        
        for name, func in sources:
            try:
                result = func()
                if result and result > 0:
                    print(f"  [{name}] 成功：{result}")
                    return result
            except Exception as e:
                pass
        
        return None
    
    def _dfcf_api(self, fund_code):
        """东方财富实时行情 API"""
        prefix = 'SZ' if fund_code.startswith(('16', '15')) else 'SH'
        secid = f"{prefix}.{fund_code}"
        
        params = {
            'fields1': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'ndays': '5',
            'iscr': '0',
            'iscca': '0',
            'secid': secid,
            '_': int(time.time() * 1000),
        }
        
        url = 'https://push2.eastmoney.com/api/qt/stock/get'
        resp = self.session.get(url, params=params, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get('data'):
                # f52 是最新价
                price = data['data'].get('f52', '-')
                if price != '-' and price:
                    return float(price)
        
        return None
    
    def _ths_api(self, fund_code):
        """同花顺 API"""
        # 同花顺接口格式
        url = f'http://d.10jqka.com.cn/v2/last/c/{fund_code}/head.js'
        resp = self.session.get(url, timeout=10)
        
        if resp.status_code == 200:
            match = re.search(r'"([^"]+)"', resp.text)
            if match:
                parts = match.group(1).split(',')
                if len(parts) >= 4:
                    price = float(parts[3])
                    if price > 0:
                        return price
        
        return None
    
    def process_fund(self, code, name):
        """处理单个基金"""
        print(f"\n[{code}] {name}")
        
        nav, nav_time = self.get_nav_from_tiantian(code)
        print(f"  净值：{nav} ({nav_time})")
        
        market_price = self.get_market_price_from_api(code)
        print(f"  市场价：{market_price}")
        
        # 计算溢价率
        premium = None
        if nav and market_price and nav != 0:
            premium = round((market_price - nav) / nav * 100, 2)
        
        premium_str = f"{premium:+.2f}%" if premium is not None else "N/A"
        print(f"  溢价率：{premium_str}")
        
        return {
            'code': code,
            'name': name,
            'nav': nav,
            'market_price': market_price,
            'premiumRate': premium_str,
            'limitAmount': '无限额',
            'subscriptionStatus': 'open'
        }


def main():
    print("\n" + "="*60)
    print("LOF 基金溢价率计算")
    print("="*60)
    
    fetcher = LOFPremiumFetcher()
    
    funds = [
        {"code": "161005", "name": "富国天惠成长混合 LOFA"},
        {"code": "160607", "name": "鹏华动力增长 LOF"},
        {"code": "161224", "name": "国投瑞银瑞源LOF"},
        {"code": "161226", "name": "国投瑞银瑞和沪深 300LOF"},
        {"code": "160213", "name": "国泰纳斯达克 100LOF"},
        {"code": "161116", "name": "易方达黄金主题 LOF"},
        {"code": "163407", "name": "兴全合润LOF"},
        {"code": "160119", "name": "南方积配LOF"},
    ]
    
    results = []
    for i, fund in enumerate(funds):
        result = fetcher.process_fund(fund['code'], fund['name'])
        results.append(result)
        if i < len(funds) - 1:
            time.sleep(2)  # 延迟以避免请求过快
    
    # 保存数据
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    js_content = f"// LOF 基金数据\n// 更新时间：{now}\nconst LOF_FUND_DATA = {json.dumps(results, ensure_ascii=False, indent=2)};\n"
    
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print("\n✓ data.js 已更新")
    
    # CSV
    with open('data/fund_data.csv', 'w', encoding='utf-8-sig') as f:
        f.write("代码，名称，净值，市场价，溢价率\n")
        for r in results:
            f.write(f"{r['code']},{r['name']},{r['nav'] or ''},{r['market_price'] or ''},{r['premiumRate']}\n")
    
    print("✓ CSV 已更新")
    
    print("\n" + "="*60)
    print("结果摘要:")
    print("="*60)
    for r in results:
        print(f"{r['code']} {r['name'][:10]:<12} : 溢价率={r['premiumRate']}")


if __name__ == '__main__':
    main()