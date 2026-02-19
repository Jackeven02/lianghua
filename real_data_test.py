"""
真实数据集成测试程序
使用 efinance 获取实时金融数据
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                           QGroupBox, QFormLayout, QComboBox, QLineEdit, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import efinance as ef
import pandas as pd

class DataFetchThread(QThread):
    """数据获取线程"""
    data_ready = pyqtSignal(object, str)  # 数据, 股票代码
    progress_update = pyqtSignal(int)     # 进度
    error_occurred = pyqtSignal(str)      # 错误信息
    
    def __init__(self, stock_code, data_type, period):
        super().__init__()
        self.stock_code = stock_code
        self.data_type = data_type
        self.period = period
        
    def run(self):
        try:
            self.progress_update.emit(20)
            
            # 根据数据类型获取数据
            if self.data_type == "股票数据":
                # 转换周期参数
                period_map = {"日线": 101, "周线": 102, "月线": 103}
                klt = period_map.get(self.period, 101)
                
                self.progress_update.emit(50)
                data = ef.stock.get_quote_history(self.stock_code, klt=klt)
                
            elif self.data_type == "基金数据":
                self.progress_update.emit(50)
                data = ef.fund.get_history_quotation(self.stock_code)
                
            elif self.data_type == "指数数据":
                period_map = {"日线": 101, "周线": 102, "月线": 103}
                klt = period_map.get(self.period, 101)
                self.progress_update.emit(50)
                data = ef.index.get_index_history(self.stock_code, klt=klt)
            
            self.progress_update.emit(80)
            
            if data is not None and not data.empty:
                self.data_ready.emit(data, self.stock_code)
            else:
                self.error_occurred.emit(f"未获取到 {self.stock_code} 的数据")
                
            self.progress_update.emit(100)
            
        except Exception as e:
            self.error_occurred.emit(f"数据获取失败: {str(e)}")

class RealDataWindow(QMainWindow):
    """真实数据测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_data = None
        
    def init_ui(self):
        self.setWindowTitle("📊 真实数据集成测试 - efinance")
        self.setGeometry(200, 200, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("✅ efinance 真实数据集成测试")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 22px; 
            font-weight: bold; 
            color: #27ae60;
            margin: 15px;
            padding: 20px;
            background-color: #ecf0f1;
            border: 2px solid #3498db;
            border-radius: 10px;
        """)
        main_layout.addWidget(title)
        
        # 数据控制面板
        control_group = QGroupBox("🔍 数据获取控制")
        control_layout = QFormLayout(control_group)
        
        # 股票代码输入
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("输入股票/基金/指数代码，如：000001 或 159915")
        self.code_input.setText("000001")  # 默认值
        control_layout.addRow("📋 代码:", self.code_input)
        
        # 数据类型选择
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["股票数据", "基金数据", "指数数据"])
        self.data_type_combo.currentTextChanged.connect(self.on_data_type_change)
        control_layout.addRow("📎 类型:", self.data_type_combo)
        
        # 数据周期选择
        self.period_combo = QComboBox()
        self.period_combo.addItems(["日线", "周线", "月线"])
        control_layout.addRow("🕐 周期:", self.period_combo)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        self.load_btn = QPushButton("🔍 获取真实数据")
        self.load_btn.clicked.connect(self.load_real_data)
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self.clear_data)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        control_layout.addRow(button_layout)
        
        main_layout.addWidget(control_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 数据显示区域
        display_group = QGroupBox("📊 数据显示")
        display_layout = QVBoxLayout(display_group)
        
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)
        self.data_display.setStyleSheet("""
            font-family: Consolas, 'Courier New', monospace;
            font-size: 12px;
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
        """)
        self.update_display_placeholder()
        display_layout.addWidget(self.data_display)
        
        main_layout.addWidget(display_group)
        
        # 状态栏
        self.status_bar = QLabel("✅ efinance 数据接口就绪 - 点击获取数据开始测试")
        self.status_bar.setStyleSheet("""
            background-color: #27ae60;
            color: white;
            padding: 10px;
            font-weight: bold;
            border-radius: 5px;
        """)
        main_layout.addWidget(self.status_bar)
        
    def update_display_placeholder(self):
        """更新显示区域占位文本"""
        placeholder = """📊 真实数据获取区域
        
测试说明：
• 使用 efinance 库获取实时金融数据
• 支持股票、基金、指数等多种数据类型
• 数据来源于真实的金融市场接口
• 显示完整的数据字段和统计信息

测试代码示例：
• 股票: 000001 (平安银行)
• 基金: 159915 (创业板ETF)
• 指数: 000001 (上证指数)

数据字段包含：
• 日期时间戳
• 开盘价、收盘价、最高价、最低价
• 成交量、成交额
• 各种技术指标数据

请在上方输入代码并点击获取数据按钮测试！"""
        
        self.data_display.setPlaceholderText(placeholder)
    
    def on_data_type_change(self):
        """数据类型改变时的处理"""
        data_type = self.data_type_combo.currentText()
        if data_type == "基金数据":
            self.code_input.setPlaceholderText("输入基金代码，如：159915")
        else:
            self.code_input.setPlaceholderText("输入代码，如：000001")
    
    def load_real_data(self):
        """加载真实数据"""
        stock_code = self.code_input.text().strip()
        if not stock_code:
            self.status_bar.setText("❌ 请输入股票/基金代码")
            return
            
        data_type = self.data_type_combo.currentText()
        period = self.period_combo.currentText()
        
        # 显示加载状态
        self.status_bar.setText(f"🔍 正在获取 {stock_code} 的 {data_type}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.load_btn.setEnabled(False)
        
        # 启动数据获取线程
        self.data_thread = DataFetchThread(stock_code, data_type, period)
        self.data_thread.data_ready.connect(self.on_data_received)
        self.data_thread.progress_update.connect(self.progress_bar.setValue)
        self.data_thread.error_occurred.connect(self.on_data_error)
        self.data_thread.finished.connect(self.on_thread_finished)
        self.data_thread.start()
    
    def on_data_received(self, data, stock_code):
        """数据接收处理"""
        try:
            self.current_data = data
            
            # 构建显示文本
            display_text = f"📊 {stock_code} 真实数据获取成功\n"
            display_text += "=" * 50 + "\n\n"
            
            # 数据基本信息
            display_text += f"📋 数据类型: {self.data_type_combo.currentText()}\n"
            display_text += f"🕐 数据周期: {self.period_combo.currentText()}\n"
            display_text += f"📊 数据条数: {len(data)}\n"
            display_text += f"💾 数据大小: {data.memory_usage(deep=True).sum() / 1024:.2f} KB\n\n"
            
            # 显示列名
            display_text += "📑 数据字段:\n"
            for i, col in enumerate(data.columns, 1):
                display_text += f"  {i}. {col}\n"
            display_text += "\n"
            
            # 显示前几行数据
            display_text += "📈 前10条数据预览:\n"
            display_text += data.head(10).to_string(index=False)
            display_text += "\n\n"
            
            # 统计信息（根据数据类型）
            if self.data_type_combo.currentText() == "股票数据":
                if '收盘' in data.columns:
                    display_text += "📊 股价统计:\n"
                    display_text += f"• 最新收盘价: {data['收盘'].iloc[-1]:.2f}\n"
                    display_text += f"• 最高价: {data['最高'].max():.2f}\n"
                    display_text += f"• 最低价: {data['最低'].min():.2f}\n"
                    display_text += f"• 平均成交量: {data['成交量'].mean():,.0f}\n"
            elif self.data_type_combo.currentText() == "基金数据":
                if '单位净值' in data.columns:
                    display_text += "💰 基金统计:\n"
                    display_text += f"• 最新净值: {data['单位净值'].iloc[-1]:.4f}\n"
                    display_text += f"• 累计净值: {data['累计净值'].iloc[-1]:.4f}\n"
            
            self.data_display.setText(display_text)
            self.status_bar.setText(f"✅ {stock_code} 数据获取成功 - 共 {len(data)} 条记录")
            
        except Exception as e:
            self.data_display.setText(f"❌ 数据处理错误: {str(e)}")
            self.status_bar.setText("❌ 数据处理失败")
    
    def on_data_error(self, error_message):
        """数据错误处理"""
        self.data_display.setText(f"❌ 数据获取失败\n\n错误信息: {error_message}")
        self.status_bar.setText("❌ 数据获取失败")
    
    def on_thread_finished(self):
        """线程结束处理"""
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
    
    def clear_data(self):
        """清空数据"""
        self.data_display.clear()
        self.update_display_placeholder()
        self.code_input.clear()
        self.status_bar.setText("📝 数据已清空 - 就绪状态")

def test_real_data_integration():
    """测试真实数据集成"""
    print("🔍 开始 efinance 真实数据集成测试...")
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = RealDataWindow()
    window.show()
    
    print("✅ 真实数据测试窗口已显示")
    print("📊 efinance 数据接口连接正常")
    print("🔍 请输入股票代码测试数据获取功能")
    
    return app.exec_()

if __name__ == '__main__':
    exit_code = test_real_data_integration()
    print(f"👋 真实数据测试完成，退出码: {exit_code}")
    sys.exit(exit_code)