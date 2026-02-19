#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# 确保当前目录在路径中
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

def main():
    print(' 启动 Quant Analyzer - 智能量化分析平台')
    print(' 正在初始化...')
    
    try:
        from PyQt5.QtWidgets import QApplication
        from ui_layer.main_window import MainWindow
        
        app = QApplication(sys.argv)
        main_window = MainWindow()
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
        print(' 请查看弹出的窗口以使用完整功能')
        print(' 智能量化分析平台已准备就绪！')
        
        return app.exec_()
        
    except ImportError as e:
        print(f' 导入错误: {e}')
        print('请确保已安装所有依赖项：pip install PyQt5 pandas numpy efinance')
        return 1
    except Exception as e:
        print(f' 启动失败: {e}')
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
