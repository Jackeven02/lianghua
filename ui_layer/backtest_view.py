"""
回测视图控制器
负责策略回测和结果展示功能
"""

from PyQt5.QtWidgets import QLabel, QVBoxLayout
from ui_layer.base_view import BaseViewController

class BacktestViewController(BaseViewController):
    """回测视图控制器"""
    
    def __init__(self):
        super().__init__("📊 回测系统")
        self.init_backtest_ui()
        
    def init_backtest_ui(self):
        """初始化回测界面"""
        info_label = QLabel("回测系统功能开发中...")
        info_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 16px;
                padding: 20px;
                text-align: center;
            }
        """)
        info_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(info_label)