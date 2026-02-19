# -*- coding: utf-8 -*-
"""
智能投资顾问系统 - GUI启动程序
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
                             QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QFont
import efinance as ef
import pandas as pd
import numpy as np
from datetime import datetime


class AnalysisWorker(QThread):
    """分析工作线程"""
    progress = pyqtSignal(int, int)  # 当前进度, 总数
    result = pyqtSignal(list)  # 分析结果
    
    def __init__(self, stock_list):
        super().__init__()
        self.stock_list = stock_list
        
    def run(self):
        """执行分析"""
        results = []
        
        for i, (code, name) in enumerate(self.stock_list, 1):
            self.progress.emit(i, len(self.stock_list))
            
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
            
            df['SMA_5'] = df['close'].rolling(window=5).mean()
            df['SMA_20'] = df['close'].rolling(window=20).mean()
            df['SMA_60'] = df['close'].rolling(window=60).mean()
            
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            latest = df.iloc[-1]
            current_price = latest['close']
            
            score = 0
            reasons = []
            
            if latest['SMA_5'] > latest['SMA_20'] > latest['SMA_60']:
                score += 30
                reasons.append("均线多头排列")
            elif latest['SMA_5'] > latest['SMA_20']:
                score += 20
                reasons.append("短期均线向上")
            
            if 30 < latest['RSI'] < 70:
                score += 20
                reasons.append("RSI健康")
            elif latest['RSI'] < 30:
                score += 15
                reasons.append("RSI超卖")
            
            if current_price > latest['SMA_20']:
                score += 15
                reasons.append("价格在均线上方")
            
            recent_vol = df['volume'].iloc[-5:].mean()
            avg_vol = df['volume'].mean()
            if recent_vol > avg_vol * 1.2:
                score += 10
                reasons.append("成交量放大")
            
            returns_5d = (df['close'].iloc[-1] / df['close'].iloc[-5] - 1) * 100
            if returns_5d > 3:
                score += 10
                reasons.append("短期上涨")
            
            if score >= 60:
                signal = "强烈买入"
            elif score >= 50:
                signal = "买入"
            elif score >= 40:
                signal = "持有"
            else:
                signal = "观望"
            
            target_price = current_price * 1.15
            stop_loss = current_price * 0.92
            
            return {
                'code': stock_code,
                'name': stock_name,
                'price': current_price,
                'signal': signal,
                'score': score,
                'confidence': min(score, 100),
                'rsi': latest['RSI'],
                'target_price': target_price,
                'stop_loss': stop_loss,
                'reasons': reasons
            }
            
        except Exception as e:
            return None


class SmartAdvisorGUI(QMainWindow):
    """智能投资顾问GUI"""
    
    def __init__(self):
        super().__init__()
        self.advice_list = []
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("智能投资顾问系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("智能投资顾问系统")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 控制面板
        control_group = QGroupBox("扫描设置")
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("扫描数量:"))
        self.stock_count_spin = QSpinBox()
        self.stock_count_spin.setRange(5, 20)
        self.stock_count_spin.setValue(10)
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
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.scan_btn.clicked.connect(self.start_scan)
        control_layout.addWidget(self.scan_btn)
        
        control_layout.addStretch()
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 统计信息
        self.stats_label = QLabel("等待扫描...")
        layout.addWidget(self.stats_label)
        
        # 结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(9)
        self.result_table.setHorizontalHeaderLabels([
            "代码", "名称", "信号", "评分", "信心度", "当前价", "目标价", "止损价", "RSI"
        ])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.itemSelectionChanged.connect(self.show_detail)
        layout.addWidget(self.result_table)
        
        # 详细信息
        detail_group = QGroupBox("详细分析")
        detail_layout = QVBoxLayout()
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(150)
        detail_layout.addWidget(self.detail_text)
        detail_group.setLayout(detail_layout)
        layout.addWidget(detail_group)
        
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
            ("600030", "中信证券"), ("601166", "兴业银行")
        ][:count]
        
        # 禁用按钮
        self.scan_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(stock_list))
        self.progress_bar.setValue(0)
        
        # 创建工作线程
        self.worker = AnalysisWorker(stock_list)
        self.worker.progress.connect(self.update_progress)
        self.worker.result.connect(self.show_results)
        self.worker.start()
        
    def update_progress(self, current, total):
        """更新进度"""
        self.progress_bar.setValue(current)
        self.stats_label.setText(f"正在分析... {current}/{total}")
        
    def show_results(self, results):
        """显示结果"""
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
            self.result_table.setItem(row, 2, signal_item)
            
            score_item = QTableWidgetItem(f"{result['score']}")
            if result['score'] >= 60:
                score_item.setBackground(QColor("#4CAF50"))
                score_item.setForeground(QColor("white"))
            self.result_table.setItem(row, 3, score_item)
            
            self.result_table.setItem(row, 4, QTableWidgetItem(f"{result['confidence']}%"))
            self.result_table.setItem(row, 5, QTableWidgetItem(f"¥{result['price']:.2f}"))
            self.result_table.setItem(row, 6, QTableWidgetItem(f"¥{result['target_price']:.2f}"))
            self.result_table.setItem(row, 7, QTableWidgetItem(f"¥{result['stop_loss']:.2f}"))
            self.result_table.setItem(row, 8, QTableWidgetItem(f"{result['rsi']:.1f}"))
        
        # 更新统计
        buy_count = sum(1 for r in results if "买入" in r['signal'])
        avg_score = sum(r['score'] for r in results) / len(results) if results else 0
        
        self.stats_label.setText(
            f"找到 {len(results)} 个投资机会 | "
            f"平均评分: {avg_score:.1f} | "
            f"买入信号: {buy_count}"
        )
        
        # 恢复按钮
        self.scan_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
    def show_detail(self):
        """显示详细信息"""
        selected = self.result_table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        if row >= len(self.advice_list):
            return
        
        advice = self.advice_list[row]
        
        detail_html = f"""
        <h3>{advice['name']} ({advice['code']})</h3>
        <p><b>投资信号:</b> <span style="color: {'green' if '买入' in advice['signal'] else 'orange'}; font-size: 16px;">
        {advice['signal']}</span> (信心度: {advice['confidence']}%)</p>
        
        <p><b>价格信息:</b><br>
        当前价: ¥{advice['price']:.2f} | 
        目标价: ¥{advice['target_price']:.2f} ({(advice['target_price']/advice['price']-1)*100:+.1f}%) | 
        止损价: ¥{advice['stop_loss']:.2f} ({(advice['stop_loss']/advice['price']-1)*100:+.1f}%)</p>
        
        <p><b>技术指标:</b><br>
        评分: {advice['score']}/100 | RSI: {advice['rsi']:.1f}</p>
        
        <p><b>理由分析:</b></p>
        <ul>
        {''.join(f'<li>{reason}</li>' for reason in advice['reasons'])}
        </ul>
        """
        
        self.detail_text.setHtml(detail_html)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = SmartAdvisorGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
