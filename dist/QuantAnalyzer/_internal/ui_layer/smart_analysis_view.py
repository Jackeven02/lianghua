"""
智能市场分析UI组件
提供实时市场分析和投资建议功能
"""

import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, 
                           QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
                           QComboBox, QLineEdit, QGroupBox, QFormLayout, QSplitter,
                           QProgressBar, QStatusBar, QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
import pandas as pd
import numpy as np
import efinance as ef

from strategy_layer import SmartMarketAnalyzer, InvestmentSuggestion

class SmartAnalysisWorker(QThread):
    """智能分析工作线程"""
    analysis_completed = pyqtSignal(list)  # 发送投资建议列表
    progress_updated = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, data, stock_code):
        super().__init__()
        self.data = data
        self.stock_code = stock_code
        
    def run(self):
        try:
            self.progress_updated.emit(20)
            
            # 初始化智能分析器
            analyzer = SmartMarketAnalyzer()
            self.progress_updated.emit(50)
            
            # 生成投资建议
            suggestions = analyzer.generate_investment_suggestions(self.data, self.stock_code)
            self.progress_updated.emit(80)
            
            self.analysis_completed.emit(suggestions)
            self.progress_updated.emit(100)
            
        except Exception as e:
            self.error_occurred.emit(f"分析过程出错: {str(e)}")

class SmartAnalysisView(QWidget):
    """智能分析视图"""
    
    def __init__(self):
        super().__init__()
        self.analyzer = SmartMarketAnalyzer()
        self.current_data = None
        self.analysis_thread = None
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("智能市场分析")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 控制面板
        control_group = QGroupBox("分析控制")
        control_layout = QFormLayout(control_group)
        
        # 股票代码输入
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("输入股票代码，如：000001")
        self.code_input.setText("000001")
        control_layout.addRow("股票代码:", self.code_input)
        
        # 数据周期选择
        self.period_combo = QComboBox()
        self.period_combo.addItems(["日线", "周线", "月线"])
        control_layout.addRow("数据周期:", self.period_combo)
        
        # 分析按钮布局
        button_layout = QHBoxLayout()
        self.analyze_btn = QPushButton("开始智能分析")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.clear_btn = QPushButton("清空结果")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addWidget(self.analyze_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        control_layout.addRow(button_layout)
        
        layout.addWidget(control_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # 结果显示区域
        splitter = QSplitter(Qt.Vertical)
        
        # 市场环境分析
        market_group = QGroupBox("市场环境分析")
        market_layout = QVBoxLayout(market_group)
        
        self.market_info = QTextEdit()
        self.market_info.setPlaceholderText("市场环境分析结果将显示在这里...")
        self.market_info.setMaximumHeight(120)
        market_layout.addWidget(self.market_info)
        
        splitter.addWidget(market_group)
        
        # 投资建议表格
        suggestion_group = QGroupBox("智能投资建议")
        suggestion_layout = QVBoxLayout(suggestion_group)
        
        self.suggestion_table = QTableWidget()
        self.suggestion_table.setColumnCount(8)
        self.suggestion_table.setHorizontalHeaderLabels([
            "股票代码", "操作建议", "置信度", "目标价格", "止损价格", 
            "时间框架", "风险等级", "建议理由"
        ])
        self.suggestion_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        suggestion_layout.addWidget(self.suggestion_table)
        
        splitter.addWidget(suggestion_group)
        
        # 技术指标分析
        indicator_group = QGroupBox("技术指标分析")
        indicator_layout = QVBoxLayout(indicator_group)
        
        self.indicator_info = QTextEdit()
        self.indicator_info.setPlaceholderText("技术指标分析结果将显示在这里...")
        indicator_layout.addWidget(self.indicator_info)
        
        splitter.addWidget(indicator_group)
        
        splitter.setSizes([100, 300, 200])
        layout.addWidget(splitter)
        
        # 状态标签
        self.status_label = QLabel("就绪 - 点击'开始智能分析'按钮进行市场分析")
        layout.addWidget(self.status_label)
        
        # 连接信号
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.clear_btn.clicked.connect(self.clear_results)
        
    def start_analysis(self):
        """开始智能分析"""
        code = self.code_input.text().strip()
        if not code:
            QMessageBox.warning(self, "警告", "请输入股票代码")
            return
        
        self.status_label.setText(f"正在获取 {code} 的数据...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.analyze_btn.setEnabled(False)
        
        try:
            # 获取efinance数据
            self.progress_bar.setValue(10)
            
            period_map = {"日线": 101, "周线": 102, "月线": 103}
            klt = period_map.get(self.period_combo.currentText(), 101)
            
            data = ef.stock.get_quote_history(code, klt=klt)
            
            if data is None or data.empty:
                raise Exception("未获取到数据")
            
            # 数据预处理
            data = data.rename(columns={
                '日期': 'date', '开盘': 'open', '最高': 'high', 
                '最低': 'low', '收盘': 'close', '成交量': 'volume'
            })
            
            data['date'] = pd.to_datetime(data['date'])
            data = data.sort_values('date')
            
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
            
            data = data.dropna()
            
            if len(data) < 50:
                raise Exception("数据量不足，至少需要50个交易日的数据进行分析")
            
            self.current_data = data
            self.progress_bar.setValue(30)
            
            # 启动分析线程
            self.analysis_thread = SmartAnalysisWorker(data, code)
            self.analysis_thread.analysis_completed.connect(self.on_analysis_completed)
            self.analysis_thread.progress_updated.connect(self.progress_bar.setValue)
            self.analysis_thread.error_occurred.connect(self.on_analysis_error)
            self.analysis_thread.finished.connect(self.on_analysis_finished)
            self.analysis_thread.start()
            
        except Exception as e:
            self.on_analysis_error(str(e))
    
    def on_analysis_completed(self, suggestions):
        """分析完成回调"""
        if not suggestions:
            self.market_info.setText("未能生成有效的投资建议，请检查数据质量")
            return
        
        # 显示市场环境分析
        if self.current_data is not None:
            market_condition = self.analyzer.analyze_market_condition(self.current_data)
            current_price = self.current_data['close'].iloc[-1] if len(self.current_data) > 0 else 0
            sma_20 = self.current_data['close'].rolling(20).mean().iloc[-1] if len(self.current_data) >= 20 else current_price
            sma_50 = self.current_data['close'].rolling(50).mean().iloc[-1] if len(self.current_data) >= 50 else current_price
            
            market_text = f"""市场环境: {market_condition}
当前价格: ¥{current_price:.2f}
20日均线: ¥{sma_20:.2f}
50日均线: ¥{sma_50:.2f}
数据周期: {self.period_combo.currentText()}
分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            self.market_info.setText(market_text)
        
        # 显示投资建议
        self.suggestion_table.setRowCount(len(suggestions))
        for row, suggestion in enumerate(suggestions):
            self.suggestion_table.setItem(row, 0, QTableWidgetItem(suggestion.stock_code))
            self.suggestion_table.setItem(row, 1, QTableWidgetItem(suggestion.action.upper()))
            self.suggestion_table.setItem(row, 2, QTableWidgetItem(f"{suggestion.confidence}%"))
            self.suggestion_table.setItem(row, 3, QTableWidgetItem(f"¥{suggestion.price_target:.2f}"))
            self.suggestion_table.setItem(row, 4, QTableWidgetItem(f"¥{suggestion.stop_loss:.2f}"))
            self.suggestion_table.setItem(row, 5, QTableWidgetItem(suggestion.time_frame))
            self.suggestion_table.setItem(row, 6, QTableWidgetItem(suggestion.risk_level))
            self.suggestion_table.setItem(row, 7, QTableWidgetItem(suggestion.recommendation_reason))
        
        # 显示技术指标分析
        if self.current_data is not None:
            rsi = self.analyzer._calculate_rsi(self.current_data, 14).iloc[-1] if len(self.current_data) >= 14 else 50
            macd_line = self._calculate_macd_line(self.current_data) if len(self.current_data) >= 26 else 0
            
            indicator_text = f"""技术指标分析:
RSI(14): {rsi:.2f} ({'超买' if rsi > 70 else '超卖' if rsi < 30 else '中性'})
MACD: {macd_line:.2f}
布林带位置: 待计算
KDJ: 待计算
趋势强度: 待计算"""
            
            self.indicator_info.setText(indicator_text)
        
        self.status_label.setText(f"分析完成 - 生成了 {len(suggestions)} 条投资建议")
    
    def on_analysis_error(self, error_msg):
        """分析错误回调"""
        QMessageBox.critical(self, "分析错误", f"分析过程中出现错误:\n{error_msg}")
        self.status_label.setText(f"分析失败: {error_msg}")
        self.market_info.setText(f"分析失败: {error_msg}")
    
    def on_analysis_finished(self):
        """分析完成清理"""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
    
    def clear_results(self):
        """清空结果"""
        self.market_info.clear()
        self.suggestion_table.setRowCount(0)
        self.indicator_info.clear()
        self.status_label.setText("就绪")
    
    def _calculate_macd_line(self, data):
        """计算MACD线"""
        try:
            ema_fast = data['close'].ewm(span=12).mean()
            ema_slow = data['close'].ewm(span=26).mean()
            macd_line = ema_fast - ema_slow
            return macd_line.iloc[-1]
        except:
            return 0

# 测试函数
def test_smart_analysis_view():
    """测试智能分析视图"""
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = SmartAnalysisView()
    window.show()
    window.resize(1200, 800)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_smart_analysis_view()