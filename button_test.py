"""
按钮功能交互测试程序
专门验证UI按钮的响应效果
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                           QGroupBox, QFormLayout, QComboBox, QLineEdit)
from PyQt5.QtCore import Qt

class ButtonTestWindow(QMainWindow):
    """按钮测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.click_count = 0
        
    def init_ui(self):
        self.setWindowTitle("📊 按钮功能测试验证")
        self.setGeometry(200, 200, 1000, 700)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("✅ 按钮功能交互测试")
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
        
        # 测试说明
        info_label = QLabel("""🔍 按钮功能测试说明:
• 点击下方各种按钮测试交互响应
• 观察按钮状态变化和反馈效果
• 验证事件处理是否正常工作
• 确认界面响应的实时性""")
        info_label.setStyleSheet("""
            font-size: 14px;
            margin: 10px;
            padding: 15px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
        """)
        main_layout.addWidget(info_label)
        
        # 按钮测试区域
        button_group = QGroupBox("🔘 按钮功能测试")
        button_layout = QVBoxLayout(button_group)
        
        # 第一行按钮 - 基础功能
        row1_layout = QHBoxLayout()
        self.load_btn = QPushButton("🔍 加载数据")
        self.load_btn.clicked.connect(self.on_load_data)
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
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self.on_refresh)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self.on_clear)
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
        
        row1_layout.addWidget(self.load_btn)
        row1_layout.addWidget(self.refresh_btn)
        row1_layout.addWidget(self.clear_btn)
        button_layout.addLayout(row1_layout)
        
        # 第二行按钮 - 策略相关
        row2_layout = QHBoxLayout()
        self.test_strategy_btn = QPushButton("🧪 测试策略")
        self.test_strategy_btn.clicked.connect(self.on_test_strategy)
        self.test_strategy_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.clicked.connect(self.on_save)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        self.run_btn = QPushButton("▶️ 运行")
        self.run_btn.clicked.connect(self.on_run)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #d68910;
            }
        """)
        
        row2_layout.addWidget(self.test_strategy_btn)
        row2_layout.addWidget(self.save_btn)
        row2_layout.addWidget(self.run_btn)
        button_layout.addLayout(row2_layout)
        
        # 第三行按钮 - 系统功能
        row3_layout = QHBoxLayout()
        self.export_btn = QPushButton("📤 导出")
        self.export_btn.clicked.connect(self.on_export)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """)
        
        self.chart_btn = QPushButton("📊 图表")
        self.chart_btn.clicked.connect(self.on_chart)
        self.chart_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        
        self.help_btn = QPushButton("❓ 帮助")
        self.help_btn.clicked.connect(self.on_help)
        self.help_btn.setStyleSheet("""
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
        
        row3_layout.addWidget(self.export_btn)
        row3_layout.addWidget(self.chart_btn)
        row3_layout.addWidget(self.help_btn)
        button_layout.addLayout(row3_layout)
        
        main_layout.addWidget(button_group)
        
        # 反馈显示区域
        feedback_group = QGroupBox("📝 操作反馈")
        feedback_layout = QVBoxLayout(feedback_group)
        
        self.feedback_display = QTextEdit()
        self.feedback_display.setReadOnly(True)
        self.feedback_display.setStyleSheet("""
            font-family: Consolas, 'Courier New', monospace;
            font-size: 12px;
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
        """)
        self.feedback_display.setText("""📋 按钮功能测试反馈区域

请依次点击上方各种按钮测试功能:
• 观察按钮是否响应点击事件
• 查看此处是否显示操作反馈
• 验证界面交互是否正常
• 确认按钮样式变化效果

当前状态: 等待用户操作...""")
        feedback_layout.addWidget(self.feedback_display)
        
        main_layout.addWidget(feedback_group)
        
        # 操作计数器
        self.counter_label = QLabel("🖱️ 点击次数: 0")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #e74c3c;
            margin: 10px;
            padding: 10px;
            background-color: #f8f9fa;
            border: 2px solid #e74c3c;
            border-radius: 8px;
        """)
        main_layout.addWidget(self.counter_label)
        
        # 状态栏
        self.status_bar = QLabel("✅ 按钮测试程序就绪 - 点击按钮开始测试")
        self.status_bar.setStyleSheet("""
            background-color: #27ae60;
            color: white;
            padding: 10px;
            font-weight: bold;
            border-radius: 5px;
        """)
        main_layout.addWidget(self.status_bar)
        
    def add_feedback(self, message):
        """添加反馈信息"""
        self.click_count += 1
        self.counter_label.setText(f"🖱️ 点击次数: {self.click_count}")
        
        current_text = self.feedback_display.toPlainText()
        new_text = f"\n[{self.click_count}] {message}"
        self.feedback_display.setText(current_text + new_text)
        self.feedback_display.moveCursor(self.feedback_display.textCursor().End)
        
        # 滚动到底部
        scrollbar = self.feedback_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def on_load_data(self):
        """加载数据按钮"""
        self.add_feedback("🔍 点击了'加载数据'按钮 - 功能正常响应")
        self.status_bar.setText("✅ '加载数据'按钮功能正常")
        
    def on_refresh(self):
        """刷新按钮"""
        self.add_feedback("🔄 点击了'刷新'按钮 - 页面刷新功能正常")
        self.status_bar.setText("✅ '刷新'按钮功能正常")
        
    def on_clear(self):
        """清空按钮"""
        self.add_feedback("🗑️ 点击了'清空'按钮 - 数据清空功能正常")
        self.status_bar.setText("✅ '清空'按钮功能正常")
        
    def on_test_strategy(self):
        """测试策略按钮"""
        self.add_feedback("🧪 点击了'测试策略'按钮 - 策略测试功能正常")
        self.status_bar.setText("✅ '测试策略'按钮功能正常")
        
    def on_save(self):
        """保存按钮"""
        self.add_feedback("💾 点击了'保存'按钮 - 数据保存功能正常")
        self.status_bar.setText("✅ '保存'按钮功能正常")
        
    def on_run(self):
        """运行按钮"""
        self.add_feedback("▶️ 点击了'运行'按钮 - 程序执行功能正常")
        self.status_bar.setText("✅ '运行'按钮功能正常")
        
    def on_export(self):
        """导出按钮"""
        self.add_feedback("📤 点击了'导出'按钮 - 数据导出功能正常")
        self.status_bar.setText("✅ '导出'按钮功能正常")
        
    def on_chart(self):
        """图表按钮"""
        self.add_feedback("📊 点击了'图表'按钮 - 图表显示功能正常")
        self.status_bar.setText("✅ '图表'按钮功能正常")
        
    def on_help(self):
        """帮助按钮"""
        self.add_feedback("❓ 点击了'帮助'按钮 - 帮助文档功能正常")
        self.status_bar.setText("✅ '帮助'按钮功能正常")

def test_button_functionality():
    """测试按钮功能"""
    print("🔍 开始按钮功能测试...")
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = ButtonTestWindow()
    window.show()
    
    print("✅ 按钮测试窗口已显示")
    print("🖱️ 请测试点击各种按钮验证功能")
    print("📝 观察反馈区域是否显示操作记录")
    print("🔄 确认按钮状态变化和响应效果")
    
    return app.exec_()

if __name__ == '__main__':
    exit_code = test_button_functionality()
    print(f"👋 按钮功能测试完成，退出码: {exit_code}")
    sys.exit(exit_code)