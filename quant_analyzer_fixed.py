#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    try:
        # 导入智能分析器
        from strategy_layer.smart_strategy_engine import SmartMarketAnalyzer
        
        # 测试基本功能
        analyzer = SmartMarketAnalyzer()
        
        # 尝试启动GUI
        try:
            from PyQt5.QtWidgets import QApplication
            from ui_layer.main_window import MainWindow
            
            # 创建Qt应用程序
            app = QApplication(sys.argv)
            main_window = MainWindow()
            main_window.setWindowTitle('智能量化分析平台 - Quant Analyzer')
            main_window.show()
            
            print(' 智能量化分析平台已启动')
            print(' 五大功能模块已加载：')
            print('   - 数据分析')
            print('   - 技术分析')
            print('   - 策略编辑')
            print('   - 回测结果')
            print('   - 智能分析')
            print()
            print(' 智能投顾系统特性：')
            print('   - 自主市场分析')
            print('   - 主动投资建议')
            print('   - 实时efinance数据对接')
            print('   - 多维度策略分析')
            
            # 启动事件循环
            exit_code = app.exec_()
            sys.exit(exit_code)
            
        except ImportError as e:
            print(f'GUI模式不可用: {e}')
            # 即使GUI不可用，也要展示核心功能
            import pandas as pd
            import numpy as np
            
            # 创建测试数据
            dates = pd.date_range('2024-01-01', periods=30, freq='D')
            prices = 100 + np.cumsum(np.random.randn(30) * 0.2)
            data = pd.DataFrame({
                'date': dates,
                'close': prices,
                'open': prices * (1 + np.random.randn(30) * 0.01),
                'high': prices * (1 + abs(np.random.randn(30)) * 0.02),
                'low': prices * (1 - abs(np.random.randn(30)) * 0.02),
                'volume': np.random.randint(1000000, 5000000, 30)
            })
            
            # 测试智能分析
            market_condition = analyzer.analyze_market_condition(data)
            suggestions = analyzer.generate_investment_suggestions(data, '000001')
            
            print(f' 市场分析: {market_condition}')
            print(f' 生成建议: {len(suggestions)} 条')
            
            if suggestions:
                suggestion = suggestions[0]
                print(f' 建议: {suggestion.action.upper()} {suggestion.stock_code}')
                print(f' 置信度: {suggestion.confidence}%')
            
            print()
            print(' 智能量化分析平台核心功能运行正常！')
            
    except Exception as e:
        print(f'启动失败: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
