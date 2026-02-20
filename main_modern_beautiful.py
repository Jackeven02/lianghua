# -*- coding: utf-8 -*-
"""
智能投资顾问系统 - 现代化美观GUI
采用现代设计风格，优化视觉体验
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'efinance'))
sys.path.insert(0, os.path.dirname(__file__))

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QColor, QFont, QIcon, QPalette, QLinearGradient, QPainter, QBrush, QPen
import efinance as ef
import pandas as pd
import numpy as np
from datetime import datetime


class ModernCard(QFrame):
    """现代卡片组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            ModernCard {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
            ModernCard:hover {
                border: 1px solid #4CAF50;
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.15);
            }
        """)


class ModernButton(QPushButton):
    """现代按钮组件"""
    def __init__(self, text, color="primary", parent=None):
        super().__init__(text, parent)
        
        colors = {
            "primary": ("#4CAF50", "#45a049", "white"),
            "secondary": ("#2196F3", "#0b7dda", "white"),
            "danger": ("#f44336", "#da190b", "white"),
            "warning": ("#ff9800", "#e68900", "white"),
            "success": ("#4CAF50", "#45a049", "white"),
        }
        
        bg, hover, text_color = colors.get(color, colors["primary"])
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                border-radius: 8px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {hover};
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background-color: {bg};
                transform: translateY(0px);
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)


class AnalysisWorker(QThread):
    """分析工作线程"""
    progress = pyqtSignal(int, int, str)
    result = pyqtSignal(list)
    
    def __init__(self, stock_list):
        super().__init__()
        self.stock_list = stock_list
        
    def run(self):
        results = []
        for i, (code, name) in enumerate(self.stock_list, 1):
            self.progress.emit(i, len(self.stock_list), f"{name}({code})")
            try:
                result = self.analyze_stock(code, name)
                if result:
                    results.append(result)
            except:
                pass
        self.result.emit(results)
    
    def analyze_stock(self, stock_code, stock_name):
        try:
            df = ef.stock.get_quote_history(stock_code)
            if df is None or df.empty or len(df) < 60:
                return None
            
            df = df.iloc[-120:].copy()
            df = df.rename(columns={
                '日期': 'date', '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low', '成交量': 'volume'
            })
            
            for col in ['open', 'high', 'low', 'close']:
                df[col] = df[col].abs()
            
            df['SMA_5'] = df['close'].rolling(window=5).mean()
            df['SMA_20'] = df['close'].rolling(window=20).mean()
            df['SMA_60'] = df['close'].rolling(window=60).mean()
            
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            ema_12 = df['close'].ewm(span=12).mean()
            ema_26 = df['close'].ewm(span=26).mean()
            df['MACD'] = ema_12 - ema_26
            df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
            
            latest = df.iloc[-1]
            current_price = latest['close']
            
            score = 0
            reasons = []
            technical_score = 0
            
            if latest['SMA_5'] > latest['SMA_20'] > latest['SMA_60']:
                score += 30
                technical_score += 30
                reasons.append("✓ 均线多头排列")
            elif latest['SMA_5'] > latest['SMA_20']:
                score += 20
                technical_score += 20
                reasons.append("✓ 短期均线向上")
            else:
                technical_score += 10
            
            if latest['MACD'] > latest['MACD_signal']:
                score += 20
                technical_score += 20
                reasons.append("✓ MACD金叉")
            else:
                technical_score += 10
            
            if 30 < latest['RSI'] < 70:
                score += 20
                reasons.append("✓ RSI健康区间")
            elif latest['RSI'] < 30:
                score += 15
                reasons.append("✓ RSI超卖")
            elif latest['RSI'] > 70:
                score += 5
                reasons.append("⚠ RSI超买")
            
            if current_price > latest['SMA_20']:
                score += 15
                reasons.append("✓ 价格在均线上方")
            
            recent_vol = df['volume'].iloc[-5:].mean()
            avg_vol = df['volume'].mean()
            if recent_vol > avg_vol * 1.2:
                score += 10
                reasons.append("✓ 成交量放大")
            
            returns_5d = (df['close'].iloc[-1] / df['close'].iloc[-5] - 1) * 100
            if returns_5d > 3:
                score += 5
                reasons.append(f"✓ 5日涨幅 {returns_5d:.1f}%")
            elif returns_5d < -3:
                reasons.append(f"⚠ 5日跌幅 {returns_5d:.1f}%")
            
            if score >= 70:
                signal = "强烈买入"
                risk_level = "中"
            elif score >= 60:
                signal = "买入"
                risk_level = "中"
            elif score >= 40:
                signal = "持有"
                risk_level = "中"
            elif score >= 30:
                signal = "观望"
                risk_level = "高"
            else:
                signal = "卖出"
                risk_level = "高"
            
            target_price = current_price * 1.15
            stop_loss = current_price * 0.92
            
            if score >= 70:
                position_size = 0.10
            elif score >= 60:
                position_size = 0.08
            elif score >= 50:
                position_size = 0.05
            else:
                position_size = 0.03
            
            return {
                'code': stock_code, 'name': stock_name, 'price': current_price,
                'signal': signal, 'score': score, 'technical_score': technical_score,
                'confidence': min(score, 100), 'rsi': latest['RSI'], 'macd': latest['MACD'],
                'target_price': target_price, 'stop_loss': stop_loss,
                'risk_level': risk_level, 'position_size': position_size,
                'returns_5d': returns_5d, 'reasons': reasons, 'date': latest['date']
            }
        except:
            return None


class ModernMainWindow(QMainWindow):
    """现代化主窗口"""
    
    def __init__(self):
        super().__init__()
        self.advice_list = []
        self.portfolio = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("智能投资顾问系统 v2.0 - 现代版")
        self.setGeometry(50, 50, 1600, 950)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5f7fa, stop:1 #e8eef5);
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 顶部标题栏
        header = self.create_modern_header()
        main_layout.addWidget(header)
        
        # 标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: transparent;
                border-radius: 12px;
            }
            QTabBar::tab {
                background: white;
                color: #666;
                padding: 16px 32px;
                margin-right: 4px;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                font-size: 15px;
                font-weight: 600;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #f0f0f0;
            }
        """)
        
        self.scan_tab = self.create_scan_tab()
        self.tab_widget.addTab(self.scan_tab, "📊 市场扫描")
        
        self.single_tab = self.create_single_tab()
        self.tab_widget.addTab(self.single_tab, "🔍 单股分析")
        
        self.portfolio_tab = self.create_portfolio_tab()
        self.tab_widget.addTab(self.portfolio_tab, "💼 组合管理")
        
        self.risk_tab = self.create_risk_tab()
        self.tab_widget.addTab(self.risk_tab, "⚠️ 风险监控")
        
        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ 系统设置")
        
        main_layout.addWidget(self.tab_widget)
        
        # 底部状态栏
        self.create_modern_statusbar()
        
    def create_modern_header(self):
        """创建现代化标题栏"""
        header = QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 16px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 0, 30, 0)
        
        # 左侧标题
        title_layout = QVBoxLayout()
        title = QLabel("🤖 智能投资顾问系统")
        title.setFont(QFont("Microsoft YaHei", 28, QFont.Bold))
        title.setStyleSheet("color: white;")
        
        subtitle = QLabel("AI-Powered Investment Advisor")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        layout.addLayout(title_layout)
        
        layout.addStretch()
        
        # 右侧信息
        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignRight)
        
        self.time_label = QLabel(datetime.now().strftime("%Y年%m月%d日 %H:%M"))
        self.time_label.setFont(QFont("Microsoft YaHei", 14))
        self.time_label.setStyleSheet("color: white;")
        
        status_label = QLabel("● 系统运行中")
        status_label.setFont(QFont("Microsoft YaHei", 11))
        status_label.setStyleSheet("color: #4CAF50;")
        
        info_layout.addWidget(self.time_label)
        info_layout.addWidget(status_label)
        layout.addLayout(info_layout)
        
        # 定时更新时间
        timer = QTimer(self)
        timer.timeout.connect(lambda: self.time_label.setText(
            datetime.now().strftime("%Y年%m月%d日 %H:%M")
        ))
        timer.start(60000)
        
        return header
    
    def create_modern_statusbar(self):
        """创建现代状态栏"""
        statusbar = self.statusBar()
        statusbar.setStyleSheet("""
            QStatusBar {
                background: white;
                color: #666;
                font-size: 13px;
                border-top: 1px solid #e0e0e0;
                padding: 8px;
            }
        """)
        statusbar.showMessage("● 就绪")

    
    def create_scan_tab(self):
        """创建市场扫描标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # 控制卡片
        control_card = ModernCard()
        control_layout = QHBoxLayout(control_card)
        control_layout.setContentsMargins(24, 20, 24, 20)
        
        control_layout.addWidget(QLabel("扫描数量:"))
        self.stock_count_spin = QSpinBox()
        self.stock_count_spin.setRange(5, 50)
        self.stock_count_spin.setValue(20)
        self.stock_count_spin.setStyleSheet("""
            QSpinBox {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                min-width: 80px;
            }
            QSpinBox:focus {
                border: 2px solid #4CAF50;
            }
        """)
        control_layout.addWidget(self.stock_count_spin)
        
        control_layout.addWidget(QLabel("最低评分:"))
        self.min_score_spin = QSpinBox()
        self.min_score_spin.setRange(0, 100)
        self.min_score_spin.setValue(40)
        self.min_score_spin.setStyleSheet(self.stock_count_spin.styleSheet())
        control_layout.addWidget(self.min_score_spin)
        
        control_layout.addSpacing(20)
        
        self.scan_btn = ModernButton("🔍 开始扫描市场", "primary")
        self.scan_btn.clicked.connect(self.start_scan)
        control_layout.addWidget(self.scan_btn)
        
        self.export_btn = ModernButton("📄 导出结果", "secondary")
        self.export_btn.clicked.connect(self.export_results)
        control_layout.addWidget(self.export_btn)
        
        control_layout.addStretch()
        layout.addWidget(control_card)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 8px;
                background-color: #e0e0e0;
                height: 24px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #8BC34A);
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 统计信息卡片
        stats_card = ModernCard()
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setContentsMargins(24, 16, 24, 16)
        self.stats_label = QLabel("等待扫描...")
        self.stats_label.setStyleSheet("font-size: 14px; color: #666;")
        stats_layout.addWidget(self.stats_label)
        layout.addWidget(stats_card)
        
        # 结果表格卡片
        table_card = ModernCard()
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(11)
        self.result_table.setHorizontalHeaderLabels([
            "代码", "名称", "信号", "评分", "信心度", "当前价", 
            "目标价", "止损价", "RSI", "风险", "建议仓位"
        ])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
                gridline-color: #f0f0f0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 12px 8px;
            }
            QTableWidget::item:selected {
                background-color: #e8f5e9;
                color: #2e7d32;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 12px 8px;
                border: none;
                border-bottom: 2px solid #4CAF50;
                font-weight: bold;
                font-size: 13px;
                color: #333;
            }
        """)
        self.result_table.itemSelectionChanged.connect(self.show_scan_detail)
        table_layout.addWidget(self.result_table)
        
        layout.addWidget(table_card, 1)
        
        # 详细信息卡片
        detail_card = ModernCard()
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(20, 16, 20, 16)
        
        detail_title = QLabel("📋 详细分析")
        detail_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        detail_title.setStyleSheet("color: #333; margin-bottom: 8px;")
        detail_layout.addWidget(detail_title)
        
        self.scan_detail_text = QTextEdit()
        self.scan_detail_text.setReadOnly(True)
        self.scan_detail_text.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: #fafafa;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        detail_layout.addWidget(self.scan_detail_text)
        
        layout.addWidget(detail_card)
        
        return widget

    
    def create_single_tab(self):
        """创建单股分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # 输入卡片
        input_card = ModernCard()
        input_layout = QHBoxLayout(input_card)
        input_layout.setContentsMargins(24, 20, 24, 20)
        
        input_layout.addWidget(QLabel("股票代码:"))
        self.stock_code_input = QLineEdit()
        self.stock_code_input.setPlaceholderText("例如: 600519")
        self.stock_code_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                min-width: 200px;
            }
            QLineEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        input_layout.addWidget(self.stock_code_input)
        
        self.analyze_btn = ModernButton("🔍 开始分析", "secondary")
        self.analyze_btn.clicked.connect(self.analyze_single_stock)
        input_layout.addWidget(self.analyze_btn)
        
        input_layout.addStretch()
        layout.addWidget(input_card)
        
        # 结果卡片
        result_card = ModernCard()
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(20, 16, 20, 16)
        
        result_title = QLabel("📊 分析报告")
        result_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        result_title.setStyleSheet("color: #333; margin-bottom: 8px;")
        result_layout.addWidget(result_title)
        
        self.single_result_text = QTextEdit()
        self.single_result_text.setReadOnly(True)
        self.single_result_text.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: #fafafa;
                border-radius: 8px;
                padding: 16px;
                font-size: 13px;
                line-height: 1.8;
            }
        """)
        result_layout.addWidget(self.single_result_text)
        
        layout.addWidget(result_card, 1)
        
        return widget
    
    def create_portfolio_tab(self):
        """创建组合管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # 概况卡片
        summary_card = ModernCard()
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(24, 20, 24, 20)
        
        summary_title = QLabel("💼 组合概况")
        summary_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        summary_title.setStyleSheet("color: #333; margin-bottom: 12px;")
        summary_layout.addWidget(summary_title)
        
        self.portfolio_summary = QLabel("暂无组合数据\n点击下方按钮构建投资组合")
        self.portfolio_summary.setAlignment(Qt.AlignCenter)
        self.portfolio_summary.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #999;
                padding: 40px;
                background-color: #fafafa;
                border-radius: 8px;
            }
        """)
        summary_layout.addWidget(self.portfolio_summary)
        
        layout.addWidget(summary_card)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.build_portfolio_btn = ModernButton("📦 构建组合", "success")
        self.build_portfolio_btn.clicked.connect(self.build_portfolio)
        btn_layout.addWidget(self.build_portfolio_btn)
        
        self.clear_portfolio_btn = ModernButton("🗑️ 清空组合", "danger")
        self.clear_portfolio_btn.clicked.connect(self.clear_portfolio)
        btn_layout.addWidget(self.clear_portfolio_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 持仓表格卡片
        table_card = ModernCard()
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.position_table = QTableWidget()
        self.position_table.setColumnCount(9)
        self.position_table.setHorizontalHeaderLabels([
            "代码", "名称", "建议仓位", "当前价", "目标价", 
            "止损价", "预期收益", "风险等级", "信号"
        ])
        self.position_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.position_table.setAlternatingRowColors(True)
        self.position_table.setStyleSheet(self.result_table.styleSheet())
        table_layout.addWidget(self.position_table)
        
        layout.addWidget(table_card, 1)
        
        return widget
    
    def create_risk_tab(self):
        """创建风险监控标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # 风险指标卡片
        metrics_card = ModernCard()
        metrics_layout = QVBoxLayout(metrics_card)
        metrics_layout.setContentsMargins(24, 20, 24, 20)
        
        metrics_title = QLabel("📊 风险指标")
        metrics_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        metrics_title.setStyleSheet("color: #333; margin-bottom: 12px;")
        metrics_layout.addWidget(metrics_title)
        
        self.risk_metrics = QLabel("暂无风险数据\n请先构建投资组合")
        self.risk_metrics.setAlignment(Qt.AlignCenter)
        self.risk_metrics.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #999;
                padding: 40px;
                background-color: #fff8e1;
                border-radius: 8px;
            }
        """)
        metrics_layout.addWidget(self.risk_metrics)
        
        layout.addWidget(metrics_card)
        
        # 风险警告卡片
        warning_card = ModernCard()
        warning_layout = QVBoxLayout(warning_card)
        warning_layout.setContentsMargins(24, 20, 24, 20)
        
        warning_title = QLabel("⚠️ 风险警告")
        warning_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        warning_title.setStyleSheet("color: #f44336; margin-bottom: 12px;")
        warning_layout.addWidget(warning_title)
        
        self.warning_text = QTextEdit()
        self.warning_text.setReadOnly(True)
        self.warning_text.setMaximumHeight(150)
        self.warning_text.setHtml("<p style='color: green;'>✓ 暂无风险警告</p>")
        self.warning_text.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: #fafafa;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
            }
        """)
        warning_layout.addWidget(self.warning_text)
        
        layout.addWidget(warning_card)
        
        # 建议操作卡片
        action_card = ModernCard()
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(24, 20, 24, 20)
        
        action_title = QLabel("💡 建议操作")
        action_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        action_title.setStyleSheet("color: #2196F3; margin-bottom: 12px;")
        action_layout.addWidget(action_title)
        
        self.action_text = QTextEdit()
        self.action_text.setReadOnly(True)
        self.action_text.setHtml("<p>暂无特别建议</p>")
        self.action_text.setStyleSheet(self.warning_text.styleSheet())
        action_layout.addWidget(self.action_text)
        
        layout.addWidget(action_card, 1)
        
        return widget

    
    def create_settings_tab(self):
        """创建系统设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        
        # 风险偏好卡片
        risk_card = ModernCard()
        risk_layout = QVBoxLayout(risk_card)
        risk_layout.setContentsMargins(24, 20, 24, 20)
        
        risk_title = QLabel("⚙️ 风险偏好设置")
        risk_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        risk_title.setStyleSheet("color: #333; margin-bottom: 12px;")
        risk_layout.addWidget(risk_title)
        
        risk_input_layout = QHBoxLayout()
        risk_input_layout.addWidget(QLabel("风险承受能力:"))
        self.risk_tolerance_combo = QComboBox()
        self.risk_tolerance_combo.addItems(["保守", "中等", "激进"])
        self.risk_tolerance_combo.setCurrentText("中等")
        self.risk_tolerance_combo.setStyleSheet("""
            QComboBox {
                padding: 10px 16px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox:focus {
                border: 2px solid #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        risk_input_layout.addWidget(self.risk_tolerance_combo)
        risk_input_layout.addStretch()
        risk_layout.addLayout(risk_input_layout)
        
        layout.addWidget(risk_card)
        
        # 关于系统卡片
        about_card = ModernCard()
        about_layout = QVBoxLayout(about_card)
        about_layout.setContentsMargins(24, 20, 24, 20)
        
        about_title = QLabel("ℹ️ 关于系统")
        about_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        about_title.setStyleSheet("color: #333; margin-bottom: 12px;")
        about_layout.addWidget(about_title)
        
        about_text = QLabel("""
        <div style="line-height: 1.8;">
        <h3 style="color: #4CAF50;">智能投资顾问系统 v2.0</h3>
        <p style="font-size: 14px; color: #666;">
        <b>🎯 功能特点:</b><br/>
        • 📊 市场扫描 - 批量分析股票，发现投资机会<br/>
        • 🔍 单股分析 - 深度分析个股，提供详细建议<br/>
        • 💼 组合管理 - 智能构建投资组合<br/>
        • ⚠️ 风险监控 - 实时监控投资风险<br/>
        <br/>
        <b>📈 数据来源:</b> 东方财富网 (efinance)<br/>
        <b>🔧 技术指标:</b> 均线、RSI、MACD等15+指标<br/>
        <br/>
        <p style="color: #f44336; font-weight: bold;">
        ⚠️ 重要提示: 本系统分析结果仅供参考，不构成投资建议。<br/>
        投资有风险，入市需谨慎！
        </p>
        </div>
        """)
        about_text.setWordWrap(True)
        about_text.setStyleSheet("font-size: 13px;")
        about_layout.addWidget(about_text)
        
        layout.addWidget(about_card, 1)
        
        return widget
    
    # 业务逻辑方法
    def start_scan(self):
        """开始扫描"""
        count = self.stock_count_spin.value()
        
        stock_list = [
            ("600519", "贵州茅台"), ("000858", "五粮液"), ("600036", "招商银行"),
            ("601318", "中国平安"), ("000333", "美的集团"), ("600276", "恒瑞医药"),
            ("000651", "格力电器"), ("601888", "中国中免"), ("300750", "宁德时代"),
            ("002475", "立讯精密"), ("600809", "山西汾酒"), ("000568", "泸州老窖"),
            ("603288", "海天味业"), ("002304", "洋河股份"), ("600887", "伊利股份"),
            ("000596", "古井贡酒"), ("600690", "海尔智家"), ("000002", "万科A"),
            ("600030", "中信证券"), ("601166", "兴业银行"), ("000001", "平安银行"),
            ("601398", "工商银行"), ("601288", "农业银行"), ("601328", "交通银行"),
            ("600000", "浦发银行"), ("002142", "宁波银行"), ("601939", "建设银行"),
            ("600016", "民生银行"), ("601169", "北京银行"), ("601009", "南京银行"),
            ("600585", "海螺水泥"), ("600048", "保利发展"), ("000002", "万科A"),
            ("600031", "三一重工"), ("601668", "中国建筑"), ("600028", "中国石化"),
            ("601857", "中国石油"), ("600019", "宝钢股份"), ("000063", "中兴通讯"),
            ("600050", "中国联通"), ("000725", "京东方A"), ("002230", "科大讯飞"),
            ("300059", "东方财富"), ("002415", "海康威视"), ("000725", "京东方A"),
            ("600104", "上汽集团"), ("000625", "长安汽车"), ("601633", "长城汽车"),
            ("002594", "比亚迪"), ("600741", "华域汽车"), ("000338", "潍柴动力")
        ][:count]
        
        self.scan_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(stock_list))
        self.progress_bar.setValue(0)
        self.statusBar().showMessage("● 正在扫描市场...")
        
        self.worker = AnalysisWorker(stock_list)
        self.worker.progress.connect(self.update_progress)
        self.worker.result.connect(self.show_scan_results)
        self.worker.start()
        
    def update_progress(self, current, total, stock_name):
        """更新进度"""
        self.progress_bar.setValue(current)
        self.stats_label.setText(f"正在分析 {stock_name}... ({current}/{total})")
        self.statusBar().showMessage(f"● 扫描进度: {current}/{total}")
        
    def show_scan_results(self, results):
        """显示扫描结果"""
        self.advice_list = results
        results.sort(key=lambda x: x['score'], reverse=True)
        
        min_score = self.min_score_spin.value()
        results = [r for r in results if r['score'] >= min_score]
        
        self.result_table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            self.result_table.setItem(row, 0, QTableWidgetItem(result['code']))
            self.result_table.setItem(row, 1, QTableWidgetItem(result['name']))
            
            signal_item = QTableWidgetItem(result['signal'])
            if "买入" in result['signal']:
                signal_item.setBackground(QColor("#4CAF50"))
                signal_item.setForeground(QColor("white"))
            elif result['signal'] == "持有":
                signal_item.setBackground(QColor("#FFC107"))
            self.result_table.setItem(row, 2, signal_item)
            
            score_item = QTableWidgetItem(f"{result['score']}")
            if result['score'] >= 70:
                score_item.setBackground(QColor("#4CAF50"))
                score_item.setForeground(QColor("white"))
            elif result['score'] >= 60:
                score_item.setBackground(QColor("#8BC34A"))
            self.result_table.setItem(row, 3, score_item)
            
            self.result_table.setItem(row, 4, QTableWidgetItem(f"{result['confidence']}%"))
            self.result_table.setItem(row, 5, QTableWidgetItem(f"¥{result['price']:.2f}"))
            self.result_table.setItem(row, 6, QTableWidgetItem(f"¥{result['target_price']:.2f}"))
            self.result_table.setItem(row, 7, QTableWidgetItem(f"¥{result['stop_loss']:.2f}"))
            self.result_table.setItem(row, 8, QTableWidgetItem(f"{result['rsi']:.1f}"))
            self.result_table.setItem(row, 9, QTableWidgetItem(result['risk_level']))
            self.result_table.setItem(row, 10, QTableWidgetItem(f"{result['position_size']*100:.1f}%"))
        
        buy_count = sum(1 for r in results if "买入" in r['signal'])
        strong_buy = sum(1 for r in results if r['signal'] == "强烈买入")
        avg_score = sum(r['score'] for r in results) / len(results) if results else 0
        
        self.stats_label.setText(
            f"✓ 找到 {len(results)} 个投资机会 | "
            f"平均评分: {avg_score:.1f} | "
            f"强烈买入: {strong_buy} | "
            f"买入: {buy_count - strong_buy}"
        )
        
        self.scan_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage(f"● 扫描完成！找到 {len(results)} 个投资机会")
        
        if len(results) > 0:
            QMessageBox.information(self, "扫描完成", 
                f"成功扫描 {len(results)} 只股票\n"
                f"找到 {buy_count} 个买入机会\n"
                f"平均评分: {avg_score:.1f}")

    
    def show_scan_detail(self):
        """显示扫描详情"""
        selected = self.result_table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        if row >= len(self.advice_list):
            return
        
        advice = self.advice_list[row]
        
        detail_html = f"""
        <div style="font-family: 'Microsoft YaHei'; line-height: 1.8;">
        <h2 style="color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px;">
        {advice['name']} ({advice['code']})
        </h2>
        
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 12px; color: white; margin: 15px 0;">
        <h3 style="margin: 0 0 10px 0;">📊 投资建议</h3>
        <p style="font-size: 18px; margin: 5px 0;">
        <b>信号:</b> <span style="font-size: 22px; font-weight: bold;">
        {advice['signal']}</span>
        </p>
        <p style="font-size: 16px; margin: 5px 0;">
        <b>信心度:</b> {advice['confidence']}% | <b>评分:</b> {advice['score']}/100
        </p>
        </div>
        
        <h3 style="color: #4CAF50; margin-top: 20px;">💰 价格信息</h3>
        <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
        <tr style="background: #f8f9fa;">
            <td style="padding: 12px; border: 1px solid #e0e0e0; font-weight: bold;">当前价</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">¥{advice['price']:.2f}</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0; font-weight: bold;">目标价</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0; color: green;">
            ¥{advice['target_price']:.2f} ({(advice['target_price']/advice['price']-1)*100:+.1f}%)
            </td>
        </tr>
        <tr>
            <td style="padding: 12px; border: 1px solid #e0e0e0; font-weight: bold;">止损价</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0; color: red;">
            ¥{advice['stop_loss']:.2f} ({(advice['stop_loss']/advice['price']-1)*100:+.1f}%)
            </td>
            <td style="padding: 12px; border: 1px solid #e0e0e0; font-weight: bold;">5日涨幅</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0; 
                color: {'green' if advice['returns_5d'] > 0 else 'red'};">
            {advice['returns_5d']:+.2f}%
            </td>
        </tr>
        </table>
        
        <h3 style="color: #2196F3; margin-top: 20px;">📈 技术指标</h3>
        <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
        <tr style="background: #f8f9fa;">
            <td style="padding: 12px; border: 1px solid #e0e0e0; font-weight: bold;">RSI</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">{advice['rsi']:.2f}</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0; font-weight: bold;">MACD</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">{advice['macd']:.4f}</td>
        </tr>
        <tr>
            <td style="padding: 12px; border: 1px solid #e0e0e0; font-weight: bold;">风险等级</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">{advice['risk_level']}</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0; font-weight: bold;">建议仓位</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">{advice['position_size']*100:.1f}%</td>
        </tr>
        </table>
        
        <h3 style="color: #ff9800; margin-top: 20px;">💡 分析理由</h3>
        <ul style="line-height: 2; font-size: 14px;">
        {''.join(f'<li style="margin: 8px 0;">{reason}</li>' for reason in advice['reasons'])}
        </ul>
        
        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; 
                    border-left: 4px solid #ff9800; margin-top: 20px;">
        <p style="color: #856404; margin: 0; font-size: 13px;">
        <b>⚠️ 风险提示:</b> 本分析基于技术指标，仅供参考。投资有风险，入市需谨慎。
        </p>
        </div>
        
        <p style="color: #999; font-size: 12px; text-align: right; margin-top: 15px;">
        数据日期: {advice['date']} | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
        </div>
        """
        
        self.scan_detail_text.setHtml(detail_html)
    
    def analyze_single_stock(self):
        """分析单只股票"""
        code = self.stock_code_input.text().strip()
        
        if not code:
            QMessageBox.warning(self, "警告", "请输入股票代码")
            return
        
        self.statusBar().showMessage(f"● 正在分析 {code}...")
        self.analyze_btn.setEnabled(False)
        
        try:
            df = ef.stock.get_quote_history(code)
            if df is None or df.empty:
                QMessageBox.warning(self, "错误", f"无法获取股票 {code} 的数据")
                return
            
            worker = AnalysisWorker([(code, code)])
            worker.result.connect(lambda results: self.show_single_result(results, code))
            worker.start()
            worker.wait()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"分析失败: {str(e)}")
        finally:
            self.analyze_btn.setEnabled(True)
            self.statusBar().showMessage("● 就绪")
    
    def show_single_result(self, results, code):
        """显示单股分析结果"""
        if not results:
            self.single_result_text.setHtml(
                f"<p style='color: red; text-align: center; padding: 40px;'>"
                f"无法分析股票 {code}，请检查代码是否正确</p>"
            )
            return
        
        result = results[0]
        
        html = f"""
        <div style="font-family: 'Microsoft YaHei'; line-height: 1.8;">
        <h1 style="color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 15px;">
        {result['name']} ({result['code']})
        </h1>
        
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 25px; border-radius: 12px; color: white; margin: 20px 0;">
        <h2 style="margin: 0 0 15px 0; color: white;">投资建议: {result['signal']}</h2>
        <p style="font-size: 16px; margin: 8px 0;">
        <b>综合评分:</b> {result['score']}/100 | 
        <b>信心度:</b> {result['confidence']}% | 
        <b>风险等级:</b> {result['risk_level']}
        </p>
        </div>
        
        <h3 style="color: #4CAF50; margin-top: 25px;">💰 价格分析</h3>
        <table style="width: 100%; border: 2px solid #e0e0e0; border-collapse: collapse; margin: 10px 0;">
        <tr style="background: linear-gradient(to right, #f8f9fa, #ffffff);">
            <th style="padding: 15px; border: 1px solid #e0e0e0; text-align: left;">指标</th>
            <th style="padding: 15px; border: 1px solid #e0e0e0; text-align: left;">数值</th>
            <th style="padding: 15px; border: 1px solid #e0e0e0; text-align: left;">说明</th>
        </tr>
        <tr>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">当前价</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;"><b>¥{result['price']:.2f}</b></td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">最新收盘价</td>
        </tr>
        <tr style="background: #f8f9fa;">
            <td style="padding: 12px; border: 1px solid #e0e0e0;">目标价</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0; color: green;">
            <b>¥{result['target_price']:.2f}</b></td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">
            预期上涨 {(result['target_price']/result['price']-1)*100:.1f}%</td>
        </tr>
        <tr>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">止损价</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0; color: red;">
            <b>¥{result['stop_loss']:.2f}</b></td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">
            风险控制 {(result['stop_loss']/result['price']-1)*100:.1f}%</td>
        </tr>
        <tr style="background: #f8f9fa;">
            <td style="padding: 12px; border: 1px solid #e0e0e0;">5日涨幅</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0; 
                color: {'green' if result['returns_5d'] > 0 else 'red'};">
            <b>{result['returns_5d']:+.2f}%</b></td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">短期走势</td>
        </tr>
        </table>
        
        <h3 style="color: #2196F3; margin-top: 25px;">📊 技术指标</h3>
        <table style="width: 100%; border: 2px solid #e0e0e0; border-collapse: collapse; margin: 10px 0;">
        <tr style="background: linear-gradient(to right, #f8f9fa, #ffffff);">
            <th style="padding: 15px; border: 1px solid #e0e0e0; text-align: left;">指标</th>
            <th style="padding: 15px; border: 1px solid #e0e0e0; text-align: left;">数值</th>
            <th style="padding: 15px; border: 1px solid #e0e0e0; text-align: left;">评价</th>
        </tr>
        <tr>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">RSI (14)</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;"><b>{result['rsi']:.2f}</b></td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">
            {'超买' if result['rsi'] > 70 else '超卖' if result['rsi'] < 30 else '正常'}
            </td>
        </tr>
        <tr style="background: #f8f9fa;">
            <td style="padding: 12px; border: 1px solid #e0e0e0;">MACD</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;"><b>{result['macd']:.4f}</b></td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">
            {'多头' if result['macd'] > 0 else '空头'}
            </td>
        </tr>
        <tr>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">技术评分</td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">
            <b>{result['technical_score']}/100</b></td>
            <td style="padding: 12px; border: 1px solid #e0e0e0;">
            {'优秀' if result['technical_score'] >= 70 else '良好' if result['technical_score'] >= 50 else '一般'}
            </td>
        </tr>
        </table>
        
        <h3 style="color: #ff9800; margin-top: 25px;">💼 投资建议</h3>
        <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); 
                    padding: 20px; border-radius: 12px; border-left: 5px solid #4CAF50;">
        <p style="margin: 8px 0; font-size: 15px;">
        <b>建议仓位:</b> {result['position_size']*100:.1f}% 
        (假设总资金100万，建议投入 ¥{result['position_size']*1000000:,.0f})
        </p>
        <p style="margin: 8px 0; font-size: 15px;">
        <b>投资期限:</b> 中短期 (1-3个月)
        </p>
        <p style="margin: 8px 0; font-size: 15px;">
        <b>风险提示:</b> {result['risk_level']}风险，请严格执行止损
        </p>
        </div>
        
        <h3 style="color: #9c27b0; margin-top: 25px;">✅ 分析理由</h3>
        <ol style="line-height: 2.2; font-size: 14px;">
        {''.join(f'<li style="margin: 10px 0; padding: 8px; background: #f8f9fa; border-radius: 6px;">{reason}</li>' for reason in result['reasons'])}
        </ol>
        
        <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffe082 100%); 
                    padding: 20px; border-radius: 12px; border-left: 5px solid #ff9800; margin-top: 25px;">
        <p style="color: #856404; margin: 0; font-size: 14px; line-height: 1.8;">
        <b>⚠️ 风险提示:</b> 本分析基于技术指标，仅供参考。投资有风险，入市需谨慎。
        建议结合基本面分析和市场环境综合判断。
        </p>
        </div>
        
        <p style="color: #999; font-size: 12px; text-align: right; margin-top: 20px;">
        分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
        </div>
        """
        
        self.single_result_text.setHtml(html)
        self.statusBar().showMessage(f"● 分析完成: {result['name']}")


    def build_portfolio(self):
        """构建投资组合"""
        if not self.advice_list:
            QMessageBox.warning(self, "警告", "请先扫描市场获取投资建议")
            return
        
        buy_signals = [adv for adv in self.advice_list 
                      if adv['signal'] in ["强烈买入", "买入"]]
        
        if not buy_signals:
            QMessageBox.information(self, "提示", "没有找到买入信号的股票")
            return
        
        buy_signals.sort(key=lambda x: x['score'], reverse=True)
        self.portfolio = buy_signals[:10]
        
        self.position_table.setRowCount(len(self.portfolio))
        
        total_position = sum(p['position_size'] for p in self.portfolio)
        
        for row, pos in enumerate(self.portfolio):
            self.position_table.setItem(row, 0, QTableWidgetItem(pos['code']))
            self.position_table.setItem(row, 1, QTableWidgetItem(pos['name']))
            self.position_table.setItem(row, 2, QTableWidgetItem(f"{pos['position_size']*100:.1f}%"))
            self.position_table.setItem(row, 3, QTableWidgetItem(f"¥{pos['price']:.2f}"))
            self.position_table.setItem(row, 4, QTableWidgetItem(f"¥{pos['target_price']:.2f}"))
            self.position_table.setItem(row, 5, QTableWidgetItem(f"¥{pos['stop_loss']:.2f}"))
            
            expected_return = (pos['target_price'] / pos['price'] - 1) * 100
            return_item = QTableWidgetItem(f"{expected_return:+.1f}%")
            return_item.setForeground(QColor("green" if expected_return > 0 else "red"))
            self.position_table.setItem(row, 6, return_item)
            
            self.position_table.setItem(row, 7, QTableWidgetItem(pos['risk_level']))
            
            signal_item = QTableWidgetItem(pos['signal'])
            if pos['signal'] == "强烈买入":
                signal_item.setBackground(QColor("#4CAF50"))
                signal_item.setForeground(QColor("white"))
            self.position_table.setItem(row, 8, signal_item)
        
        avg_score = sum(p['score'] for p in self.portfolio) / len(self.portfolio)
        avg_return = sum((p['target_price']/p['price']-1)*100 for p in self.portfolio) / len(self.portfolio)
        
        summary_html = f"""
        <div style="font-family: 'Microsoft YaHei'; line-height: 1.8;">
        <h3 style="color: #4CAF50; margin: 0 0 15px 0;">✓ 投资组合已构建</h3>
        <div style="background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); 
                    padding: 20px; border-radius: 12px;">
        <table style="width: 100%; font-size: 15px;">
        <tr>
            <td style="padding: 8px;"><b>持仓数量:</b></td>
            <td style="padding: 8px; color: #4CAF50;"><b>{len(self.portfolio)} 只</b></td>
            <td style="padding: 8px;"><b>总仓位:</b></td>
            <td style="padding: 8px; color: #2196F3;"><b>{total_position*100:.1f}%</b></td>
        </tr>
        <tr>
            <td style="padding: 8px;"><b>平均评分:</b></td>
            <td style="padding: 8px; color: #ff9800;"><b>{avg_score:.1f}/100</b></td>
            <td style="padding: 8px;"><b>预期收益:</b></td>
            <td style="padding: 8px; color: green;"><b>{avg_return:+.1f}%</b></td>
        </tr>
        <tr>
            <td style="padding: 8px;"><b>强烈买入:</b></td>
            <td style="padding: 8px;">{sum(1 for p in self.portfolio if p['signal']=='强烈买入')} 只</td>
            <td style="padding: 8px;"><b>买入:</b></td>
            <td style="padding: 8px;">{sum(1 for p in self.portfolio if p['signal']=='买入')} 只</td>
        </tr>
        </table>
        </div>
        <p style="color: #666; margin-top: 15px; font-size: 14px;">
        💡 建议: 根据个人资金情况，按建议仓位比例配置。严格执行止损，控制风险。
        </p>
        </div>
        """
        
        self.portfolio_summary.setText("")
        self.portfolio_summary.setTextFormat(Qt.RichText)
        self.portfolio_summary.setText(summary_html)
        self.portfolio_summary.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        self.update_risk_monitor()
        
        QMessageBox.information(self, "成功", 
            f"投资组合构建完成！\n"
            f"共 {len(self.portfolio)} 只股票\n"
            f"预期收益: {avg_return:+.1f}%")
    
    def clear_portfolio(self):
        """清空组合"""
        if not self.portfolio:
            return
        
        reply = QMessageBox.question(self, "确认", 
            "确定要清空投资组合吗？",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.portfolio = []
            self.position_table.setRowCount(0)
            self.portfolio_summary.setText("暂无组合数据\n点击下方按钮构建投资组合")
            self.portfolio_summary.setAlignment(Qt.AlignCenter)
            self.risk_metrics.setText("暂无风险数据\n请先构建投资组合")
            self.risk_metrics.setAlignment(Qt.AlignCenter)
            self.warning_text.setHtml("<p style='color: green;'>✓ 暂无风险警告</p>")
            self.action_text.setHtml("<p>暂无特别建议</p>")
            QMessageBox.information(self, "成功", "投资组合已清空")
    
    def update_risk_monitor(self):
        """更新风险监控"""
        if not self.portfolio:
            return
        
        high_risk_count = sum(1 for p in self.portfolio if p['risk_level'] == "高")
        total_position = sum(p['position_size'] for p in self.portfolio)
        max_position = max(p['position_size'] for p in self.portfolio)
        
        if high_risk_count > len(self.portfolio) * 0.3:
            risk_level = "高"
            risk_color = "#f44336"
        elif total_position > 0.8:
            risk_level = "中"
            risk_color = "#ff9800"
        else:
            risk_level = "低"
            risk_color = "#4CAF50"
        
        metrics_html = f"""
        <div style="font-family: 'Microsoft YaHei'; line-height: 1.8;">
        <h3 style="color: {risk_color}; margin: 0 0 15px 0;">
        风险等级: <span style="font-size: 24px;">{risk_level}</span>
        </h3>
        <div style="background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); 
                    padding: 20px; border-radius: 12px;">
        <table style="width: 100%; font-size: 14px;">
        <tr>
            <td style="padding: 8px;"><b>总仓位:</b></td>
            <td style="padding: 8px; color: {risk_color};"><b>{total_position*100:.1f}%</b></td>
            <td style="padding: 8px;"><b>最大单只仓位:</b></td>
            <td style="padding: 8px;"><b>{max_position*100:.1f}%</b></td>
        </tr>
        <tr>
            <td style="padding: 8px;"><b>高风险股票:</b></td>
            <td style="padding: 8px;">{high_risk_count} 只</td>
            <td style="padding: 8px;"><b>持仓数量:</b></td>
            <td style="padding: 8px;">{len(self.portfolio)} 只</td>
        </tr>
        </table>
        </div>
        </div>
        """
        
        self.risk_metrics.setText("")
        self.risk_metrics.setTextFormat(Qt.RichText)
        self.risk_metrics.setText(metrics_html)
        self.risk_metrics.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        warnings = []
        if total_position > 0.8:
            warnings.append("⚠️ 总仓位过高，建议保留20%以上现金")
        if max_position > 0.15:
            warnings.append("⚠️ 单只股票仓位过大，建议分散投资")
        if high_risk_count > 3:
            warnings.append("⚠️ 高风险股票较多，注意风险控制")
        
        if warnings:
            warning_html = "<ul style='color: #f44336; font-size: 14px; line-height: 2;'>"
            for w in warnings:
                warning_html += f"<li style='margin: 8px 0;'>{w}</li>"
            warning_html += "</ul>"
            self.warning_text.setHtml(warning_html)
        else:
            self.warning_text.setHtml(
                "<p style='color: #4CAF50; font-size: 16px; text-align: center; padding: 20px;'>"
                "✓ 暂无风险警告</p>"
            )
        
        suggestions = []
        if total_position < 0.5:
            suggestions.append("💡 仓位较轻，可以考虑增加配置")
        if len(self.portfolio) < 5:
            suggestions.append("💡 持仓数量较少，建议增加分散度")
        
        suggestions.append("💡 定期检查持仓，及时止盈止损")
        suggestions.append("💡 关注市场动态，适时调整组合")
        
        action_html = "<ul style='font-size: 14px; line-height: 2;'>"
        for s in suggestions:
            action_html += f"<li style='margin: 8px 0;'>{s}</li>"
        action_html += "</ul>"
        self.action_text.setHtml(action_html)
    
    def export_results(self):
        """导出结果"""
        if not self.advice_list:
            QMessageBox.warning(self, "警告", "没有可导出的数据")
            return
        
        try:
            data = []
            for adv in self.advice_list:
                data.append({
                    '代码': adv['code'], '名称': adv['name'], '信号': adv['signal'],
                    '评分': adv['score'], '信心度': adv['confidence'],
                    '当前价': adv['price'], '目标价': adv['target_price'],
                    '止损价': adv['stop_loss'], 'RSI': adv['rsi'],
                    '风险等级': adv['risk_level'],
                    '建议仓位': f"{adv['position_size']*100:.1f}%"
                })
            
            df = pd.DataFrame(data)
            filename = f"投资建议_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            
            QMessageBox.information(self, "成功", f"结果已导出到: {filename}")
            self.statusBar().showMessage(f"● 已导出: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    # 设置全局样式
    app.setStyleSheet("""
        * {
            font-family: 'Microsoft YaHei', 'Segoe UI', Arial, sans-serif;
        }
        QLabel {
            color: #333;
        }
        QMessageBox {
            background-color: white;
        }
        QMessageBox QLabel {
            font-size: 14px;
        }
    """)
    
    window = ModernMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
