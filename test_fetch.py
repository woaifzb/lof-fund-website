#!/usr/bin/env python3
import requests
import json
import time

url = "https://fundmobapi.eastmoney.com/FundMNewApi/FundMNFGetLOFList"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

params = {
    'plat': 'Android',
    'appType': 'ttjj',
    'product': 'Fund',
    'version': '6.2.0',
}

try:
    resp = requests.post(url, headers=headers, data=params, timeout=15)
    print(f"Status: {resp.status_code}")
    print(resp.text[:3000])
except Exception as e:
    print(f"Error: {e}")
