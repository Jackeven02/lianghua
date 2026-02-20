# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'efinance'))

import efinance as ef
import pandas as pd

print("=" * 60)
print("快速测试 - efinance 数据获取")
print("=" * 60)

# 测试获取股票数据
print("\n正在获取贵州茅台(600519)数据...")
try:
    df = ef.stock.get_quote_history("600519")
    if df is not None and not df.empty:
        print(f"成功！获取到 {len(df)} 条数据")
        print(f"最新价格: {df['收盘'].iloc[-1]:.2f}")
        print(f"最新日期: {df['日期'].iloc[-1]}")
    else:
        print("失败：无法获取数据")
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
