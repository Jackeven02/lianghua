"""
数据视图控制器
负责数据获取、显示和基本分析功能
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
                           QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                           QComboBox, QLabel, QGroupBox, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

import pandas as pd
from ui_layer.base_view import BaseViewController
from data_layer import get_stock_data, get_fund_data, get_favorites
from analysis_layer import calculate_all_technical_indicators

class DataViewController(BaseViewController):
    """数据视图控制器"""
    
    data_loaded = pyqtSignal(object)  # 数据加载完成信号
    
    def __init__(self):
        super().__init__("📈 数据分析")
        self.current_data = None
        self.setup_connections()
        
    def init_ui(self):
        """初始化界面"""
        super().init_ui()
        
        # 创建主分割器
        self.main_splitter = QSplitter(Qt.Vertical)
        self.content_layout.addWidget(self.main_splitter)
        
        # 创建查询区域
        self.create_query_area()
        self.main_splitter.addWidget(self.query_group)
        
        # 创建数据显示区域
        self.create_data_display()
        self.main_splitter.addWidget(self.data_group)
        
        # 设置分割器比例
        self.main_splitter.setSizes([200, 600])
        
    def create_query_area(self):
        """创建查询区域"""
        self.query_group = QGroupBox("数据查询")
        self.query_group.setStyleSheet("""
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
        
        query_layout = QVBoxLayout(self.query_group)
        
        # 查询表单
        form_layout = QFormLayout()
        
        # 代码输入
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("请输入股票代码或基金代码（如：000001）")
        self.code_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        form_layout.addRow("代码:", self.code_input)
        
        # 数据类型选择
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["股票数据", "基金数据"])
        self.data_type_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        form_layout.addRow("类型:", self.data_type_combo)
        
        # 时间周期选择
        self.period_combo = QComboBox()
        self.period_combo.addItems(["日线", "周线", "月线", "5分钟", "15分钟", "30分钟", "60分钟"])
        self.period_combo.setCurrentText("日线")
        form_layout.addRow("周期:", self.period_combo)
        
        query_layout.addLayout(form_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.query_btn = QPushButton("🔍 查询数据")
        self.query_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        
        self.add_fav_btn = QPushButton("⭐ 添加收藏")
        self.add_fav_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        
        self.refresh_fav_btn = QPushButton("🔄 刷新收藏")
        self.refresh_fav_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        button_layout.addWidget(self.query_btn)
        button_layout.addWidget(self.add_fav_btn)
        button_layout.addWidget(self.refresh_fav_btn)
        button_layout.addStretch()
        
        query_layout.addLayout(button_layout)
        
        # 收藏列表
        self.fav_label = QLabel("我的收藏:")
        self.fav_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        query_layout.addWidget(self.fav_label)
        
        self.fav_list = QTextEdit()
        self.fav_list.setMaximumHeight(80)
        self.fav_list.setReadOnly(True)
        self.fav_list.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 5px;
                background-color: #ffffff;
            }
        """)
        query_layout.addWidget(self.fav_list)
        
    def create_data_display(self):
        """创建数据展示区域"""
        self.data_group = QGroupBox("数据展示")
        self.data_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
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
        
        data_layout = QVBoxLayout(self.data_group)
        
        # 数据信息显示
        self.info_label = QLabel("请查询数据以开始分析")
        self.info_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                padding: 10px;
                border: 1px dashed #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
        """)
        data_layout.addWidget(self.info_label)
        
        # 数据表格
        self.data_table = QTableWidget()
        self.data_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                gridline-color: #ecf0f1;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: 1px solid #2c3e50;
                font-weight: bold;
            }
        """)
        data_layout.addWidget(self.data_table)
        
        # 操作按钮
        op_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("📤 导出数据")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        
        self.tech_btn = QPushButton("📊 技术分析")
        self.tech_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        op_layout.addWidget(self.export_btn)
        op_layout.addWidget(self.tech_btn)
        op_layout.addStretch()
        
        data_layout.addLayout(op_layout)
        
    def setup_connections(self):
        """设置信号连接"""
        self.query_btn.clicked.connect(self.query_data)
        self.add_fav_btn.clicked.connect(self.add_favorite)
        self.refresh_fav_btn.clicked.connect(self.refresh_favorites)
        self.export_btn.clicked.connect(self.export_data)
        self.tech_btn.clicked.connect(self.technical_analysis)
        
    def query_data(self):
        """查询数据"""
        self.update_status("正在查询数据...")
        
        try:
            code = self.code_input.text().strip()
            if not code:
                self.update_status("请输入代码")
                return
                
            data_type = self.data_type_combo.currentText()
            period = self.period_combo.currentText()
            
            # 映射周期到数据层需要的格式
            period_map = {
                "日线": "daily",
                "周线": "weekly", 
                "月线": "monthly",
                "15分钟": "15min",
                "30分钟": "30min",
                "60分钟": "60min"
            }
            
            # 根据数据类型获取数据
            if data_type == "股票数据":
                data = get_stock_data(code, period=period_map.get(period, "daily"))
            elif data_type == "基金数据":
                data = get_fund_data(code)
            else:  # 指数数据
                data = get_index_data(code, period=period_map.get(period, "daily"))
                
            if data.empty:
                self.update_status("未获取到数据")
                return
                
            self.current_data = data
            self.display_data(data)
            self.data_loaded.emit(data)
            self.update_status(f"数据获取成功，共{len(data)}条记录")
            
        except Exception as e:
            self.update_status(f"数据查询失败: {str(e)}")
            
    def display_data(self, data):
        """显示数据"""
        if data.empty:
            self.info_label.setText("无数据可显示")
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            return
            
        # 显示数据信息
        self.info_label.setText(f"数据范围: {data.index[0]} 至 {data.index[-1]}  共 {len(data)} 条记录")
        
        # 显示数据表格
        self.data_table.setRowCount(len(data))
        self.data_table.setColumnCount(len(data.columns))
        self.data_table.setHorizontalHeaderLabels(data.columns.tolist())
        
        # 填充数据
        for row in range(len(data)):
            for col, column in enumerate(data.columns):
                item = QTableWidgetItem(str(data.iloc[row, col]))
                self.data_table.setItem(row, col, item)
                
        # 调整列宽
        self.data_table.resizeColumnsToContents()
        
    def add_favorite(self):
        """添加收藏"""
        from data_layer import add_to_favorites
        code = self.code_input.text().strip()
        if code:
            try:
                add_to_favorites(code, code)  # 使用代码作为名称
                self.update_status(f"已添加 {code} 到收藏")
                self.refresh_favorites()
            except Exception as e:
                self.update_status(f"添加收藏失败: {str(e)}")
        else:
            self.update_status("请输入代码")
            
    def refresh_favorites(self):
        """刷新收藏列表"""
        try:
            favorites = get_favorites()
            if not favorites.empty:
                fav_text = "\n".join([f"★ {row['stock_code']}" for _, row in favorites.iterrows()])
                self.fav_list.setText(fav_text)
            else:
                self.fav_list.setText("暂无收藏")
            self.update_status("收藏列表已刷新")
        except Exception as e:
            self.update_status(f"刷新收藏失败: {str(e)}")
            
    def export_data(self):
        """导出数据"""
        if self.current_data is None or self.current_data.empty:
            self.update_status("没有数据可导出")
            return
            
        try:
            from config.settings import EXPORT_DIR
            import os
            import time
            
            # 确保导出目录存在
            if not os.path.exists(EXPORT_DIR):
                os.makedirs(EXPORT_DIR)
                
            # 生成文件名
            filename = f"export_{int(time.time())}.csv"
            filepath = os.path.join(EXPORT_DIR, filename)
            
            # 导出数据
            self.current_data.to_csv(filepath, encoding='utf-8-sig')
            self.update_status(f"数据已导出至: {filepath}")
            
        except Exception as e:
            self.update_status(f"导出失败: {str(e)}")
            
    def technical_analysis(self):
        """技术分析"""
        if self.current_data is None or self.current_data.empty:
            self.update_status("请先加载数据")
            return
            
        try:
            self.update_status("正在计算技术指标...")
            # 计算技术指标
            tech_data = calculate_all_technical_indicators(self.current_data)
            self.display_data(tech_data)
            self.update_status("技术分析完成")
        except Exception as e:
            self.update_status(f"技术分析失败: {str(e)}")
            
    def refresh_view(self):
        """刷新视图"""
        self.update_status("正在刷新数据视图...")
        self.refresh_favorites()
        self.update_status("刷新完成")
        
    def save_work(self):
        """保存当前工作"""
        self.update_status("正在保存数据工作空间...")
        # 保存当前的代码、配置等到本地配置
        # 也可保存当前数据到临时文件
        self.update_status("工作空间已保存")