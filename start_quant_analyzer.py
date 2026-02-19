#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print(' 启动 Quant Analyzer - 智能量化分析平台')
print(' 正在初始化...')

# 直接导入并启动
try:
    from strategy_layer.smart_strategy_engine import SmartMarketAnalyzer
    print(' 智能分析器模块加载成功')
    
    from PyQt5.QtWidgets import QApplication
    from ui_layer.main_window import MainWindow
    
    print(' 所有依赖导入成功')
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.setWindowTitle('智能量化分析平台 - Quant Analyzer')
    main_window.show()
    
    print(' 智能版主窗口已启动')
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
    print()
    print(' 项目已成功启动！')
    print(' 智能量化分析平台运行中...')
    
    sys.exit(app.exec_())
    
except ImportError as e:
    print(f' 导入错误: {e}')
    print(' 请确保已安装所有依赖: pip install PyQt5 pandas numpy efinance')
except Exception as e:
    print(f' 启动失败: {e}')
    import traceback
    traceback.print_exc()
