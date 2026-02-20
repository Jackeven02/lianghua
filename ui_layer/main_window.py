import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QTabWidget, QLabel, QStatusBar)
from PyQt5.QtCore import Qt
from .data_view import DataView
from .analysis_view import AnalysisView
from .strategy_view import StrategyView
from .backtest_view import BacktestView
from .smart_analysis_view import SmartAnalysisView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Quant Analyzer - 智能量化分析平台')
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title_label = QLabel('Quant Analyzer - 智能量化分析平台')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin: 15px; color: #2c3e50;")
        main_layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 添加各个视图
        self.data_view = DataView()
        self.analysis_view = AnalysisView()
        self.strategy_view = StrategyView()
        self.backtest_view = BacktestView()
        self.smart_analysis_view = SmartAnalysisView()
        
        self.tab_widget.addTab(self.data_view, "数据分析")
        self.tab_widget.addTab(self.analysis_view, "技术分析")
        self.tab_widget.addTab(self.strategy_view, "策略编辑")
        self.tab_widget.addTab(self.backtest_view, "回测结果")
        self.tab_widget.addTab(self.smart_analysis_view, "智能分析")
        
        main_layout.addWidget(self.tab_widget)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Quant Analyzer 就绪 - 智能量化分析平台")
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #bdc3c7;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)