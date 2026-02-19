#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print('Starting Quant Analyzer - Smart Quantitative Analysis Platform')
print('Initializing...')

try:
    from strategy_layer.smart_strategy_engine import SmartMarketAnalyzer
    print('Smart analyzer module loaded successfully')
    
    from PyQt5.QtWidgets import QApplication
    from ui_layer.main_window import MainWindow
    
    print('All dependencies imported successfully')
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.setWindowTitle('Smart Quantitative Analysis Platform - Quant Analyzer')
    main_window.show()
    
    print('Main window launched successfully')
    print('Five functional modules loaded:')
    print('   - Data Analysis')
    print('   - Technical Analysis') 
    print('   - Strategy Editor')
    print('   - Backtest Results')
    print('   - Smart Analysis')
    print()
    print('Smart Investment Advisory System Features:')
    print('   - Autonomous Market Analysis')
    print('   - Proactive Investment Suggestions')
    print('   - Real-time efinance Data Integration')
    print('   - Multi-dimensional Strategy Analysis')
    print()
    print('Please check the pop-up window to use the full functionality')
    print('Smart Quantitative Analysis Platform is ready!')
    
    sys.exit(app.exec_())
    
except ImportError as e:
    print(f'Import error: {e}')
    print('Please ensure all dependencies are installed: pip install PyQt5 pandas numpy efinance')
except Exception as e:
    print(f'Startup failed: {e}')
    import traceback
    traceback.print_exc()
