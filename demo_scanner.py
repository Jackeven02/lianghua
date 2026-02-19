# -*- coding: utf-8 -*-
"""
市场扫描演示程序
"""
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'efinance'))
sys.path.insert(0, os.path.dirname(__file__))

import efinance as ef
import pandas as pd
import numpy as np
from datetime import datetime

def analyze_stock(stock_code, stock_name):
    """简单分析股票"""
    try:
        # 获取历史数据
        df = ef.stock.get_quote_history(stock_code)
        
        if df is None or df.empty or len(df) < 60:
            return None
        
        # 取最近120天
        df = df.iloc[-120:].copy()
        
        # 重命名列
        df = df.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume'
        })
        
        # 处理负数价格
        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col].abs()
        
        # 计算技术指标
        df['SMA_5'] = df['close'].rolling(window=5).mean()
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_60'] = df['close'].rolling(window=60).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 获取最新数据
        latest = df.iloc[-1]
        current_price = latest['close']
        
        # 计算评分
        score = 0
        
        # 趋势分析
        if latest['SMA_5'] > latest['SMA_20'] > latest['SMA_60']:
            score += 30
        elif latest['SMA_5'] > latest['SMA_20']:
            score += 20
        
        # RSI分析
        if 30 < latest['RSI'] < 70:
            score += 20
        elif latest['RSI'] < 30:
            score += 15
        
        # 价格位置
        if current_price > latest['SMA_20']:
            score += 15
        
        # 成交量
        recent_vol = df['volume'].iloc[-5:].mean()
        avg_vol = df['volume'].mean()
        if recent_vol > avg_vol * 1.2:
            score += 10
        
        # 动量
        returns_5d = (df['close'].iloc[-1] / df['close'].iloc[-5] - 1) * 100
        if returns_5d > 3:
            score += 10
        
        # 生成信号
        if score >= 60:
            signal = "买入"
        elif score >= 40:
            signal = "持有"
        else:
            signal = "观望"
        
        return {
            'code': stock_code,
            'name': stock_name,
            'price': current_price,
            'signal': signal,
            'score': score,
            'rsi': latest['RSI']
        }
        
    except Exception as e:
        return None


print("\n" + "=" * 80)
print(" " * 28 + "市场扫描演示")
print("=" * 80 + "\n")

# 定义要扫描的股票列表
stock_list = [
    ("600519", "贵州茅台"),
    ("000858", "五粮液"),
    ("600036", "招商银行"),
    ("601318", "中国平安"),
    ("000333", "美的集团"),
    ("600276", "恒瑞医药"),
    ("000651", "格力电器"),
    ("601888", "中国中免"),
    ("300750", "宁德时代"),
    ("002475", "立讯精密"),
]

print(f"正在扫描 {len(stock_list)} 只股票...")
print("这可能需要一些时间，请耐心等待...\n")

results = []

for i, (code, name) in enumerate(stock_list, 1):
    print(f"[{i}/{len(stock_list)}] 分析 {name} ({code})...", end=" ")
    
    result = analyze_stock(code, name)
    
    if result:
        results.append(result)
        print(f"完成 (评分: {result['score']})")
    else:
        print("跳过")

# 按评分排序
results.sort(key=lambda x: x['score'], reverse=True)

# 显示结果
print("\n" + "=" * 80)
print("扫描结果")
print("=" * 80 + "\n")

print(f"找到 {len(results)} 个投资机会\n")

print(f"{'排名':<6} {'代码':<10} {'名称':<12} {'价格':<12} {'信号':<10} {'评分':<8} {'RSI':<8}")
print("-" * 80)

for i, result in enumerate(results, 1):
    print(f"{i:<6} {result['code']:<10} {result['name']:<12} "
          f"¥{result['price']:<11.2f} {result['signal']:<10} "
          f"{result['score']:<8} {result['rsi']:<8.1f}")

# 显示Top 3详情
if len(results) >= 3:
    print("\n" + "=" * 80)
    print("Top 3 投资标的")
    print("=" * 80)
    
    for i, result in enumerate(results[:3], 1):
        print(f"\n{i}. {result['name']} ({result['code']})")
        print(f"   当前价: ¥{result['price']:.2f}")
        print(f"   信号: {result['signal']}")
        print(f"   评分: {result['score']}/100")
        print(f"   RSI: {result['rsi']:.1f}")
        
        target_price = result['price'] * 1.15
        stop_loss = result['price'] * 0.92
        print(f"   目标价: ¥{target_price:.2f} (+15%)")
        print(f"   止损价: ¥{stop_loss:.2f} (-8%)")

print("\n" + "=" * 80)
print("扫描完成")
print("=" * 80)

print("\n提示:")
print("- 本分析仅供参考，不构成投资建议")
print("- 投资有风险，入市需谨慎")
print("- 建议结合基本面和市场环境综合判断")
print()
