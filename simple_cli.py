"""
简化版智能投资顾问CLI界面
提供命令行界面访问所有功能
"""
import sys
import os
import pandas as pd
import numpy as np
import efinance as ef
from datetime import datetime


# 导入我们创建的简化版组件
from integrated_simple_gui import SimpleSmartAdvisor, SimpleMarketScanner, SimpleTechnicalIndicators


def display_advice(advice):
    """显示投资建议"""
    print("\n" + "="*60)
    print("投资建议详情")
    print("="*60)
    print(f"股票: {advice.stock_name} ({advice.stock_code})")
    print(f"当前价格: ¥{advice.current_price:.2f}")
    print(f"分析时间: {advice.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("技术指标:")
    print(f"  技术评分: {advice.technical_score:.1f}/100")
    print(f"  基本面评分: {advice.fundamental_score:.1f}/100")
    print(f"  情绪面评分: {advice.sentiment_score:.1f}/100")
    print(f"  综合评分: {advice.overall_score:.1f}/100")
    print()
    
    print("投资建议:")
    print(f"  信号: {advice.signal.value}")
    print(f"  信心度: {advice.confidence:.1f}%")
    print(f"  风险等级: {advice.risk_level}")
    print(f"  建议仓位: {advice.position_size*100:.1f}%")
    print()
    
    print("价格建议:")
    print(f"  目标价: ¥{advice.target_price:.2f} ({(advice.target_price/advice.current_price-1)*100:+.2f}%)")
    print(f"  止损价: ¥{advice.stop_loss:.2f} ({(advice.stop_loss/advice.current_price-1)*100:+.2f}%)")
    print()
    
    print("建议理由:")
    for i, reason in enumerate(advice.reasons, 1):
        print(f"  {i}. {reason}")
    print()


def single_stock_analysis():
    """单股分析功能"""
    print("\n单股分析")
    print("-" * 30)
    
    # 获取用户输入
    stock_code = input("请输入股票代码 (例如: 600519): ").strip()
    if not stock_code:
        stock_code = "600519"  # 默认贵州茅台
        
    stock_name = input(f"请输入股票名称 (默认: 贵州茅台): ").strip()
    if not stock_name:
        stock_name = "贵州茅台"
    
    print(f"\n正在获取 {stock_name}({stock_code}) 的数据...")
    
    try:
        # 获取数据
        data = ef.stock.get_quote_history(stock_code)
        
        if data is None or data.empty:
            print("❌ 未获取到数据，请检查股票代码")
            return
            
        # 数据预处理
        data = data.rename(columns={
            '日期': 'date', '开盘': 'open', '最高': 'high', 
            '最低': 'low', '收盘': 'close', '成交量': 'volume'
        })
        
        data['date'] = pd.to_datetime(data['date'])
        data = data.sort_values('date')
        
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        data = data.dropna()
        
        if len(data) < 60:
            print(f"❌ 数据量不足，当前有 {len(data)} 条数据，至少需要60条")
            return
            
        print(f"✅ 成功获取 {len(data)} 条历史数据")
        
        # 计算技术指标
        print("📊 正在计算技术指标...")
        data = SimpleTechnicalIndicators.calculate_all_indicators(data)
        
        # 创建顾问并分析
        print("🧠 正在进行智能分析...")
        advisor = SimpleSmartAdvisor()
        
        # 获取基本面数据
        fundamental_data = {
            'roe': 15.0, 'revenue_growth': 10.0, 'profit_growth': 12.0,
            'pe_ratio': 20.0, 'pb_ratio': 2.5, 'debt_ratio': 0.4, 'current_ratio': 1.8
        }
        
        advice = advisor.analyze_stock(stock_code, stock_name, data, fundamental_data)
        
        if advice:
            display_advice(advice)
        else:
            print("❌ 分析失败")
            
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")


def market_scan_analysis():
    """市场扫描功能"""
    print("\n市场扫描")
    print("-" * 30)
    
    print("🔍 正在扫描市场...")
    
    try:
        advisor = SimpleSmartAdvisor()
        scanner = SimpleMarketScanner(advisor)
        
        # 热门股票列表
        hot_stocks = [
            ("600519", "贵州茅台"),
            ("000858", "五粮液"),
            ("600036", "招商银行"),
            ("601318", "中国平安"),
            ("000333", "美的集团"),
            ("600276", "恒瑞医药"),
            ("000651", "格力电器"),
            ("601888", "中国中免"),
            ("300750", "宁德时代"),
            ("002475", "立讯精密")
        ]
        
        print(f"📊 正在分析 {len(hot_stocks)} 只热门股票...")
        
        advice_list = scanner.scan_market(hot_stocks)
        
        if advice_list:
            print(f"\n✅ 扫描完成，找到 {len(advice_list)} 个投资机会")
            
            # 按评分排序并显示前10
            top_picks = sorted(advice_list, key=lambda x: x.overall_score, reverse=True)[:10]
            
            print("\n" + "="*100)
            print(f"{'排名':<4} {'代码':<8} {'名称':<12} {'信号':<8} {'评分':<6} {'当前价':<10} {'目标价':<10} {'止损价':<10} {'信心度':<8}")
            print("="*100)
            
            for i, advice in enumerate(top_picks, 1):
                signal_color = ""
                signal_reset = ""
                
                if "买入" in advice.signal.value:
                    signal_color = ""
                    signal_reset = ""
                elif "卖出" in advice.signal.value:
                    signal_color = ""
                    signal_reset = ""
                
                print(f"{i:<4} {advice.stock_code:<8} {advice.stock_name:<12} {signal_color}{advice.signal.value:<8}{signal_reset} "
                      f"{advice.overall_score:<6.1f} ¥{advice.current_price:<9.2f} ¥{advice.target_price:<9.2f} "
                      f"¥{advice.stop_loss:<9.2f} {advice.confidence:<7.1f}%")
            
            print("="*100)
            
            # 询问是否查看详细信息
            if top_picks:
                print(f"\n📈 前3名详细分析:")
                for i, advice in enumerate(top_picks[:3], 1):
                    print(f"\n{i}. {advice.stock_name} ({advice.stock_code})")
                    print(f"   信号: {advice.signal.value}")
                    print(f"   评分: {advice.overall_score:.1f}/100")
                    print(f"   价格: ¥{advice.current_price:.2f} → ¥{advice.target_price:.2f} (+{(advice.target_price/advice.current_price-1)*100:+.1f}%)")
                    print(f"   止损: ¥{advice.stop_loss:.2f}")
                    print(f"   理由: {advice.reasons[0] if advice.reasons else '无'}")
        else:
            print("❌ 未找到符合条件的投资机会")
            
    except Exception as e:
        print(f"❌ 扫描过程中出现错误: {e}")


def main():
    """主函数"""
    print("🎯 智能投资顾问系统 - 简化版")
    print("="*50)
    
    while True:
        print("\n📋 请选择功能:")
        print("1. 单股分析")
        print("2. 市场扫描")
        print("3. 退出")
        
        choice = input("\n请输入选择 (1-3): ").strip()
        
        if choice == "1":
            single_stock_analysis()
        elif choice == "2":
            market_scan_analysis()
        elif choice == "3":
            print("\n👋 感谢使用智能投资顾问系统！")
            break
        else:
            print("\n❌ 无效选择，请重新输入")


if __name__ == "__main__":
    main()