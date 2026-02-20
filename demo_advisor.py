# -*- coding: utf-8 -*-
"""
智能投资顾问演示程序
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

print("\n" + "=" * 80)
print(" " * 25 + "智能投资顾问演示")
print("=" * 80 + "\n")

# 获取股票数据
stock_code = "600519"
stock_name = "贵州茅台"

print(f"正在分析 {stock_name} ({stock_code})...")
print("正在获取数据...")

try:
    # 获取历史数据
    df = ef.stock.get_quote_history(stock_code)
    
    if df is None or df.empty:
        print("无法获取数据")
        sys.exit(1)
    
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
    
    print(f"成功获取 {len(df)} 天数据")
    
    # 计算简单技术指标
    print("正在计算技术指标...")
    
    # 移动平均线
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
    
    print("\n" + "=" * 80)
    print("分析结果")
    print("=" * 80)
    
    print(f"\n股票: {stock_name} ({stock_code})")
    print(f"当前价格: ¥{current_price:.2f}")
    print(f"日期: {latest['date']}")
    
    # 简单分析
    print("\n技术指标:")
    print(f"  SMA5:  ¥{latest['SMA_5']:.2f}")
    print(f"  SMA20: ¥{latest['SMA_20']:.2f}")
    print(f"  SMA60: ¥{latest['SMA_60']:.2f}")
    print(f"  RSI:   {latest['RSI']:.2f}")
    
    # 生成简单建议
    print("\n投资建议:")
    
    score = 0
    reasons = []
    
    # 趋势分析
    if latest['SMA_5'] > latest['SMA_20'] > latest['SMA_60']:
        score += 30
        reasons.append("均线呈多头排列")
    elif latest['SMA_5'] > latest['SMA_20']:
        score += 20
        reasons.append("短期均线向上")
    
    # RSI分析
    if 30 < latest['RSI'] < 70:
        score += 20
        reasons.append("RSI处于健康区间")
    elif latest['RSI'] < 30:
        score += 15
        reasons.append("RSI超卖，可能反弹")
    
    # 价格位置
    if current_price > latest['SMA_20']:
        score += 15
        reasons.append("价格在20日均线上方")
    
    # 成交量
    recent_vol = df['volume'].iloc[-5:].mean()
    avg_vol = df['volume'].mean()
    if recent_vol > avg_vol * 1.2:
        score += 10
        reasons.append("成交量放大")
    
    # 生成信号
    if score >= 60:
        signal = "买入"
        color = "绿色"
    elif score >= 40:
        signal = "持有"
        color = "黄色"
    else:
        signal = "观望"
        color = "红色"
    
    print(f"  信号: {signal}")
    print(f"  评分: {score}/100")
    print(f"  信心度: {min(score, 100)}%")
    
    # 计算目标价和止损价
    target_price = current_price * 1.15
    stop_loss = current_price * 0.92
    
    print(f"\n价格建议:")
    print(f"  目标价: ¥{target_price:.2f} (+15%)")
    print(f"  止损价: ¥{stop_loss:.2f} (-8%)")
    
    print(f"\n理由:")
    for i, reason in enumerate(reasons, 1):
        print(f"  {i}. {reason}")
    
    print("\n" + "=" * 80)
    print("分析完成")
    print("=" * 80)
    
    print("\n提示:")
    print("- 本分析仅供参考，不构成投资建议")
    print("- 投资有风险，入市需谨慎")
    print("- 建议结合基本面和市场环境综合判断")
    
except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()

print()
