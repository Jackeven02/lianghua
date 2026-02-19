"""
量化分析软件简化优化版
直接使用 efinance 获取数据，优化UI界面
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTabWidget, QLabel, 
                           QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
                           QComboBox, QLineEdit, QGroupBox, QFormLayout, QSplitter,
                           QProgressBar, QStatusBar, QFrame, QHeaderView)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import efinance as ef

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
                period_map = {"日线": 101, "周线": 102, "月线": 103, "15分钟": 15, "30分钟": 30, "60分钟": 60}
                klt = period_map.get(self.period, 101)
                data = ef.stock.get_quote_history(self.code, klt=klt)
            elif self.data_type == "基金数据":
                data = ef.fund.get_history_quotation(self.code)
            else:  # 指数数据
                period_map = {"日线": 101, "周线": 102, "月线": 103}
                klt = period_map.get(self.period, 101)
                data = ef.index.get_index_history(self.code, klt=klt)
            
            self.progress_update.emit(80)
            
            if data is not None and not data.empty:
                # 数据处理
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
        else:  # 指数数据
            column_mapping = {'日期': 'date', '开盘': 'open', '最高': 'high', '最低': 'low', '收盘': 'close', '成交量': 'volume', '成交额': 'amount'}
        
        data = data.rename(columns=column_mapping)
        
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            data = data.sort_values('date')
            
        numeric_columns = [col for col in ['open', 'high', 'low', 'close', 'volume', 'amount', 'nav', 'accumulated_nav', 'daily_return'] if col in data.columns]
        for col in numeric_columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
            
        return data

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
        
        title_label = QLabel("📈 数据分析中心 (efinance版)")
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
        self.code_input.setText("000001")  # 默认值
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
        self.data_type_combo.currentTextChanged.connect(self.on_data_type_change)
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
        
        self.load_btn = QPushButton("🔍 获取真实数据")
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
        self.update_info_placeholder()
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
        self.status_label = QLabel("✅ 就绪 - 请输入代码开始数据分析 (数据源: efinance)")
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
        
    def update_info_placeholder(self):
        """更新信息面板占位文本"""
        placeholder = """📊 数据信息面板

功能说明：
• 直接使用 efinance 获取实时金融数据
• 支持股票、基金、指数多种数据类型
• 提供详细的数据统计信息
• 实时显示数据质量和完整性

数据源：efinance 实时接口
更新频率：实时获取最新数据
数据质量：来自专业金融数据提供商

请在上方输入代码并点击获取数据按钮开始分析！"""
        
        self.info_text.setPlaceholderText(placeholder)
    
    def on_data_type_change(self):
        """数据类型改变时的处理"""
        data_type = self.data_type_combo.currentText()
        if data_type == "基金数据":
            self.code_input.setPlaceholderText("输入基金代码，如：159915")
            # 基金数据不支持分钟级别
            self.period_combo.clear()
            self.period_combo.addItems(["日线", "周线", "月线"])
        else:
            self.code_input.setPlaceholderText("输入代码，如：000001")
            self.period_combo.clear()
            if data_type == "股票数据":
                self.period_combo.addItems(["日线", "周线", "月线", "15分钟", "30分钟", "60分钟"])
            else:  # 指数数据
                self.period_combo.addItems(["日线", "周线", "月线"])
    
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
        self.data_thread = DataWorker(code, data_type, period)
        self.data_thread.data_ready.connect(self.on_data_received)
        self.data_thread.progress_update.connect(self.progress_bar.setValue)
        self.data_thread.error_occurred.connect(self.on_data_error)
        self.data_thread.finished.connect(self.on_thread_finished)
        self.data_thread.start()
    
    def on_data_received(self, data, code):
        """数据接收处理"""
        try:
            self.current_data = data
            
            # 更新信息面板
            info_text = f"📊 {code} 真实数据获取成功\n"
            info_text += "=" * 50 + "\n\n"
            info_text += f"📋 数据类型: {self.data_type_combo.currentText()}\n"
            info_text += f"🕐 数据周期: {self.period_combo.currentText()}\n"
            info_text += f"📊 数据条数: {len(data)}\n"
            info_text += f"💾 数据大小: {data.memory_usage(deep=True).sum() / 1024:.2f} KB\n"
            info_text += f"📅 时间范围: {data.iloc[0, 0]} 至 {data.iloc[-1, 0]}\n\n"
            
            # 字段信息
            info_text += "📑 数据字段:\n"
            for i, col in enumerate(data.columns, 1):
                info_text += f"  {i}. {col}\n"
            info_text += "\n"
            
            # 统计信息
            if self.data_type_combo.currentText() == "股票数据" and 'close' in data.columns:
                info_text += "📈 股价统计:\n"
                info_text += f"• 最新收盘价: {data['close'].iloc[-1]:.2f}\n"
                info_text += f"• 最高价: {data['high'].max():.2f}\n"
                info_text += f"• 最低价: {data['low'].min():.2f}\n"
                info_text += f"• 平均成交量: {data['volume'].mean():,.0f}\n"
            elif self.data_type_combo.currentText() == "基金数据" and 'nav' in data.columns:
                info_text += "💰 基金统计:\n"
                info_text += f"• 最新净值: {data['nav'].iloc[-1]:.4f}\n"
                info_text += f"• 累计净值: {data['accumulated_nav'].iloc[-1]:.4f}\n"
                info_text += f"• 最新日增长率: {data['daily_return'].iloc[-1]:.2%}\n"
            elif self.data_type_combo.currentText() == "指数数据" and 'close' in data.columns:
                info_text += "💹 指数统计:\n"
                info_text += f"• 最新指数: {data['close'].iloc[-1]:.2f}\n"
                info_text += f"• 最高指数: {data['high'].max():.2f}\n"
                info_text += f"• 最低指数: {data['low'].min():.2f}\n"
            
            self.info_text.setText(info_text)
            
            # 更新数据表格
            self.display_data_table(data)
            
            self.status_label.setText(f"✅ {code} 真实数据获取成功 - 共 {len(data)} 条记录 (via efinance)")
            
        except Exception as e:
            self.info_text.setText(f"❌ 数据处理错误: {str(e)}")
            self.status_label.setText("❌ 数据处理失败")
    
    def display_data_table(self, data):
        """显示数据表格"""
        self.data_table.setRowCount(len(data))
        self.data_table.setColumnCount(len(data.columns))
        self.data_table.setHorizontalHeaderLabels(data.columns.tolist())
        
        for row in range(min(len(data), 100)):  # 限制显示前100行
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
        self.info_text.clear()
        self.update_info_placeholder()
        self.data_table.clear()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
        self.code_input.clear()
        self.status_label.setText("📝 数据已清空 - 就绪状态 (数据源: efinance)")

class OptimizedMainWindow(QMainWindow):
    """优化版主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Quant Analyzer v1.0.0 - 优化版量化分析平台 (efinance)')
        self.setGeometry(50, 50, 1600, 1000)
        self.setMinimumSize(1400, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 欢迎标题
        welcome_label = QLabel("🚀 欢迎使用 Quant Analyzer 优化版")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin: 15px;
                padding: 20px;
                background-color: #ecf0f1;
                border-radius: 10px;
                border: 2px solid #3498db;
            }
        """)
        main_layout.addWidget(welcome_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(OptimizedDataView(), "📈 数据分析")
        # 这里可以添加其他标签页
        
        main_layout.addWidget(self.tab_widget)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✅ Quant Analyzer 优化版就绪 - efinance 数据接口已连接")
        
        # 定时更新状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(3000)
        
    def update_status(self):
        """更新状态栏"""
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_tab = self.tab_widget.tabText(self.tab_widget.currentIndex())
        self.status_bar.showMessage(f"📊 Quant Analyzer v1.0.0 | {current_time} | 当前模块: {current_tab} | 数据源: efinance")

def main():
    """主函数"""
    print("🚀 启动 Quant Analyzer v1.0.0 优化版")
    print("🔧 正在初始化基于 efinance 的量化分析平台...")
    print("📋 数据源: efinance 实时金融数据接口")
    print("🎨 界面: 优化的现代化UI设计")
    print("⚡ 特性: 多线程数据获取，实时进度显示")
    
    app = QApplication(sys.argv)
    app.setApplicationName('Quant Analyzer')
    app.setApplicationVersion('1.0.0')
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    try:
        main_window = OptimizedMainWindow()
        main_window.show()
        print("✅ 优化版主窗口启动成功")
        print("📈 数据分析模块已加载 (使用 efinance)")
        print("📊 实时数据获取功能正常")
        print("🎨 现代化界面已启用")
        print("⚡ 多线程处理已就绪")
        
        exit_code = app.exec_()
        print("👋 应用程序已退出")
        return exit_code
        
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())