#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOF 基金溢价率自动计算系统 v2
来源：天天基金网（净值）、东方财富（市场价格）
"""

import requests
import json
import time
import re
from datetime import datetime

class LOFPremiumCalculator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'http://quote.eastmoney.com/center/',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        })
    
    def get_nav_from_tiantian(self, fund_code):
        """从天天基金网获取基金净值"""
        try:
            url = f'http://fundgz.1234567.com.cn/js/{fund_code}.js'
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                text = response.text
                match = re.search(r'jsonpgz\((\{.*?\})\)', text)
                if match:
                    data = json.loads(match.group(1))
                    gsz = data.get('gsz')
                    gztime = data.get('gztime')
                    return float(gsz), gztime
        except Exception as e:
            pass
        return None, None
    
    def get_market_price_from_dfcf(self, fund_code):
        """从东方财富获取市场价格 - 使用统一的 quote 接口"""
        try:
            # 确定交易所前缀
            # 深交所 LOF: 16xxx, 15xxx -> sz
            # 上交所 LOF: 50xxx, 51xxx -> sh
            if fund_code.startswith(('16', '15')):
                prefix = 'SZ'
            else:
                prefix = 'SH'
            
            # 东方财富实时行情 API
            secid = f"{prefix}.{fund_code}"
            params = {
                'fields1': 'f1,f2,f3,f4,f5,f6',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58',
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'ndays': '5',
                'iscr': '0',
                'iscca': '0',
                'secid': secid,
                '_': int(datetime.now().timestamp() * 1000)
            }
            
            url = 'https://push2.eastmoney.com/api/qt/stock/get'
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    # f52 = 最新价
                    price = data['data'].get('f52')
                    if price and price != '-':
                        return float(price)
        except Exception as e:
            pass
        
        # 备选方案：尝试新浪接口
        return self.get_market_price_from_sina(fund_code)
    
    def get_market_price_from_sina(self, fund_code):
        """从新浪财经获取市场价格"""
        try:
            # 根据代码判断交易所
            if fund_code.startswith(('15', '16', '50', '51')):
                # LOF 基金大部分在深交所
                url = f'https://hq.sinajs.cn/list=sz{fund_code}'
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    text = response.text
                    match = re.search(r'"([^"]+)"', text)
                    if match:
                        parts = match.group(1).split(',')
                        # 索引 3 = 当前价格
                        if len(parts) >= 4 and parts[3]:
                            price = float(parts[3])
                            if price > 0:
                                return price
        except Exception:
            pass
        
        # 再试一次上交所
        try:
            url = f'https://hq.sinajs.cn/list=sh{fund_code}'
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                text = response.text
                match = re.search(r'"([^"]+)"', text)
                if match:
                    parts = match.group(1).split(',')
                    if len(parts) >= 4 and parts[3]:
                        price = float(parts[3])
                        if price > 0:
                            return price
        except Exception:
            pass
        
        return None
    
    def calculate_premium_rate(self, nav, market_price):
        """计算溢价率 = (市场价 - 净值) / 净值 × 100%"""
        if nav and market_price and nav != 0:
            premium_rate = (market_price - nav) / nav * 100
            return round(premium_rate, 2)
        return None
    
    def format_premium(self, premium_rate):
        """格式化溢价率"""
        if premium_rate is None:
            return "N/A"
        return f"{premium_rate:+.2f}%"
    
    def process_fund(self, fund_code, fund_name=None):
        """处理单个基金"""
        print(f"\n[{fund_code}] {fund_name or '未知'}")
        
        # 获取净值
        nav, nav_time = self.get_nav_from_tiantian(fund_code)
        print(f"  净值：{nav} @ {nav_time}")
        
        # 获取市场价格
        market_price = self.get_market_price_from_dfcf(fund_code)
        print(f"  市场价：{market_price}")
        
        # 计算溢价率
        premium_rate = self.calculate_premium_rate(nav, market_price)
        premium_str = self.format_premium(premium_rate)
        print(f"  溢价率：{premium_str}")
        
        return {
            'code': fund_code,
            'name': fund_name or '未知',
            'nav': nav,
            'market_price': market_price,
            'premiumRate': premium_str,
            'limitAmount': '无限额',
            'subscriptionStatus': 'open'
        }
    
    def batch_process(self, funds, delay=0.3):
        """批量处理"""
        results = []
        for i, fund in enumerate(funds):
            print(f"\n{'='*50}")
            print(f"进度：{i+1}/{len(funds)}")
            result = self.process_fund(fund['code'], fund.get('name'))
            results.append(result)
            if i < len(funds) - 1:
                time.sleep(delay)
        return results
    
    def save_to_data_js(self, results, output_file='data.js'):
        """保存为前端 JS 文件"""
        content = f"// LOF 基金数据\n"
        content += f"// 更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"// 基金总数：{len(results)}\n\n"
        content += "const LOF_FUND_DATA = " + json.dumps(results, ensure_ascii=False, indent=2) + ";\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✓ 已保存至 {output_file}")
    
    def save_to_csv(self, results, output_file='data/fund_premium_data.csv'):
        """保存为 CSV"""
        with open(output_file, 'w', encoding='utf-8-sig') as f:
            f.write("基金代码，基金名称，单位净值，市场价格，溢价率，限购值，时间\n")
            for r in results:
                f.write(f"{r['code']},{r['name']},{r['nav'] or ''},{r['market_price'] or ''},{r['premiumRate']},{r['limitAmount']},{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print(f"✓ 已保存至 {output_file}")


def main():
    print("\n" + "="*60)
    print("LOF 基金溢价率计算系统 v2")
    print("="*60)
    
    calculator = LOFPremiumCalculator()
    
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
    
    results = calculator.batch_process(funds, delay=1)
    calculator.save_to_data_js(results)
    calculator.save_to_csv(results)
    
    print("\n" + "="*60)
    print("汇总:")
    print("="*60)
    for r in results:
        print(f"  {r['code']} {r['name'][:12]:<14} : {r['premiumRate']}")


if __name__ == '__main__':
    main()