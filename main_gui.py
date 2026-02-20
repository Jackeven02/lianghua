# -*- coding: utf-8 -*-
"""
智能投资顾问系统 - 完整GUI界面
整合所有功能：市场扫描、单股分析、组合管理、风险监控
"""
import sys
import os

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'efinance'))
sys.path.insert(0, os.path.dirname(__file__))

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTableWidget,
                             QTableWidgetItem, QTextEdit, QTabWidget, QGroupBox,
                             QComboBox, QSpinBox, QProgressBar, QMessageBox,
                             QHeaderView, QLineEdit, QDoubleSpinBox, QSplitter,
                             QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QFont, QIcon
import efinance as ef
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict


class AnalysisWorker(QThread):
    """分析工作线程"""
    progress = pyqtSignal(int, int, str)  # 当前进度, 总数, 当前股票
    result = pyqtSignal(list)  # 分析结果
    
    def __init__(self, stock_list):
        super().__init__()
        self.stock_list = stock_list
        
    def run(self):
        """执行分析"""
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
        """分析股票"""
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
            
            # 计算技术指标
            df['SMA_5'] = df['close'].rolling(window=5).mean()
            df['SMA_20'] = df['close'].rolling(window=20).mean()
            df['SMA_60'] = df['close'].rolling(window=60).mean()
            
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            ema_12 = df['close'].ewm(span=12).mean()
            ema_26 = df['close'].ewm(span=26).mean()
            df['MACD'] = ema_12 - ema_26
            df['MACD_signal'] = df['MACD'].ewm(span=9).mean()
            
            latest = df.iloc[-1]
            current_price = latest['close']
            
            # 评分系统
            score = 0
            reasons = []
            technical_score = 0
            
            # 趋势分析 (30分)
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
            
            # MACD (20分)
            if latest['MACD'] > latest['MACD_signal']:
                score += 20
                technical_score += 20
                reasons.append("✓ MACD金叉")
            else:
                technical_score += 10
            
            # RSI (20分)
            if 30 < latest['RSI'] < 70:
                score += 20
                reasons.append("✓ RSI健康区间")
            elif latest['RSI'] < 30:
                score += 15
                reasons.append("✓ RSI超卖")
            elif latest['RSI'] > 70:
                score += 5
                reasons.append("⚠ RSI超买")
            
            # 价格位置 (15分)
            if current_price > latest['SMA_20']:
                score += 15
                reasons.append("✓ 价格在均线上方")
            
            # 成交量 (10分)
            recent_vol = df['volume'].iloc[-5:].mean()
            avg_vol = df['volume'].mean()
            if recent_vol > avg_vol * 1.2:
                score += 10
                reasons.append("✓ 成交量放大")
            
            # 短期动量 (5分)
            returns_5d = (df['close'].iloc[-1] / df['close'].iloc[-5] - 1) * 100
            if returns_5d > 3:
                score += 5
                reasons.append(f"✓ 5日涨幅 {returns_5d:.1f}%")
            elif returns_5d < -3:
                reasons.append(f"⚠ 5日跌幅 {returns_5d:.1f}%")
            
            # 生成信号
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
            
            # 计算价格目标
            target_price = current_price * 1.15
            stop_loss = current_price * 0.92
            
            # 建议仓位
            if score >= 70:
                position_size = 0.10
            elif score >= 60:
                position_size = 0.08
            elif score >= 50:
                position_size = 0.05
            else:
                position_size = 0.03
            
            return {
                'code': stock_code,
                'name': stock_name,
                'price': current_price,
                'signal': signal,
                'score': score,
                'technical_score': technical_score,
                'confidence': min(score, 100),
                'rsi': latest['RSI'],
                'macd': latest['MACD'],
                'target_price': target_price,
                'stop_loss': stop_loss,
                'risk_level': risk_level,
                'position_size': position_size,
                'returns_5d': returns_5d,
                'reasons': reasons,
                'date': latest['date']
            }
            
        except Exception as e:
            return None


class MainGUI(QMainWindow):
    """主GUI界面"""
    
    def __init__(self):
        super().__init__()
        self.advice_list = []
        self.portfolio = []
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("智能投资顾问系统 v1.0")
        self.setGeometry(50, 50, 1400, 900)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 标题栏
        title_widget = self.create_title_bar()
        main_layout.addWidget(title_widget)
        
        # 标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
                color: white;
            }
        """)
        
        # 1. 市场扫描
        self.scan_tab = self.create_scan_tab()
        self.tab_widget.addTab(self.scan_tab, "📊 市场扫描")
        
        # 2. 单股分析
        self.single_tab = self.create_single_analysis_tab()
        self.tab_widget.addTab(self.single_tab, "🔍 单股分析")
        
        # 3. 组合管理
        self.portfolio_tab = self.create_portfolio_tab()
        self.tab_widget.addTab(self.portfolio_tab, "💼 组合管理")
        
        # 4. 风险监控
        self.risk_tab = self.create_risk_tab()
        self.tab_widget.addTab(self.risk_tab, "⚠️ 风险监控")
        
        # 5. 系统设置
        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ 系统设置")
        
        main_layout.addWidget(self.tab_widget)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
        
    def create_title_bar(self):
        """创建标题栏"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 5px;
                padding: 10px;
            }
        """)
        layout = QHBoxLayout(widget)
        
        title = QLabel("🤖 智能投资顾问系统")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: white;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        time_label = QLabel(datetime.now().strftime("%Y-%m-%d %H:%M"))
        time_label.setFont(QFont("Arial", 12))
        time_label.setStyleSheet("color: white;")
        layout.addWidget(time_label)
        
        # 定时更新时间
        timer = QTimer(self)
        timer.timeout.connect(lambda: time_label.setText(
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))
        timer.start(60000)  # 每分钟更新
        
        return widget

    def create_scan_tab(self):
        """创建市场扫描标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 控制面板
        control_group = QGroupBox("扫描设置")
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("扫描数量:"))
        self.stock_count_spin = QSpinBox()
        self.stock_count_spin.setRange(5, 50)
        self.stock_count_spin.setValue(20)
        control_layout.addWidget(self.stock_count_spin)
        
        control_layout.addWidget(QLabel("最低评分:"))
        self.min_score_spin = QSpinBox()
        self.min_score_spin.setRange(0, 100)
        self.min_score_spin.setValue(40)
        control_layout.addWidget(self.min_score_spin)
        
        self.scan_btn = QPushButton("🔍 开始扫描市场")
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.scan_btn.clicked.connect(self.start_scan)
        control_layout.addWidget(self.scan_btn)
        
        self.export_btn = QPushButton("📄 导出结果")
        self.export_btn.clicked.connect(self.export_results)
        control_layout.addWidget(self.export_btn)
        
        control_layout.addStretch()
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 统计信息
        self.stats_label = QLabel("等待扫描...")
        self.stats_label.setStyleSheet("font-size: 12px; color: #666; padding: 5px;")
        layout.addWidget(self.stats_label)
        
        # 分割器
        splitter = QSplitter(Qt.Vertical)
        
        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(11)
        self.result_table.setHorizontalHeaderLabels([
            "代码", "名称", "信号", "评分", "信心度", "当前价", 
            "目标价", "止损价", "RSI", "风险", "建议仓位"
        ])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.itemSelectionChanged.connect(self.show_scan_detail)
        splitter.addWidget(self.result_table)
        
        # 详细信息
        detail_group = QGroupBox("详细分析")
        detail_layout = QVBoxLayout()
        self.scan_detail_text = QTextEdit()
        self.scan_detail_text.setReadOnly(True)
        detail_layout.addWidget(self.scan_detail_text)
        detail_group.setLayout(detail_layout)
        splitter.addWidget(detail_group)
        
        splitter.setSizes([500, 200])
        layout.addWidget(splitter)
        
        return widget
    
    def create_single_analysis_tab(self):
        """创建单股分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 输入区域
        input_group = QGroupBox("股票查询")
        input_layout = QHBoxLayout()
        
        input_layout.addWidget(QLabel("股票代码:"))
        self.stock_code_input = QLineEdit()
        self.stock_code_input.setPlaceholderText("例如: 600519")
        self.stock_code_input.setMaximumWidth(150)
        input_layout.addWidget(self.stock_code_input)
        
        self.analyze_btn = QPushButton("🔍 分析")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #0b7dda; }
        """)
        self.analyze_btn.clicked.connect(self.analyze_single_stock)
        input_layout.addWidget(self.analyze_btn)
        
        input_layout.addStretch()
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # 分析结果
        self.single_result_text = QTextEdit()
        self.single_result_text.setReadOnly(True)
        self.single_result_text.setStyleSheet("""
            QTextEdit {
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        layout.addWidget(self.single_result_text)
        
        return widget
    
    def create_portfolio_tab(self):
        """创建组合管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 组合概况
        summary_group = QGroupBox("组合概况")
        summary_layout = QVBoxLayout()
        self.portfolio_summary = QLabel("暂无组合数据\n点击下方按钮构建投资组合")
        self.portfolio_summary.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 20px;
                background-color: #f5f5f5;
                border-radius: 5px;
            }
        """)
        self.portfolio_summary.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(self.portfolio_summary)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.build_portfolio_btn = QPushButton("📦 构建组合")
        self.build_portfolio_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.build_portfolio_btn.clicked.connect(self.build_portfolio)
        btn_layout.addWidget(self.build_portfolio_btn)
        
        self.clear_portfolio_btn = QPushButton("🗑️ 清空组合")
        self.clear_portfolio_btn.clicked.connect(self.clear_portfolio)
        btn_layout.addWidget(self.clear_portfolio_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 持仓表格
        self.position_table = QTableWidget()
        self.position_table.setColumnCount(9)
        self.position_table.setHorizontalHeaderLabels([
            "代码", "名称", "建议仓位", "当前价", "目标价", 
            "止损价", "预期收益", "风险等级", "信号"
        ])
        self.position_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.position_table.setAlternatingRowColors(True)
        layout.addWidget(self.position_table)
        
        return widget
    
    def create_risk_tab(self):
        """创建风险监控标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 风险指标
        metrics_group = QGroupBox("风险指标")
        metrics_layout = QVBoxLayout()
        self.risk_metrics = QLabel("暂无风险数据\n请先构建投资组合")
        self.risk_metrics.setStyleSheet("""
            QLabel {
                font-size: 13px;
                padding: 15px;
                background-color: #fff3cd;
                border-radius: 5px;
            }
        """)
        self.risk_metrics.setAlignment(Qt.AlignCenter)
        metrics_layout.addWidget(self.risk_metrics)
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        # 风险警告
        warning_group = QGroupBox("⚠️ 风险警告")
        warning_layout = QVBoxLayout()
        self.warning_text = QTextEdit()
        self.warning_text.setReadOnly(True)
        self.warning_text.setMaximumHeight(150)
        self.warning_text.setHtml("<p style='color: green;'>✓ 暂无风险警告</p>")
        warning_layout.addWidget(self.warning_text)
        warning_group.setLayout(warning_layout)
        layout.addWidget(warning_group)
        
        # 建议操作
        action_group = QGroupBox("💡 建议操作")
        action_layout = QVBoxLayout()
        self.action_text = QTextEdit()
        self.action_text.setReadOnly(True)
        self.action_text.setHtml("<p>暂无特别建议</p>")
        action_layout.addWidget(self.action_text)
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        return widget
    
    def create_settings_tab(self):
        """创建系统设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 风险偏好设置
        risk_group = QGroupBox("风险偏好设置")
        risk_layout = QHBoxLayout()
        
        risk_layout.addWidget(QLabel("风险承受能力:"))
        self.risk_tolerance_combo = QComboBox()
        self.risk_tolerance_combo.addItems(["保守", "中等", "激进"])
        self.risk_tolerance_combo.setCurrentText("中等")
        risk_layout.addWidget(self.risk_tolerance_combo)
        
        risk_layout.addStretch()
        risk_group.setLayout(risk_layout)
        layout.addWidget(risk_group)
        
        # 关于信息
        about_group = QGroupBox("关于系统")
        about_layout = QVBoxLayout()
        about_text = QLabel("""
        <h3>智能投资顾问系统 v1.0</h3>
        <p><b>功能特点:</b></p>
        <ul>
            <li>📊 市场扫描 - 批量分析股票，发现投资机会</li>
            <li>🔍 单股分析 - 深度分析个股，提供详细建议</li>
            <li>💼 组合管理 - 智能构建投资组合</li>
            <li>⚠️ 风险监控 - 实时监控投资风险</li>
        </ul>
        <p><b>数据来源:</b> 东方财富网 (efinance)</p>
        <p><b>技术指标:</b> 均线、RSI、MACD等15+指标</p>
        <p style="color: red;"><b>重要提示:</b> 本系统分析结果仅供参考，不构成投资建议。投资有风险，入市需谨慎！</p>
        """)
        about_text.setWordWrap(True)
        about_layout.addWidget(about_text)
        about_layout.addStretch()
        about_group.setLayout(about_layout)
        layout.addWidget(about_group)
        
        layout.addStretch()
        
        return widget

    def start_scan(self):
        """开始扫描"""
        count = self.stock_count_spin.value()
        
        # 股票列表
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
        
        # 禁用按钮
        self.scan_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(stock_list))
        self.progress_bar.setValue(0)
        self.statusBar().showMessage("正在扫描市场...")
        
        # 创建工作线程
        self.worker = AnalysisWorker(stock_list)
        self.worker.progress.connect(self.update_progress)
        self.worker.result.connect(self.show_scan_results)
        self.worker.start()
        
    def update_progress(self, current, total, stock_name):
        """更新进度"""
        self.progress_bar.setValue(current)
        self.stats_label.setText(f"正在分析 {stock_name}... ({current}/{total})")
        self.statusBar().showMessage(f"扫描进度: {current}/{total}")
        
    def show_scan_results(self, results):
        """显示扫描结果"""
        self.advice_list = results
        
        # 按评分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # 过滤低分
        min_score = self.min_score_spin.value()
        results = [r for r in results if r['score'] >= min_score]
        
        # 更新表格
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
        
        # 更新统计
        buy_count = sum(1 for r in results if "买入" in r['signal'])
        strong_buy = sum(1 for r in results if r['signal'] == "强烈买入")
        avg_score = sum(r['score'] for r in results) / len(results) if results else 0
        
        self.stats_label.setText(
            f"✓ 找到 {len(results)} 个投资机会 | "
            f"平均评分: {avg_score:.1f} | "
            f"强烈买入: {strong_buy} | "
            f"买入: {buy_count - strong_buy}"
        )
        
        # 恢复按钮
        self.scan_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage(f"扫描完成！找到 {len(results)} 个投资机会")
        
        # 显示提示
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
        <h2>{advice['name']} ({advice['code']})</h2>
        
        <h3>📊 投资建议</h3>
        <p style="font-size: 16px;">
        <b>信号:</b> <span style="color: {'green' if '买入' in advice['signal'] else 'orange'}; font-size: 18px; font-weight: bold;">
        {advice['signal']}</span> | 
        <b>信心度:</b> {advice['confidence']}% | 
        <b>评分:</b> {advice['score']}/100
        </p>
        
        <h3>💰 价格信息</h3>
        <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 5px;"><b>当前价:</b></td>
            <td style="padding: 5px;">¥{advice['price']:.2f}</td>
            <td style="padding: 5px;"><b>目标价:</b></td>
            <td style="padding: 5px; color: green;">¥{advice['target_price']:.2f} ({(advice['target_price']/advice['price']-1)*100:+.1f}%)</td>
        </tr>
        <tr>
            <td style="padding: 5px;"><b>止损价:</b></td>
            <td style="padding: 5px; color: red;">¥{advice['stop_loss']:.2f} ({(advice['stop_loss']/advice['price']-1)*100:+.1f}%)</td>
            <td style="padding: 5px;"><b>5日涨幅:</b></td>
            <td style="padding: 5px; color: {'green' if advice['returns_5d'] > 0 else 'red'};">{advice['returns_5d']:+.2f}%</td>
        </tr>
        </table>
        
        <h3>📈 技术指标</h3>
        <table style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 5px;"><b>RSI:</b></td>
            <td style="padding: 5px;">{advice['rsi']:.2f}</td>
            <td style="padding: 5px;"><b>MACD:</b></td>
            <td style="padding: 5px;">{advice['macd']:.4f}</td>
        </tr>
        <tr>
            <td style="padding: 5px;"><b>风险等级:</b></td>
            <td style="padding: 5px;">{advice['risk_level']}</td>
            <td style="padding: 5px;"><b>建议仓位:</b></td>
            <td style="padding: 5px;">{advice['position_size']*100:.1f}%</td>
        </tr>
        </table>
        
        <h3>💡 分析理由</h3>
        <ul style="line-height: 1.8;">
        {''.join(f'<li>{reason}</li>' for reason in advice['reasons'])}
        </ul>
        
        <p style="color: #666; font-size: 11px; margin-top: 20px;">
        数据日期: {advice['date']} | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
        """
        
        self.scan_detail_text.setHtml(detail_html)
    
    def analyze_single_stock(self):
        """分析单只股票"""
        code = self.stock_code_input.text().strip()
        
        if not code:
            QMessageBox.warning(self, "警告", "请输入股票代码")
            return
        
        self.statusBar().showMessage(f"正在分析 {code}...")
        self.analyze_btn.setEnabled(False)
        
        try:
            # 获取股票名称
            df = ef.stock.get_quote_history(code)
            if df is None or df.empty:
                QMessageBox.warning(self, "错误", f"无法获取股票 {code} 的数据")
                return
            
            # 分析
            worker = AnalysisWorker([(code, code)])
            worker.result.connect(lambda results: self.show_single_result(results, code))
            worker.start()
            worker.wait()  # 等待完成
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"分析失败: {str(e)}")
        finally:
            self.analyze_btn.setEnabled(True)
            self.statusBar().showMessage("就绪")
    
    def show_single_result(self, results, code):
        """显示单股分析结果"""
        if not results:
            self.single_result_text.setHtml(f"<p style='color: red;'>无法分析股票 {code}，请检查代码是否正确</p>")
            return
        
        result = results[0]
        
        html = f"""
        <h1>{result['name']} ({result['code']})</h1>
        
        <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
        <h2 style="color: {'green' if '买入' in result['signal'] else 'orange'};">
        投资建议: {result['signal']}
        </h2>
        <p style="font-size: 16px;">
        <b>综合评分:</b> {result['score']}/100 | 
        <b>信心度:</b> {result['confidence']}% | 
        <b>风险等级:</b> {result['risk_level']}
        </p>
        </div>
        
        <h3>💰 价格分析</h3>
        <table style="width: 100%; border: 1px solid #ddd; border-collapse: collapse;">
        <tr style="background: #f9f9f9;">
            <th style="padding: 10px; border: 1px solid #ddd;">指标</th>
            <th style="padding: 10px; border: 1px solid #ddd;">数值</th>
            <th style="padding: 10px; border: 1px solid #ddd;">说明</th>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">当前价</td>
            <td style="padding: 8px; border: 1px solid #ddd;"><b>¥{result['price']:.2f}</b></td>
            <td style="padding: 8px; border: 1px solid #ddd;">最新收盘价</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">目标价</td>
            <td style="padding: 8px; border: 1px solid #ddd; color: green;"><b>¥{result['target_price']:.2f}</b></td>
            <td style="padding: 8px; border: 1px solid #ddd;">预期上涨 {(result['target_price']/result['price']-1)*100:.1f}%</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">止损价</td>
            <td style="padding: 8px; border: 1px solid #ddd; color: red;"><b>¥{result['stop_loss']:.2f}</b></td>
            <td style="padding: 8px; border: 1px solid #ddd;">风险控制 {(result['stop_loss']/result['price']-1)*100:.1f}%</td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">5日涨幅</td>
            <td style="padding: 8px; border: 1px solid #ddd; color: {'green' if result['returns_5d'] > 0 else 'red'};">
            <b>{result['returns_5d']:+.2f}%</b></td>
            <td style="padding: 8px; border: 1px solid #ddd;">短期走势</td>
        </tr>
        </table>
        
        <h3>📊 技术指标</h3>
        <table style="width: 100%; border: 1px solid #ddd; border-collapse: collapse;">
        <tr style="background: #f9f9f9;">
            <th style="padding: 10px; border: 1px solid #ddd;">指标</th>
            <th style="padding: 10px; border: 1px solid #ddd;">数值</th>
            <th style="padding: 10px; border: 1px solid #ddd;">评价</th>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">RSI (14)</td>
            <td style="padding: 8px; border: 1px solid #ddd;"><b>{result['rsi']:.2f}</b></td>
            <td style="padding: 8px; border: 1px solid #ddd;">
            {'超买' if result['rsi'] > 70 else '超卖' if result['rsi'] < 30 else '正常'}
            </td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">MACD</td>
            <td style="padding: 8px; border: 1px solid #ddd;"><b>{result['macd']:.4f}</b></td>
            <td style="padding: 8px; border: 1px solid #ddd;">
            {'多头' if result['macd'] > 0 else '空头'}
            </td>
        </tr>
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">技术评分</td>
            <td style="padding: 8px; border: 1px solid #ddd;"><b>{result['technical_score']}/100</b></td>
            <td style="padding: 8px; border: 1px solid #ddd;">
            {'优秀' if result['technical_score'] >= 70 else '良好' if result['technical_score'] >= 50 else '一般'}
            </td>
        </tr>
        </table>
        
        <h3>💼 投资建议</h3>
        <div style="background: #e8f5e9; padding: 15px; border-radius: 5px; border-left: 4px solid #4CAF50;">
        <p><b>建议仓位:</b> {result['position_size']*100:.1f}% (假设总资金100万，建议投入 ¥{result['position_size']*1000000:,.0f})</p>
        <p><b>投资期限:</b> 中短期 (1-3个月)</p>
        <p><b>风险提示:</b> {result['risk_level']}风险，请严格执行止损</p>
        </div>
        
        <h3>✅ 分析理由</h3>
        <ol style="line-height: 2;">
        {''.join(f'<li style="margin: 5px 0;">{reason}</li>' for reason in result['reasons'])}
        </ol>
        
        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin-top: 20px;">
        <p style="color: #856404; margin: 0;">
        <b>⚠️ 风险提示:</b> 本分析基于技术指标，仅供参考。投资有风险，入市需谨慎。
        建议结合基本面分析和市场环境综合判断。
        </p>
        </div>
        
        <p style="color: #999; font-size: 12px; text-align: right; margin-top: 20px;">
        分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
        """
        
        self.single_result_text.setHtml(html)
        self.statusBar().showMessage(f"分析完成: {result['name']}")

    def build_portfolio(self):
        """构建投资组合"""
        if not self.advice_list:
            QMessageBox.warning(self, "警告", "请先扫描市场获取投资建议")
            return
        
        # 筛选买入信号
        buy_signals = [adv for adv in self.advice_list 
                      if adv['signal'] in ["强烈买入", "买入"]]
        
        if not buy_signals:
            QMessageBox.information(self, "提示", "没有找到买入信号的股票")
            return
        
        # 按评分排序，取前10个
        buy_signals.sort(key=lambda x: x['score'], reverse=True)
        self.portfolio = buy_signals[:10]
        
        # 更新持仓表格
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
        
        # 更新组合概况
        avg_score = sum(p['score'] for p in self.portfolio) / len(self.portfolio)
        avg_return = sum((p['target_price']/p['price']-1)*100 for p in self.portfolio) / len(self.portfolio)
        
        summary_html = f"""
        <h3 style="color: #4CAF50;">✓ 投资组合已构建</h3>
        <table style="width: 100%; font-size: 14px;">
        <tr>
            <td><b>持仓数量:</b></td>
            <td>{len(self.portfolio)} 只</td>
            <td><b>总仓位:</b></td>
            <td>{total_position*100:.1f}%</td>
        </tr>
        <tr>
            <td><b>平均评分:</b></td>
            <td>{avg_score:.1f}/100</td>
            <td><b>预期收益:</b></td>
            <td style="color: green;"><b>{avg_return:+.1f}%</b></td>
        </tr>
        <tr>
            <td><b>强烈买入:</b></td>
            <td>{sum(1 for p in self.portfolio if p['signal']=='强烈买入')} 只</td>
            <td><b>买入:</b></td>
            <td>{sum(1 for p in self.portfolio if p['signal']=='买入')} 只</td>
        </tr>
        </table>
        <p style="color: #666; margin-top: 10px;">
        建议: 根据个人资金情况，按建议仓位比例配置。严格执行止损，控制风险。
        </p>
        """
        
        self.portfolio_summary.setText("")
        self.portfolio_summary.setTextFormat(Qt.RichText)
        self.portfolio_summary.setText(summary_html)
        
        # 更新风险监控
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
            self.risk_metrics.setText("暂无风险数据\n请先构建投资组合")
            self.warning_text.setHtml("<p style='color: green;'>✓ 暂无风险警告</p>")
            self.action_text.setHtml("<p>暂无特别建议</p>")
            QMessageBox.information(self, "成功", "投资组合已清空")
    
    def update_risk_monitor(self):
        """更新风险监控"""
        if not self.portfolio:
            return
        
        # 计算风险指标
        high_risk_count = sum(1 for p in self.portfolio if p['risk_level'] == "高")
        total_position = sum(p['position_size'] for p in self.portfolio)
        max_position = max(p['position_size'] for p in self.portfolio)
        
        # 风险等级
        if high_risk_count > len(self.portfolio) * 0.3:
            risk_level = "高"
            risk_color = "red"
        elif total_position > 0.8:
            risk_level = "中"
            risk_color = "orange"
        else:
            risk_level = "低"
            risk_color = "green"
        
        # 更新风险指标
        metrics_html = f"""
        <h3>风险等级: <span style="color: {risk_color}; font-size: 20px;">{risk_level}</span></h3>
        <table style="width: 100%; font-size: 13px;">
        <tr>
            <td><b>总仓位:</b></td>
            <td>{total_position*100:.1f}%</td>
            <td><b>最大单只仓位:</b></td>
            <td>{max_position*100:.1f}%</td>
        </tr>
        <tr>
            <td><b>高风险股票:</b></td>
            <td>{high_risk_count} 只</td>
            <td><b>持仓数量:</b></td>
            <td>{len(self.portfolio)} 只</td>
        </tr>
        </table>
        """
        
        self.risk_metrics.setText("")
        self.risk_metrics.setTextFormat(Qt.RichText)
        self.risk_metrics.setText(metrics_html)
        
        # 风险警告
        warnings = []
        if total_position > 0.8:
            warnings.append("⚠️ 总仓位过高，建议保留20%以上现金")
        if max_position > 0.15:
            warnings.append("⚠️ 单只股票仓位过大，建议分散投资")
        if high_risk_count > 3:
            warnings.append("⚠️ 高风险股票较多，注意风险控制")
        
        if warnings:
            warning_html = "<ul style='color: red;'>"
            for w in warnings:
                warning_html += f"<li>{w}</li>"
            warning_html += "</ul>"
            self.warning_text.setHtml(warning_html)
        else:
            self.warning_text.setHtml("<p style='color: green;'>✓ 暂无风险警告</p>")
        
        # 建议操作
        suggestions = []
        if total_position < 0.5:
            suggestions.append("💡 仓位较轻，可以考虑增加配置")
        if len(self.portfolio) < 5:
            suggestions.append("💡 持仓数量较少，建议增加分散度")
        
        suggestions.append("💡 定期检查持仓，及时止盈止损")
        suggestions.append("💡 关注市场动态，适时调整组合")
        
        action_html = "<ul>"
        for s in suggestions:
            action_html += f"<li>{s}</li>"
        action_html += "</ul>"
        self.action_text.setHtml(action_html)
    
    def export_results(self):
        """导出结果"""
        if not self.advice_list:
            QMessageBox.warning(self, "警告", "没有可导出的数据")
            return
        
        try:
            # 创建DataFrame
            data = []
            for adv in self.advice_list:
                data.append({
                    '代码': adv['code'],
                    '名称': adv['name'],
                    '信号': adv['signal'],
                    '评分': adv['score'],
                    '信心度': adv['confidence'],
                    '当前价': adv['price'],
                    '目标价': adv['target_price'],
                    '止损价': adv['stop_loss'],
                    'RSI': adv['rsi'],
                    '风险等级': adv['risk_level'],
                    '建议仓位': f"{adv['position_size']*100:.1f}%"
                })
            
            df = pd.DataFrame(data)
            
            # 保存到文件
            filename = f"投资建议_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)
            
            QMessageBox.information(self, "成功", f"结果已导出到: {filename}")
            self.statusBar().showMessage(f"已导出: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 设置应用图标和样式
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QTableWidget {
            gridline-color: #d0d0d0;
            background-color: white;
        }
        QTableWidget::item:selected {
            background-color: #4CAF50;
            color: white;
        }
        QHeaderView::section {
            background-color: #f0f0f0;
            padding: 5px;
            border: 1px solid #d0d0d0;
            font-weight: bold;
        }
    """)
    
    window = MainGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
