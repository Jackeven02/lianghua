"""
量化分析软件精美版
专业级UI设计，现代化视觉效果
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTabWidget, QLabel, 
                           QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
                           QComboBox, QLineEdit, QGroupBox, QFormLayout, QSplitter,
                           QProgressBar, QStatusBar, QMenuBar, QAction, QTreeWidget,
                           QTreeWidgetItem, QHeaderView, QFrame, QStackedWidget,
                           QScrollArea, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPalette, QColor
import pandas as pd
import numpy as np
import efinance as ef

class ModernDataWorker(QThread):
    """现代化数据获取工作线程"""
    data_ready = pyqtSignal(object, str)
    progress_update = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, code, data_type, period):
        super().__init__()
        self.code = code
        self.data_type = data_type
        self.period = period
        
    def run(self):
        try:
            self.progress_update.emit(20)
            
            if self.data_type == "股票数据":
                period_map = {"日线": 101, "周线": 102, "月线": 103, "15分钟": 15, "30分钟": 30, "60分钟": 60}
                klt = period_map.get(self.period, 101)
                data = ef.stock.get_quote_history(self.code, klt=klt)
            elif self.data_type == "基金数据":
                data = ef.fund.get_history_quotation(self.code)
            else:  # 指数数据
                period_map = {"日线": 101, "周线": 102, "月线": 103}
                klt = period_map.get(self.period, 101)
                data = ef.index.get_index_history(self.code, klt=klt)
            
            self.progress_update.emit(70)
            
            if data is not None and not data.empty:
                data = self.process_data(data, self.data_type)
                self.data_ready.emit(data, self.code)
            else:
                self.error_occurred.emit(f"未获取到 {self.code} 的数据")
                
            self.progress_update.emit(100)
            
        except Exception as e:
            self.error_occurred.emit(f"数据获取失败: {str(e)}")
    
    def process_data(self, data, data_type):
        """处理数据"""
        if data_type == "股票数据":
            column_mapping = {'日期': 'date', '开盘': 'open', '最高': 'high', '最低': 'low', '收盘': 'close', '成交量': 'volume', '成交额': 'amount'}
        elif data_type == "基金数据":
            column_mapping = {'净值日期': 'date', '单位净值': 'nav', '累计净值': 'accumulated_nav', '日增长率': 'daily_return'}
        else:
            column_mapping = {'日期': 'date', '开盘': 'open', '最高': 'high', '最低': 'low', '收盘': 'close', '成交量': 'volume', '成交额': 'amount'}
        
        data = data.rename(columns=column_mapping)
        
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            data = data.sort_values('date')
            
        numeric_columns = [col for col in ['open', 'high', 'low', 'close', 'volume', 'amount', 'nav', 'accumulated_nav', 'daily_return'] if col in data.columns]
        for col in numeric_columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
            
        return data

class ModernDataView(QWidget):
    """精美数据视图"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_data = None
        self.data_thread = None
        
    def init_ui(self):
        # 设置背景色
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 顶部卡片
        header_card = QFrame()
        header_card.setStyleSheet("""
            QFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c3e50, stop:1 #3498db);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        header_layout = QHBoxLayout(header_card)
        
        # 标题和图标
        title_layout = QVBoxLayout()
        title_icon = QLabel("📈")
        title_icon.setStyleSheet("font-size: 36px; color: white;")
        title_layout.addWidget(title_icon)
        
        title_label = QLabel("数据分析中心")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                margin-top: 10px;
            }
        """)
        title_layout.addWidget(title_label)
        header_layout.addLayout(title_layout)
        
        # 数据源信息
        source_info = QLabel("数据源: efinance 实时接口")
        source_info.setStyleSheet("""
            QLabel {
                color: #ecf0f1;
                font-size: 14px;
                margin-top: 15px;
            }
        """)
        title_layout.addWidget(source_info)
        header_layout.addStretch()
        
        main_layout.addWidget(header_card)
        
        # 控制面板卡片
        control_card = QFrame()
        control_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                border: 1px solid #e9ecef;
            }
        """)
        control_layout = QVBoxLayout(control_card)
        
        # 控制面板标题
        control_title = QLabel("🔍 数据查询控制")
        control_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 15px;
            }
        """)
        control_layout.addWidget(control_title)
        
        # 表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # 代码输入
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("请输入股票/基金/指数代码，如：000001")
        self.code_input.setText("000001")
        self.code_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #3498db;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border-color: #2980b9;
                background-color: white;
            }
        """)
        form_layout.addRow("📋 代码:", self.code_input)
        
        # 数据类型选择
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["股票数据", "基金数据", "指数数据"])
        self.data_type_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #3498db;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        form_layout.addRow("📎 类型:", self.data_type_combo)
        
        # 数据周期选择
        self.period_combo = QComboBox()
        self.period_combo.addItems(["日线", "周线", "月线", "15分钟", "30分钟", "60分钟"])
        self.period_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 2px solid #3498db;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
        """)
        form_layout.addRow("🕐 周期:", self.period_combo)
        
        control_layout.addLayout(form_layout)
        
        # 操作按钮区域
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
                margin-top: 15px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        
        self.load_btn = QPushButton("🔍 获取数据")
        self.load_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2980b9, stop:1 #21618c);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #21618c, stop:1 #1a5276);
            }
        """)
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #95a5a6, stop:1 #7f8c8d);
                color: white;
                border: none;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7f8c8d, stop:1 #6c7a7d);
            }
        """)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: none;
                padding: 12px 25px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #c0392b, stop:1 #a93226);
            }
        """)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        
        control_layout.addWidget(button_frame)
        main_layout.addWidget(control_card)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 10px;
                text-align: center;
                height: 25px;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3498db, stop:1 #2980b9);
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # 数据显示区域
        display_splitter = QSplitter(Qt.Horizontal)
        display_splitter.setHandleWidth(8)
        
        # 信息面板
        info_panel = QFrame()
        info_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e9ecef;
            }
        """)
        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        info_title = QLabel("📊 数据信息")
        info_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #27ae60;
                margin-bottom: 10px;
            }
        """)
        info_layout.addWidget(info_title)
        
        self.info_display = QTextEdit()
        self.info_display.setPlaceholderText("在此输入代码并点击获取数据按钮开始分析...")
        self.info_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                color: #2c3e50;
            }
        """)
        info_layout.addWidget(self.info_display)
        
        display_splitter.addWidget(info_panel)
        
        # 数据表格
        table_panel = QFrame()
        table_panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e9ecef;
            }
        """)
        table_layout = QVBoxLayout(table_panel)
        table_layout.setContentsMargins(15, 15, 15, 15)
        
        table_title = QLabel("📈 数据表格")
        table_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #f39c12;
                margin-bottom: 10px;
            }
        """)
        table_layout.addWidget(table_title)
        
        self.data_table = QTableWidget()
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                gridline-color: #dee2e6;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e9ecef;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9);
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
        """)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_layout.addWidget(self.data_table)
        
        display_splitter.addWidget(table_panel)
        display_splitter.setSizes([350, 650])
        main_layout.addWidget(display_splitter)
        
        # 状态栏卡片
        status_card = QFrame()
        status_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #27ae60, stop:1 #2ecc71);
                border-radius: 10px;
                padding: 12px;
            }
        """)
        status_layout = QHBoxLayout(status_card)
        
        self.status_label = QLabel("✅ 就绪 - 请输入代码开始数据分析")
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        status_layout.addWidget(self.status_label)
        main_layout.addWidget(status_card)
        
        # 连接信号
        self.load_btn.clicked.connect(self.load_data)
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.clear_btn.clicked.connect(self.clear_data)
        
    def load_data(self):
        code = self.code_input.text().strip()
        if not code:
            self.status_label.setText("❌ 请输入代码")
            return
            
        data_type = self.data_type_combo.currentText()
        period = self.period_combo.currentText()
        
        self.status_label.setText(f"🔍 正在获取 {code} 数据...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.load_btn.setEnabled(False)
        
        self.data_thread = ModernDataWorker(code, data_type, period)
        self.data_thread.data_ready.connect(self.on_data_received)
        self.data_thread.progress_update.connect(self.progress_bar.setValue)
        self.data_thread.error_occurred.connect(self.on_data_error)
        self.data_thread.finished.connect(self.on_thread_finished)
        self.data_thread.start()
    
    def on_data_received(self, data, code):
        self.current_data = data
        
        info_text = f"📊 {code} 数据获取成功\n"
        info_text += "=" * 40 + "\n\n"
        info_text += f"📋 数据类型: {self.data_type_combo.currentText()}\n"
        info_text += f"🕐 数据周期: {self.period_combo.currentText()}\n"
        info_text += f"📊 数据条数: {len(data)}\n"
        info_text += f"💾 数据大小: {data.memory_usage(deep=True).sum() / 1024:.2f} KB\n\n"
        
        if self.data_type_combo.currentText() == "股票数据" and 'close' in data.columns:
            info_text += "📈 价格统计:\n"
            info_text += f"• 最新收盘价: {data['close'].iloc[-1]:.2f}\n"
            info_text += f"• 最高价格: {data['high'].max():.2f}\n"
            info_text += f"• 最低价格: {data['low'].min():.2f}\n"
        elif self.data_type_combo.currentText() == "基金数据" and 'nav' in data.columns:
            info_text += "💰 基金统计:\n"
            info_text += f"• 最新净值: {data['nav'].iloc[-1]:.4f}\n"
            info_text += f"• 累计净值: {data['accumulated_nav'].iloc[-1]:.4f}\n"
            
        self.info_display.setText(info_text)
        
        self.data_table.setRowCount(len(data))
        self.data_table.setColumnCount(len(data.columns))
        self.data_table.setHorizontalHeaderLabels(data.columns.tolist())
        
        for row in range(min(len(data), 100)):
            for col, column_name in enumerate(data.columns):
                item = QTableWidgetItem(str(data.iloc[row, col]))
                self.data_table.setItem(row, col, item)
                
        self.status_label.setText(f"✅ {code} 数据获取成功 - 共 {len(data)} 条记录")
    
    def on_data_error(self, error_message):
        self.info_display.setText(f"❌ 数据获取失败\n\n错误信息: {error_message}")
        self.status_label.setText("❌ 数据获取失败")
        self.data_table.clear()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
    
    def on_thread_finished(self):
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
    
    def refresh_data(self):
        if self.current_data is not None:
            self.load_data()
    
    def clear_data(self):
        self.info_display.clear()
        self.info_display.setPlaceholderText("在此输入代码并点击获取数据按钮开始分析...")
        self.data_table.clear()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
        self.code_input.clear()
        self.status_label.setText("✅ 就绪 - 请输入代码开始数据分析")

class ModernMainWindow(QMainWindow):
    """精美主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Quant Analyzer v1.0.0 - 精美版量化分析平台')
        self.setGeometry(30, 30, 1700, 1100)
        self.setMinimumSize(1500, 900)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
        """)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 欢迎横幅
        banner = QFrame()
        banner.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8e44ad, stop:1 #9b59b6);
                padding: 25px;
            }
        """)
        banner_layout = QHBoxLayout(banner)
        
        welcome_title = QLabel("🚀 欢迎使用 Quant Analyzer 精美版")
        welcome_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        banner_layout.addWidget(welcome_title)
        banner_layout.addStretch()
        
        main_layout.addWidget(banner)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #f8f9fa;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ecf0f1, stop:1 #bdc3c7);
                border: 1px solid #95a5a6;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 20px;
                margin-right: 2px;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border-color: #2980b9;
            }
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d5dbdb, stop:1 #bdc3c7);
            }
        """)
        
        self.tab_widget.addTab(ModernDataView(), "📈 数据分析")
        # 其他模块可以后续添加
        
        main_layout.addWidget(self.tab_widget)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2c3e50, stop:1 #34495e);
                color: white;
                border: none;
                padding: 8px;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✨ Quant Analyzer 精美版就绪 - efinance 数据接口已连接")
        
        # 定时更新状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)
        
    def update_status(self):
        """更新状态栏"""
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        self.status_bar.showMessage(f"✨ Quant Analyzer v1.0.0 | {current_time} | 模块: {current_tab} | 数据源: efinance 实时接口")

def main():
    """主函数"""
    print("🌟 启动 Quant Analyzer v1.0.0 精美版")
    print("🎨 正在初始化精美UI量化分析平台...")
    print("✨ 特色: 现代化设计、渐变色彩、卡片布局")
    print("📊 数据源: efinance 实时金融数据接口")
    
    app = QApplication(sys.argv)
    app.setApplicationName('Quant Analyzer')
    app.setApplicationVersion('1.0.0')
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    try:
        main_window = ModernMainWindow()
        main_window.show()
        print("✅ 精美版主窗口启动成功")
        print("🎨 现代化UI界面已启用")
        print("✨ 渐变色彩和卡片设计已应用")
        print("📊 数据分析模块正常运行")
        
        exit_code = app.exec_()
        print("👋 应用程序已退出")
        return exit_code
        
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())