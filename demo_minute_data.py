#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from data_layer.efinance_provider import EFinanceProvider
import pandas as pd
from datetime import datetime

def demo_minute_data():
    print("=" * 80)
    print("分钟级数据演示")
    print("=" * 80)
    
    provider = EFinanceProvider()
    stock_code = "600519"
    
    klt_types = {
        1: "1分钟",
        5: "5分钟",
        15: "15分钟",
        30: "30分钟",
        60: "60分钟",
        101: "日线"
    }
    
    print(f"\n测试股票: {stock_code} (贵州茅台)")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 80)
    
    for klt, name in klt_types.items():
        print(f"\n【{name}数据】")
        print("-" * 80)
        
        try:
            df = provider.get_stock_data(stock_code, days=100, klt=klt)
            
            if df.empty:
                print(f"❌ 无法获取{name}数据")
                continue
            
            print(f"✅ 成功获取 {len(df)} 条数据")
            
            print(f"\n最新5条{name}数据:")
            latest_data = df.tail(5)[['date', 'open', 'high', 'low', 'close', 'volume']]
            print(latest_data.to_string(index=False))
            
            if 'MA5' in df.columns and 'MA10' in df.columns:
                latest = df.iloc[-1]
                print(f"\n技术指标:")
                print(f"  MA5:  {latest['MA5']:.2f}")
                print(f"  MA10: {latest['MA10']:.2f}")
                print(f"  MA20: {latest['MA20']:.2f}")
                
                if 'RSI' in df.columns:
                    print(f"  RSI:  {latest['RSI']:.2f}")
                
                if 'MACD' in df.columns:
                    print(f"  MACD: {latest['MACD']:.4f}")
                    print(f"  Signal: {latest['Signal']:.4f}")
            
            print(f"\n数据时间范围:")
            print(f"  开始: {df.iloc[0]['date']}")
            print(f"  结束: {df.iloc[-1]['date']}")
            
        except Exception as e:
            print(f"❌ 获取{name}数据失败: {str(e)}")
    
    print("\n" + "=" * 80)
    print("演示完成！")
    print("=" * 80)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("QuantAnalyzer - 分钟级数据演示程序")
    print("=" * 80)
    
    demo_minute_data()
    
    print("\n提示:")
    print("  - 1分钟数据适合短线交易和实时监控")
    print("  - 5分钟数据适合日内分析")
    print("  - 15/30分钟数据适合短期趋势分析")
    print("  - 60分钟数据适合中期趋势分析")
    print("  - 日线数据适合长期投资分析")
    print("=" * 80)
