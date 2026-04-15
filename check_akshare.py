#!/usr/bin/env python3
import akshare as ak
import pandas as pd
import json
from datetime import datetime

print("正在获取真实 LOF 基金数据...")

# 方法 1: 获取 LOF 场内实时行情
try:
    df = ak.fund_etf_fund_info_em(fund="LOF 场内")
    print(f"✓ 从 fund_etf_fund_info_em 获取到 {len(df)} 只 LOF 基金")
    print("\n列名:", list(df.columns))
    print("\n前 5 条:")
    print(df.head().to_string())
except Exception as e:
    print(f"✗ 方法 1 失败：{e}")
    
# 方法 2: LOF 列表
try:
    df2 = ak.fund_lof_list_em()
    print(f"\n✓ 从 fund_lof_list_em 获取到 {len(df2)} 只 LOF 基金")
    print("列名:", list(df2.columns))
    print("\n前 5 条:")
    print(df2.head().to_string())
except Exception as e:
    print(f"✗ 方法 2 失败：{e}")

# 方法 3: LOF 历史行情
try:
    df3 = ak.fund_lof_hist_em(symbol="161005", period="日")
    print(f"\n✓ 从 fund_lof_hist_em 获取数据成功")
except Exception as e:
    print(f"✗ 方法 3 失败：{e}")
