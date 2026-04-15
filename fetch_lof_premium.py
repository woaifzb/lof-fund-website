#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOF 基金溢价率完整数据采集脚本
使用 AKShare 获取实时市场行情 + 天天基金网获取净值
"""

import akshare as ak
import pandas as pd
import requests
import json
import re
import time
from datetime import datetime

class LOFPremiumCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://fund.eastmoney.com/',
        })
    
    def get_lof_market_data(self):
        """从 AKShare 获取 LOF 基金实时市场数据"""
        print("正在获取 LOF 基金实时市场数据...")
        try:
            df = ak.fund_lof_spot_em()
            print(f"✓ 获取到 {len(df)} 只 LOF 基金的实时行情")
            return df
        except Exception as e:
            print(f"✗ 获取市场数据失败：{e}")
            return None
    
    def get_nav_from_tiantian(self, fund_code):
        """从天天基金网获取基金单位净值"""
        try:
            url = f'http://fundgz.1234567.com.cn/js/{fund_code}.js'
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                match = re.search(r'jsonpgz\((\{.*?\})\)', response.text)
                if match:
                    data = json.loads(match.group(1))
                    gsz = data.get('gsz')  # 估算净值
                    gztime = data.get('gztime')
                    return float(gsz), gztime
        except Exception as e:
            pass
        
        return None, None
    
    def calculate_premium_rate(self, market_price, nav):
        """
        计算溢价率
        公式：溢价率 = (市场价格 - 单位净值) / 单位净值 × 100%
        """
        if market_price and nav and nav != 0:
            return round((market_price - nav) / nav * 100, 2)
        return None
    
    def format_premium(self, premium_rate):
        """格式化溢价率"""
        if premium_rate is None:
            return "N/A"
        sign = "+" if premium_rate >= 0 else ""
        return f"{sign}{premium_rate:.2f}%"
    
    def collect_all_data(self, sample_size=100):
        """
        收集所有 LOF 基金数据
        :param sample_size: 采集的基金数量（为避免请求过快，可设置样本数）
        """
        # 1. 获取市场数据
        market_df = self.get_lof_market_data()
        if market_df is None:
            print("无法获取市场数据，程序退出")
            return []
        
        results = []
        total = len(market_df)
        
        print(f"\n开始处理 {total} 只 LOF 基金...")
        
        for i, row in market_df.iterrows():
            code = str(row['代码'])
            name = row['名称']
            market_price = row['最新价']
            
            # 获取净值
            nav, nav_time = self.get_nav_from_tiantian(code)
            
            # 计算溢价率
            premium = self.calculate_premium_rate(market_price, nav)
            premium_str = self.format_premium(premium)
            
            result = {
                'code': code,
                'name': name,
                'nav': nav,
                'market_price': market_price,
                'premiumRate': premium_str,
                'limitAmount': '无限额',
                'subscriptionStatus': 'open',
                'exchange': 'SSE' if code.startswith(('50', '51')) else 'SZSE'
            }
            results.append(result)
            
            # 显示进度
            if (i + 1) % 50 == 0 or i == total - 1:
                status_count = sum(1 for r in results if r['premiumRate'] != 'N/A')
                print(f"  进度：{i+1}/{total}, 已计算溢价率：{status_count}只")
            
            # 小延迟避免请求过快
            if i < total - 1 and i % 10 == 0:
                time.sleep(0.5)
        
        return results
    
    def save_to_js(self, results, output_file='data.js'):
        """保存为前端 JS 文件"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = f"// LOF 基金数据 - 自动生成\n"
        content += f"// 更新时间：{now}\n"
        content += f"// 基金总数：{len(results)}\n\n"
        content += "const LOF_FUND_DATA = " + json.dumps(results, ensure_ascii=False, indent=2) + ";\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✓ 已保存至 {output_file}")
    
    def save_to_csv(self, results, output_file='data/fund_full_data.csv'):
        """保存为 CSV 文件"""
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✓ 已保存至 {output_file}")


def main():
    print("\n" + "="*70)
    print("LOF 基金完整数据采集与溢价率计算系统")
    print("="*70)
    
    collector = LOFPremiumCollector()
    
    # 收集数据（默认全部采集，可调整 sample_size 限制数量）
    results = collector.collect_all_data(sample_size=400)
    
    if not results:
        print("没有获取到任何数据，程序退出")
        return
    
    # 统计数据
    calc_count = sum(1 for r in results if r['premiumRate'] != 'N/A')
    print(f"\n{'='*70}")
    print(f"数据处理完成!")
    print(f"  总基金数：{len(results)}")
    print(f"  成功计算溢价率：{calc_count}")
    print(f"  溢价率计算成功率：{calc_count/len(results)*100:.1f}%")
    
    # 按溢价率排序并显示前 10
    valid_results = [r for r in results if r['premiumRate'] != 'N/A']
    valid_results.sort(key=lambda x: float(x['premiumRate'].replace('%', '').replace('+', '')), reverse=True)
    
    print(f"\n{'='*70}")
    print("溢价率最高的 10 只 LOF 基金:")
    print("-"*70)
    for r in valid_results[:10]:
        print(f"  {r['code']} {r['name'][:12]:<14} : {r['premiumRate']:>10}")
    
    print(f"\n溢价率最低的 10 只 LOF 基金:")
    print("-"*70)
    for r in valid_results[-10:]:
        print(f"  {r['code']} {r['name'][:12]:<14} : {r['premiumRate']:>10}")
    
    # 保存数据
    collector.save_to_js(results)
    collector.save_to_csv(results)
    
    print("\n" + "="*70)
    print("数据已更新到前端页面，请刷新浏览器查看!")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()