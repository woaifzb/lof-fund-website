#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 HTTP 请求直接获取东方财富 LOF 基金数据
"""

import requests
import re
import json
from datetime import datetime

def fetch_lof_from_dfcf():
    """从东方财富网页抓取 LOF 基金列表"""
    
    # 东方财富 LOF 基金页面
    url = "http://fund.eastmoney.com/lof/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://fund.eastmoney.com/',
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        
        if resp.status_code == 200:
            content = resp.text
            
            # 查找所有 LOF 基金的 JSON 数据
            # 寻找 fundList 或类似变量
            patterns = [
                r'var\s+fundList\s*=\s*(\[.*?\]);',
                r'"code":"(\d+)","name":"([^"]+)".*?"nav":"([\d.]+)"',
                r'f2="([\d.]+)".*?f14="([^"]+)"',  # 最新价和名称
            ]
            
            # 尝试提取表格数据
            # 东方财富通常使用 DataTable，可以查找相关的 JS 数据
            fund_matches = re.findall(r'data:\[{"code":"(\d+)","name":"([^"]+)"', content)
            
            if fund_matches:
                funds = []
                for code, name in fund_matches[:10]:
                    print(f"  {code} {name}")
                print(f"...共找到 {len(fund_matches)} 只基金")
                return fund_matches
        
    except Exception as e:
        print(f"获取失败：{e}")
    
    return None


def fetch_lof_data_api():
    """使用东方财富通用 API 获取 LOF 数据"""
    
    # 通用行情数据接口
    url = "https://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get"
    
    params = {
        'type': 'RPT_FUNDLOF_LIST',
        'st': 'create_time',
        'sr': '-1',
        'ps': '1000',  # 每页 1000 条
        'p': '1',
        'js': '{"data":(x)}',
        'rt': int(datetime.now().timestamp() * 1000),
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        
        if resp.status_code == 200:
            # 响应格式：{"status":true,"data":[],"msg":null}
            data = resp.json()
            
            if 'data' in data and data['data']:
                funds = data['data']
                print(f"✓ 成功获取 {len(funds)} 只 LOF 基金")
                
                # 打印前 10 条
                for i, fund in enumerate(funds[:10]):
                    print(f"\n基金 {i+1}:")
                    for key, value in fund.items():
                        print(f"  {key}: {value}")
                
                return funds
    
    except Exception as e:
        print(f"API 请求失败：{e}")
    
    return None


def main():
    print("="*70)
    print("从东方财富获取 LOF 基金完整列表")
    print("="*70)
    
    # 方法 1: API 接口
    funds = fetch_lof_data_api()
    
    if funds:
        print("\n" + "="*70)
        print("字段说明:")
        print("="*70)
        if funds:
            first_fund = funds[0]
            for key in first_fund.keys():
                print(f"  {key}")
    
    else:
        print("\n未能通过 API 获取，尝试网页解析...")
        result = fetch_lof_from_dfcf()
        if result:
            print(f"\n通过网页解析获取到 {len(result)} 只基金")


if __name__ == '__main__':
    main()
