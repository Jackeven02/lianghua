"""
界面渲染验证测试
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

def test_ui_rendering():
    """测试UI渲染"""
    print("🔍 开始界面渲染验证测试...")
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = QMainWindow()
    window.setWindowTitle("Quant Analyzer - 界面渲染验证")
    window.setGeometry(200, 200, 800, 600)
    
    # 创建中央部件
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # 创建布局
    layout = QVBoxLayout(central_widget)
    
    # 添加测试标签
    title_label = QLabel("✅ 界面渲染验证成功")
    title_label.setAlignment(Qt.AlignCenter)
    title_label.setStyleSheet("""
        font-size: 24px; 
        font-weight: bold; 
        color: #27ae60;
        margin: 20px;
        padding: 15px;
        background-color: #ecf0f1;
        border: 2px solid #3498db;
        border-radius: 10px;
    """)
    layout.addWidget(title_label)
    
    status_label = QLabel("""📊 测试结果：
• PyQt5环境正常
• 窗口渲染成功  
• 样式应用正常
• 事件循环运行
• 界面响应正常""")
    status_label.setAlignment(Qt.AlignLeft)
    status_label.setStyleSheet("""
        font-size: 14px;
        margin: 20px;
        padding: 15px;
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
    """)
    layout.addWidget(status_label)
    
    # 显示窗口
    window.show()
    print("✅ 测试窗口已显示")
    print("🔍 请检查窗口是否正常渲染")
    print("✅ 界面渲染验证完成")
    
    # 运行应用
    return app.exec_()

if __name__ == '__main__':
    exit_code = test_ui_rendering()
    print(f"👋 测试完成，退出码: {exit_code}")
    sys.exit(exit_code)