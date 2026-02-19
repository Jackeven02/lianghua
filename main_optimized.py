"""
量化分析软件优化版主程序
集成 efinance 数据源和优化的用户界面
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTabWidget, QLabel, 
                           QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
                           QComboBox, QLineEdit, QGroupBox, QFormLayout, QSplitter,
                           QProgressBar, QStatusBar, QMenuBar, QAction, QTreeWidget,
                           QTreeWidgetItem, QHeaderView, QFrame)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_NAME, APP_VERSION
from data_layer import get_stock_data, get_fund_data, get_index_data, get_stock_list, get_fund_list

class DataWorker(QThread):
    """数据获取工作线程"""
    data_ready = pyqtSignal(object, str)  # 数据, 代码
    progress_update = pyqtSignal(int)     # 进度
    error_occurred = pyqtSignal(str)      # 错误信息
    
    def __init__(self, code, data_type, period):
        super().__init__()
        self.code = code
        self.data_type = data_type
        self.period = period
        
    def run(self):
        try:
            self.progress_update.emit(30)
            
            # 根据数据类型获取数据
            if self.data_type == "股票数据":
                data = get_stock_data(self.code, period=self.period)
            elif self.data_type == "基金数据":
                data = get_fund_data(self.code)
            else:  # 指数数据
                data = get_index_data(self.code, period=self.period)
            
            self.progress_update.emit(80)
            
            if data is not None and not data.empty:
                self.data_ready.emit(data, self.code)
            else:
                self.error_occurred.emit(f"未获取到 {self.code} 的数据")
                
            self.progress_update.emit(100)
            
        except Exception as e:
            self.error_occurred.emit(f"数据获取失败: {str(e)}")

class OptimizedDataView(QWidget):
    """优化的数据视图组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_data = None
        self.data_thread = None
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 标题栏
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        
        title_label = QLabel("📈 数据分析中心")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        layout.addWidget(title_frame)
        
        # 控制面板
        control_panel = QGroupBox("🔍 数据查询控制")
        control_panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        control_layout = QFormLayout(control_panel)
        control_layout.setSpacing(15)
        
        # 代码输入
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("输入股票/基金/指数代码，如：000001 或 159915")
        self.code_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        control_layout.addRow("📋 代码:", self.code_input)
        
        # 数据类型选择
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["股票数据", "基金数据", "指数数据"])
        self.data_type_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        control_layout.addRow("📎 类型:", self.data_type_combo)
        
        # 数据周期选择
        self.period_combo = QComboBox()
        self.period_combo.addItems(["日线", "周线", "月线", "15分钟", "30分钟", "60分钟"])
        self.period_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
            }
        """)
        control_layout.addRow("🕐 周期:", self.period_combo)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("🔍 获取数据")
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        
        control_layout.addRow(button_layout)
        layout.addWidget(control_panel)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 数据信息面板
        info_panel = QGroupBox("📊 数据信息")
        info_panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
            }
        """)
        info_layout = QVBoxLayout(info_panel)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.info_text.setText("📋 数据信息面板\n\n在此输入代码并点击获取数据按钮开始分析")
        info_layout.addWidget(self.info_text)
        
        splitter.addWidget(info_panel)
        
        # 数据表格
        table_panel = QGroupBox("📈 数据表格")
        table_panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #f39c12;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
            }
        """)
        table_layout = QVBoxLayout(table_panel)
        
        self.data_table = QTableWidget()
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                gridline-color: #e9ecef;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: none;
            }
        """)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_layout.addWidget(self.data_table)
        
        splitter.addWidget(table_panel)
        splitter.setSizes([300, 700])
        layout.addWidget(splitter)
        
        # 状态栏
        self.status_label = QLabel("✅ 就绪 - 请输入代码开始数据分析")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #27ae60;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.status_label)
        
        # 连接信号
        self.load_btn.clicked.connect(self.load_data)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.clear_btn.clicked.connect(self.clear_data)
        
    def load_data(self):
        """加载数据"""
        code = self.code_input.text().strip()
        if not code:
            self.status_label.setText("❌ 请输入代码")
            return
            
        data_type = self.data_type_combo.currentText()
        period = self.period_combo.currentText()
        
        # 显示加载状态
        self.status_label.setText(f"🔍 正在通过 efinance 获取 {code} 的 {data_type}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.load_btn.setEnabled(False)
        
        # 启动数据获取线程
        self.data_thread = DataWorker(code, data_type, self.map_period(period))
        self.data_thread.data_ready.connect(self.on_data_received)
        self.data_thread.progress_update.connect(self.progress_bar.setValue)
        self.data_thread.error_occurred.connect(self.on_data_error)
        self.data_thread.finished.connect(self.on_thread_finished)
        self.data_thread.start()
    
    def map_period(self, period_text):
        """映射周期文本到数据层格式"""
        period_map = {
            "日线": "daily",
            "周线": "weekly",
            "月线": "monthly", 
            "15分钟": "15min",
            "30分钟": "30min",
            "60分钟": "60min"
        }
        return period_map.get(period_text, "daily")
    
    def on_data_received(self, data, code):
        """数据接收处理"""
        try:
            self.current_data = data
            
            # 更新信息面板
            info_text = f"📊 {code} 数据信息\n"
            info_text += "=" * 40 + "\n\n"
            info_text += f"📋 数据类型: {self.data_type_combo.currentText()}\n"
            info_text += f"🕐 数据周期: {self.period_combo.currentText()}\n"
            info_text += f"📊 数据条数: {len(data)}\n"
            info_text += f"💾 数据大小: {data.memory_usage(deep=True).sum() / 1024:.2f} KB\n\n"
            
            # 统计信息
            if self.data_type_combo.currentText() == "股票数据" and 'close' in data.columns:
                info_text += "📈 价格统计:\n"
                info_text += f"• 最新收盘价: {data['close'].iloc[-1]:.2f}\n"
                info_text += f"• 最高价: {data['high'].max():.2f}\n"
                info_text += f"• 最低价: {data['low'].min():.2f}\n"
                info_text += f"• 平均成交量: {data['volume'].mean():,.0f}\n"
            elif self.data_type_combo.currentText() == "基金数据" and 'nav' in data.columns:
                info_text += "💰 基金统计:\n"
                info_text += f"• 最新净值: {data['nav'].iloc[-1]:.4f}\n"
                info_text += f"• 累计净值: {data['accumulated_nav'].iloc[-1]:.4f}\n"
            
            self.info_text.setText(info_text)
            
            # 更新数据表格
            self.display_data_table(data)
            
            self.status_label.setText(f"✅ {code} 数据获取成功 - 共 {len(data)} 条记录")
            
        except Exception as e:
            self.info_text.setText(f"❌ 数据处理错误: {str(e)}")
            self.status_label.setText("❌ 数据处理失败")
    
    def display_data_table(self, data):
        """显示数据表格"""
        self.data_table.setRowCount(len(data))
        self.data_table.setColumnCount(len(data.columns))
        self.data_table.setHorizontalHeaderLabels(data.columns.tolist())
        
        for row in range(len(data)):
            for col, column_name in enumerate(data.columns):
                item = QTableWidgetItem(str(data.iloc[row, col]))
                self.data_table.setItem(row, col, item)
    
    def on_data_error(self, error_message):
        """数据错误处理"""
        self.info_text.setText(f"❌ 数据获取失败\n\n错误信息: {error_message}")
        self.status_label.setText("❌ 数据获取失败")
        self.data_table.clear()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
    
    def on_thread_finished(self):
        """线程结束处理"""
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
    
    def refresh_data(self):
        """刷新数据"""
        if self.current_data is not None:
            self.load_data()
        else:
            self.status_label.setText("❌ 没有可刷新的数据")
    
    def clear_data(self):
        """清空数据"""
        self.info_text.setText("📋 数据信息面板\n\n在此输入代码并点击获取数据按钮开始分析")
        self.data_table.clear()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
        self.code_input.clear()
        self.status_label.setText("📝 数据已清空 - 就绪状态")

class OptimizedMainWindow(QMainWindow):
    """优化版主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f'{APP_NAME} v{APP_VERSION} - 专业量化分析平台 (efinance版)')
        self.setGeometry(50, 50, 1600, 1000)
        self.setMinimumSize(1400, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(OptimizedDataView(), "📈 数据分析")
        # 这里可以添加其他标签页
        
        main_layout.addWidget(self.tab_widget)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🚀 Quant Analyzer efinance版就绪 - 数据分析功能已加载")
        
        # 定时更新状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(3000)
        
    def update_status(self):
        """更新状态栏"""
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        self.status_bar.showMessage(f"📊 Quant Analyzer v{APP_VERSION} | {current_time} | 当前模块: {current_tab}")

def main():
    """主函数"""
    print(f"🚀 启动 {APP_NAME} v{APP_VERSION} 优化版")
    print("🔧 正在初始化基于 efinance 的量化分析平台...")
    print("📋 数据源: efinance 实时金融数据接口")
    print("🎨 界面: 优化的现代化UI设计")
    
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    try:
        main_window = OptimizedMainWindow()
        main_window.show()
        print("✅ 优化版主窗口启动成功")
        print("📈 数据分析模块已加载 (使用 efinance)")
        print("📊 实时数据获取功能正常")
        print("🎨 现代化界面已启用")
        
        exit_code = app.exec_()
        print("👋 应用程序已退出")
        return exit_code
        
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())