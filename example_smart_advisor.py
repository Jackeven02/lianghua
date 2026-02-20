"""
智能投资顾问系统使用示例
演示如何使用智能分析引擎进行投资决策
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入核心模块
from strategy_layer.smart_advisor import SmartAdvisor, MarketScanner, SignalStrength
from strategy_layer.portfolio_manager import PortfolioManager, RiskManager
from analysis_layer.technical_indicators import TechnicalIndicators
from data_layer.efinance_provider import EFinanceProvider, DataProviderFactory


def example_1_analyze_single_stock(use_real_data: bool = True):
    """示例1：分析单只股票"""
    print("=" * 80)
    print("示例1：分析单只股票")
    print("=" * 80)
    
    # 创建智能顾问
    advisor = SmartAdvisor(risk_tolerance="中等")
    
    # 准备数据
    stock_code = "600519"
    stock_name = "贵州茅台"
    
    # 选择数据提供者
    if use_real_data:
        print("\n使用真实市场数据 (efinance)...")
        data_provider = EFinanceProvider()
    else:
        print("\n使用模拟数据...")
        from example_smart_advisor_mock import MockDataProvider
        data_provider = MockDataProvider()
    
    stock_data = data_provider.get_stock_data(stock_code)
    fundamental_data = data_provider.get_fundamental_data(stock_code)
    
    if stock_data.empty:
        print(f"✗ 无法获取 {stock_code} 的数据")
        return
    
    # 分析股票
    advice = advisor.analyze_stock(
        stock_code=stock_code,
        stock_name=stock_name,
        data=stock_data,
        fundamental_data=fundamental_data
    )
    
    # 打印结果
    print(f"\n股票: {advice.stock_name} ({advice.stock_code})")
    print(f"投资信号: {advice.signal.value}")
    print(f"信心度: {advice.confidence:.1f}%")
    print(f"当前价: ¥{advice.current_price:.2f}")
    print(f"目标价: ¥{advice.target_price:.2f} ({(advice.target_price/advice.current_price-1)*100:+.1f}%)")
    print(f"止损价: ¥{advice.stop_loss:.2f} ({(advice.stop_loss/advice.current_price-1)*100:+.1f}%)")
    print(f"\n综合评分: {advice.overall_score:.1f}")
    print(f"  - 技术面: {advice.technical_score:.1f}")
    print(f"  - 基本面: {advice.fundamental_score:.1f}")
    print(f"  - 情绪面: {advice.sentiment_score:.1f}")
    print(f"\n风险等级: {advice.risk_level}")
    print(f"建议仓位: {advice.position_size*100:.1f}%")
    print(f"投资期限: {advice.time_horizon}")
    print(f"\n投资理由:")
    for i, reason in enumerate(advice.reasons, 1):
        print(f"  {i}. {reason}")
    print()


def example_2_scan_market(use_real_data: bool = True):
    """示例2：扫描市场寻找投资机会"""
    print("=" * 80)
    print("示例2：扫描市场寻找投资机会")
    print("=" * 80)
    
    # 创建智能顾问和扫描器
    advisor = SmartAdvisor(risk_tolerance="中等")
    scanner = MarketScanner(advisor)
    
    # 选择数据提供者
    if use_real_data:
        print("\n使用真实市场数据 (efinance)...")
        data_provider = EFinanceProvider()
        
        # 获取热门股票列表
        print("正在获取热门股票列表...")
        stock_list = data_provider.get_hot_stocks(20)
        
        if not stock_list:
            print("✗ 无法获取股票列表，使用默认列表")
            stock_list = [
                ("600519", "贵州茅台"),
                ("000858", "五粮液"),
                ("600036", "招商银行"),
                ("601318", "中国平安"),
                ("000333", "美的集团"),
            ]
    else:
        print("\n使用模拟数据...")
        from example_smart_advisor_mock import MockDataProvider
        data_provider = MockDataProvider()
        
        # 准备股票列表（示例）
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
    
    # 扫描市场
    print(f"\n开始扫描 {len(stock_list)} 只股票...")
    advice_list = scanner.scan_market(
        stock_list=stock_list,
        data_provider=data_provider,
        min_confidence=60
    )
    
    # 获取最佳投资标的
    top_picks = scanner.get_top_picks(advice_list, top_n=5)
    
    print(f"\n找到 {len(advice_list)} 个投资机会")
    print(f"\n【Top 5 投资标的】")
    print(f"{'排名':<6} {'代码':<10} {'名称':<10} {'信号':<12} {'评分':<8} {'信心度':<10} {'建议仓位':<10}")
    print("-" * 80)
    
    for i, advice in enumerate(top_picks, 1):
        print(f"{i:<6} {advice.stock_code:<10} {advice.stock_name:<10} "
              f"{advice.signal.value:<12} {advice.overall_score:<8.1f} "
              f"{advice.confidence:<10.1f}% {advice.position_size*100:<10.1f}%")
    
    print()
    
    return advice_list


def example_3_build_portfolio(advice_list):
    """示例3：构建投资组合"""
    print("=" * 80)
    print("示例3：构建投资组合")
    print("=" * 80)
    
    # 创建组合管理器
    initial_capital = 1000000  # 100万初始资金
    portfolio_mgr = PortfolioManager(initial_capital=initial_capital)
    
    # 构建组合（使用80%资金）
    available_capital = initial_capital * 0.8
    portfolio = portfolio_mgr.build_portfolio(
        advice_list=advice_list,
        available_capital=available_capital
    )
    
    # 生成报告
    report = portfolio_mgr.generate_portfolio_report(portfolio)
    print(report)
    
    return portfolio, portfolio_mgr


def example_4_risk_management(portfolio):
    """示例4：风险管理"""
    print("=" * 80)
    print("示例4：风险管理")
    print("=" * 80)
    
    # 创建风险管理器
    risk_mgr = RiskManager(max_portfolio_risk=0.20)
    
    # 检查组合风险
    risk_check = risk_mgr.check_portfolio_risk(portfolio)
    
    print(f"\n【组合风险评估】")
    print(f"风险等级: {risk_check['risk_level']}")
    
    if risk_check['warnings']:
        print(f"\n⚠️ 风险警告:")
        for warning in risk_check['warnings']:
            print(f"  - {warning}")
    else:
        print(f"\n✓ 暂无风险警告")
    
    if risk_check['suggestions']:
        print(f"\n💡 建议:")
        for suggestion in risk_check['suggestions']:
            print(f"  - {suggestion}")
    
    # 检查单个持仓风险
    print(f"\n【持仓风险检查】")
    for position in portfolio.positions:
        pos_risk = risk_mgr.check_position_risk(position, portfolio.total_value)
        
        status = "✓ 安全" if pos_risk['is_safe'] else "⚠️ 风险"
        print(f"\n{position.stock_name} ({position.stock_code}): {status}")
        
        if pos_risk['warnings']:
            for warning in pos_risk['warnings']:
                print(f"  警告: {warning}")
        
        if pos_risk['actions']:
            for action in pos_risk['actions']:
                print(f"  建议: {action}")
    
    print()


def example_5_rebalance(portfolio, portfolio_mgr, use_real_data: bool = True):
    """示例5：组合再平衡"""
    print("=" * 80)
    print("示例5：组合再平衡")
    print("=" * 80)
    
    # 模拟价格变化（实际应该获取最新价格）
    print("\n模拟市场变化...")
    for position in portfolio.positions:
        # 随机价格变化 -10% 到 +15%
        price_change = np.random.uniform(-0.10, 0.15)
        position.current_price = position.avg_cost * (1 + price_change)
        position.market_value = position.quantity * position.current_price
        position.profit_loss = position.market_value - (position.quantity * position.avg_cost)
        position.profit_loss_pct = (position.current_price / position.avg_cost - 1) * 100
        position.hold_days += 5
    
    # 获取新的投资建议
    advisor = SmartAdvisor(risk_tolerance="中等")
    scanner = MarketScanner(advisor)
    
    # 选择数据提供者
    if use_real_data:
        data_provider = EFinanceProvider()
    else:
        from example_smart_advisor_mock import MockDataProvider
        data_provider = MockDataProvider()
    
    stock_list = [(pos.stock_code, pos.stock_name) for pos in portfolio.positions]
    stock_list.extend([("002594", "比亚迪"), ("688981", "中芯国际")])
    
    new_advice_list = scanner.scan_market(stock_list, data_provider, min_confidence=60)
    
    # 再平衡
    rebalance_actions = portfolio_mgr.rebalance_portfolio(portfolio, new_advice_list)
    
    print(f"\n【再平衡建议】")
    if rebalance_actions:
        for stock_code, action in rebalance_actions.items():
            stock_name = next((pos.stock_name for pos in portfolio.positions 
                             if pos.stock_code == stock_code), 
                            next((adv.stock_name for adv in new_advice_list 
                                 if adv.stock_code == stock_code), "未知"))
            print(f"{stock_name} ({stock_code}): {action}")
    else:
        print("当前组合无需调整")
    
    print()


def example_6_different_risk_profiles(use_real_data: bool = True):
    """示例6：不同风险偏好的对比"""
    print("=" * 80)
    print("示例6：不同风险偏好的对比")
    print("=" * 80)
    
    # 准备数据
    stock_code = "600519"
    stock_name = "贵州茅台"
    
    # 选择数据提供者
    if use_real_data:
        data_provider = EFinanceProvider()
    else:
        from example_smart_advisor_mock import MockDataProvider
        data_provider = MockDataProvider()
    
    stock_data = data_provider.get_stock_data(stock_code)
    fundamental_data = data_provider.get_fundamental_data(stock_code)
    
    if stock_data.empty:
        print(f"✗ 无法获取 {stock_code} 的数据")
        return
    
    # 对比不同风险偏好
    risk_profiles = ["保守", "中等", "激进"]
    
    print(f"\n股票: {stock_name} ({stock_code})")
    print(f"\n{'风险偏好':<10} {'信号':<12} {'信心度':<10} {'建议仓位':<12} {'止损比例':<10}")
    print("-" * 70)
    
    for risk_profile in risk_profiles:
        advisor = SmartAdvisor(risk_tolerance=risk_profile)
        advice = advisor.analyze_stock(stock_code, stock_name, stock_data, fundamental_data)
        
        stop_loss_pct = (advice.stop_loss / advice.current_price - 1) * 100
        
        print(f"{risk_profile:<10} {advice.signal.value:<12} {advice.confidence:<10.1f}% "
              f"{advice.position_size*100:<12.1f}% {abs(stop_loss_pct):<10.1f}%")
    
    print()


def main():
    """主函数"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "智能投资顾问系统 - 使用示例" + " " * 28 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # 询问是否使用真实数据
    print("请选择数据源:")
    print("1. 真实市场数据 (efinance) - 推荐")
    print("2. 模拟数据 (用于测试)")
    
    choice = input("\n请输入选择 (1/2，默认1): ").strip() or "1"
    use_real_data = (choice == "1")
    
    if use_real_data:
        print("\n✓ 将使用真实市场数据")
        print("提示: 首次运行可能需要下载数据，请耐心等待...\n")
    else:
        print("\n✓ 将使用模拟数据\n")
    
    try:
        # 示例1：分析单只股票
        example_1_analyze_single_stock(use_real_data)
        input("按回车继续...")
        
        # 示例2：扫描市场
        advice_list = example_2_scan_market(use_real_data)
        
        if not advice_list:
            print("\n⚠️ 未找到符合条件的投资机会，跳过后续示例")
            return
        
        input("按回车继续...")
        
        # 示例3：构建组合
        portfolio, portfolio_mgr = example_3_build_portfolio(advice_list)
        input("按回车继续...")
        
        # 示例4：风险管理
        example_4_risk_management(portfolio)
        input("按回车继续...")
        
        # 示例5：组合再平衡
        example_5_rebalance(portfolio, portfolio_mgr, use_real_data)
        input("按回车继续...")
        
        # 示例6：不同风险偏好对比
        example_6_different_risk_profiles(use_real_data)
        
        print("\n" + "=" * 80)
        print("所有示例运行完成！")
        print("=" * 80)
        print("\n提示：")
        print("1. 真实数据来自efinance库，确保网络连接正常")
        print("2. 建议结合基本面研究和市场环境进行投资决策")
        print("3. 严格执行止损，控制风险")
        print("4. 定期回测和优化策略参数")
        print()
        
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
