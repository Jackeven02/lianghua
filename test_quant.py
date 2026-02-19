"""
量化分析软件测试模块
用于测试各个功能模块
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_data():
    """创建测试数据"""
    # 生成测试日期
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    
    # 生成测试价格数据（模拟股价）
    np.random.seed(42)
    initial_price = 100
    returns = np.random.normal(0.001, 0.02, len(dates))  # 日收益率
    prices = [initial_price]
    
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    # 创建DataFrame
    data = pd.DataFrame({
        'date': dates,
        'open': [p * (1 + np.random.normal(0, 0.01)) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.02))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.02))) for p in prices],
        'close': prices,
        'volume': [np.random.randint(1000000, 10000000) for _ in range(len(dates))],
        'amount': [p * v for p, v in zip(prices, [np.random.randint(1000000, 10000000) for _ in range(len(dates))])]
    })
    
    return data.set_index('date')

def test_data_layer():
    """测试数据层功能"""
    print("测试数据层功能...")
    
    try:
        from data_layer import get_stock_data, get_data_provider, get_data_processor
        
        # 测试数据提供者
        provider = get_data_provider()
        print(f"数据提供者创建成功: {type(provider)}")
        
        # 测试数据处理器
        processor = get_data_processor()
        print(f"数据处理器创建成功: {type(processor)}")
        
        # 测试数据获取（使用测试数据）
        test_data = create_test_data()
        processed_data = processor.clean_data(test_data)
        print(f"数据处理成功，处理后数据形状: {processed_data.shape}")
        
        print("数据层测试通过 ✓")
        return True
        
    except Exception as e:
        print(f"数据层测试失败: {str(e)}")
        return False

def test_analysis_layer():
    """测试分析层功能"""
    print("\n测试分析层功能...")
    
    try:
        from analysis_layer import TechnicalIndicators, StatisticalAnalysis
        
        # 创建测试数据
        test_data = create_test_data()['close']
        
        # 测试技术指标
        sma = TechnicalIndicators.calculate_sma(test_data, 20)
        rsi = TechnicalIndicators.calculate_rsi(test_data, 14)
        print(f"技术指标计算成功 - SMA长度: {len(sma)}, RSI长度: {len(rsi)}")
        
        # 测试统计分析
        returns = StatisticalAnalysis.calculate_returns(test_data)
        volatility = StatisticalAnalysis.calculate_volatility(returns)
        sharpe = StatisticalAnalysis.calculate_sharpe_ratio(returns)
        print(f"统计分析成功 - 波动率: {volatility:.4f}, 夏普比率: {sharpe:.4f}")
        
        print("分析层测试通过 ✓")
        return True
        
    except Exception as e:
        print(f"分析层测试失败: {str(e)}")
        return False

def test_strategy_layer():
    """测试策略层功能"""
    print("\n测试策略层功能...")
    
    try:
        from strategy_layer import TechnicalStrategy, BacktestingEngine
        
        # 创建测试数据
        test_data = create_test_data()
        
        # 测试策略
        strategy = TechnicalStrategy('测试策略', ['SMA', 'RSI'])
        signals = strategy.generate_signals(test_data)
        print(f"策略信号生成成功: {signals}")
        
        # 测试回测引擎
        engine = BacktestingEngine(initial_capital=100000)
        # 由于需要较长时间，这里简化测试
        print("回测引擎创建成功")
        
        print("策略层测试通过 ✓")
        return True
        
    except Exception as e:
        print(f"策略层测试失败: {str(e)}")
        return False

def test_risk_layer():
    """测试风险层功能"""
    print("\n测试风险层功能...")
    
    try:
        from risk_layer import RiskManager, PositionSizing
        
        # 测试风险管理器
        risk_manager = RiskManager()
        risk_manager.set_risk_limits('TEST', 1000, 5000)
        print("风险管理器配置成功")
        
        # 测试仓位计算
        position_size = PositionSizing.fixed_fractional_sizing(
            capital=100000, risk_percent=0.02, 
            entry_price=50, stop_loss_price=45
        )
        print(f"仓位计算成功: {position_size} 股")
        
        print("风险层测试通过 ✓")
        return True
        
    except Exception as e:
        print(f"风险层测试失败: {str(e)}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("量化分析软件模块测试")
    print("=" * 50)
    
    test_results = []
    
    # 运行各层测试
    test_results.append(test_data_layer())
    test_results.append(test_analysis_layer())
    test_results.append(test_strategy_layer())
    test_results.append(test_risk_layer())
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"通过测试: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！系统可以正常运行。")
        return True
    else:
        print("❌ 部分测试失败，请检查相关模块。")
        return False

if __name__ == '__main__':
    run_all_tests()