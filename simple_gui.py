"""
简化版智能投资顾问GUI
整合所有功能到一个简洁的界面
"""
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                           QTableWidget, QTableWidgetItem, QComboBox, 
                           QLineEdit, QGroupBox, QFormLayout, QSplitter,
                           QProgressBar, QStatusBar, QMessageBox, QHeaderView,
                           QFrame)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
import pandas as pd
import numpy as np
import efinance as ef

from strategy_layer.smart_advisor import SmartAdvisor, MarketScanner
from strategy_layer.smart_strategy_engine import SmartMarketAnalyzer
from analysis_layer.technical_indicators import TechnicalIndicators


class AnalysisWorker(QThread):
    """分析工作线程"""
    analysis_completed = pyqtSignal(object)  # 发送分析结果
    progress_updated = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, data, stock_code, stock_name, analysis_type):
        super().__init__()
        self.data = data
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.analysis_type = analysis_type
        
    def run(self):
        try:
            self.progress_updated.emit(20)
            
            if self.analysis_type == "single":
                # 单股分析
                advisor = SmartAdvisor()
                self.progress_updated.emit(50)
                
                # 获取基本面数据（如果有的话）
                fundamental_data = self.get_fundamental_data(self.stock_code)
                self.progress_updated.emit(70)
                
                # 分析股票
                advice = advisor.analyze_stock(
                    self.stock_code, 
                    self.stock_name, 
                    self.data, 
                    fundamental_data
                )
                self.progress_updated.emit(90)
                
                self.analysis_completed.emit(advice)
                
            elif self.analysis_type == "scan":
                # 市场扫描
                advisor = SmartAdvisor()
                scanner = MarketScanner(advisor)
                self.progress_updated.emit(50)
                
                # 使用热门股票列表进行扫描
                hot_stocks = [
                    ("600519", "贵州茅台"),
                    ("000858", "五粮液"),
                    ("600036", "招商银行"),
                    ("601318", "中国平安"),
                    ("000333", "美的集团"),
                    ("600276", "恒瑞医药"),
                    ("000651", "格力电器"),
                    ("601888", "中国中免"),
                    ("300750", "宁德时代"),
                    ("002475", "立讯精密")
                ]
                
                # 为每只股票获取数据
                stock_data_list = []
                for i, (code, name) in enumerate(hot_stocks):
                    try:
                        stock_data = ef.stock.get_quote_history(code)
                        if stock_data is not None and not stock_data.empty and len(stock_data) >= 60:
                            stock_data = stock_data.rename(columns={
                                '日期': 'date', '开盘': 'open', '最高': 'high', 
                                '最低': 'low', '收盘': 'close', '成交量': 'volume'
                            })
                            stock_data['date'] = pd.to_datetime(stock_data['date'])
                            stock_data = stock_data.sort_values('date')
                            
                            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
                            for col in numeric_cols:
                                if col in stock_data.columns:
                                    stock_data[col] = pd.to_numeric(stock_data[col], errors='coerce')
                            
                            stock_data = stock_data.dropna()
                            
                            if len(stock_data) >= 60:
                                # 计算技术指标
                                stock_data = TechnicalIndicators.calculate_all_indicators(stock_data)
                                stock_data_list.append((code, name, stock_data))
                        
                        # 更新进度
                        progress = 50 + int((i + 1) / len(hot_stocks) * 40)
                        self.progress_updated.emit(progress)
                        
                    except Exception:
                        continue
                
                self.progress_updated.emit(90)
                
                # 执行扫描
                advice_list = []
                for code, name, data in stock_data_list:
                    try:
                        fundamental_data = self.get_fundamental_data(code)
                        advice = advisor.analyze_stock(code, name, data, fundamental_data)
                        if advice and advice.confidence >= 40:  # 只保留信心度大于40的建议
                            advice_list.append(advice)
                    except Exception:
                        continue
                
                self.analysis_completed.emit(advice_list)
                
            self.progress_updated.emit(100)
            
        except Exception as e:
            self.error_occurred.emit(f"分析过程出错: {str(e)}")
    
    def get_fundamental_data(self, stock_code):
        """获取基本面数据（简化版）"""
        try:
            # 这里可以添加从efinance获取基本面数据的逻辑
            # 暂时返回默认值
            return {
                'roe': 15.0,  # 净资产收益率
                'revenue_growth': 10.0,  # 营收增长率
                'profit_growth': 12.0,  # 利润增长率
                'pe_ratio': 20.0,  # 市盈率
                'pb_ratio': 2.5,  # 市净率
                'debt_ratio': 0.4,  # 资产负债率
                'current_ratio': 1.8  # 流动比率
            }
        except:
            return {
                'roe': 10.0,
                'revenue_growth': 5.0,
                'profit_growth': 5.0,
                'pe_ratio': 20.0,
                'pb_ratio': 2.0,
                'debt_ratio': 0.5,
                'current_ratio': 1.5
            }


class SimpleQuantAnalyzerGUI(QMainWindow):
    """简化版量化分析GUI"""
    
    def __init__(self):
        super().__init__()
        self.current_data = None
        self.analysis_thread = None
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('智能投资顾问 - 简化版')
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title_label = QLabel('智能投资顾问系统')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            margin: 15px; 
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        """)
        main_layout.addWidget(title_label)
        
        # 控制面板
        control_group = QGroupBox("分析控制")
        control_layout = QFormLayout(control_group)
        
        # 股票代码输入
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("输入股票代码，如：600519 或 000001")
        self.code_input.setText("600519")  # 默认贵州茅台
        control_layout.addRow("股票代码:", self.code_input)
        
        # 股票名称输入
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入股票名称，如：贵州茅台")
        self.name_input.setText("贵州茅台")  # 默认名称
        control_layout.addRow("股票名称:", self.name_input)
        
        # 分析类型选择
        self.type_combo = QComboBox()
        self.type_combo.addItems(["单股分析", "市场扫描"])
        control_layout.addRow("分析类型:", self.type_combo)
        
        # 数据周期选择
        self.period_combo = QComboBox()
        self.period_combo.addItems(["日线", "周线", "月线"])
        control_layout.addRow("数据周期:", self.period_combo)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        self.analyze_btn = QPushButton("开始分析")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
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
        self.clear_btn = QPushButton("清空结果")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addWidget(self.analyze_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        control_layout.addRow(button_layout)
        
        main_layout.addWidget(control_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        main_layout.addWidget(self.progress_bar)
        
        # 结果显示区域 - 使用分割器
        splitter = QSplitter(Qt.Vertical)
        
        # 上半部分：基本分析结果
        top_group = QGroupBox("分析结果")
        top_layout = QVBoxLayout(top_group)
        
        # 基本信息显示
        self.basic_info = QTextEdit()
        self.basic_info.setPlaceholderText("分析结果将显示在这里...")
        self.basic_info.setMaximumHeight(150)
        self.basic_info.setFont(QFont("Consolas", 10))
        top_layout.addWidget(self.basic_info)
        
        splitter.addWidget(top_group)
        
        # 中间部分：详细分析
        middle_group = QGroupBox("详细分析")
        middle_layout = QVBoxLayout(middle_group)
        
        # 详细分析文本框
        self.detailed_analysis = QTextEdit()
        self.detailed_analysis.setPlaceholderText("详细分析将显示在这里...")
        self.detailed_analysis.setFont(QFont("Consolas", 10))
        middle_layout.addWidget(self.detailed_analysis)
        
        splitter.addWidget(middle_group)
        
        # 下半部分：投资建议表格
        bottom_group = QGroupBox("投资建议")
        bottom_layout = QVBoxLayout(bottom_group)
        
        self.advice_table = QTableWidget()
        self.advice_table.setColumnCount(9)
        self.advice_table.setHorizontalHeaderLabels([
            "股票代码", "股票名称", "操作建议", "置信度", "当前价格", 
            "目标价格", "止损价格", "评分", "建议理由"
        ])
        header = self.advice_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # 允许手动调整列宽
        bottom_layout.addWidget(self.advice_table)
        
        splitter.addWidget(bottom_group)
        
        # 设置分割器比例
        splitter.setSizes([150, 300, 250])
        main_layout.addWidget(splitter)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 - 请输入股票代码并点击'开始分析'")
        
        # 连接信号
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.clear_btn.clicked.connect(self.clear_results)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QComboBox, QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 5px;
            }
            QTableWidget {
                border: 1px solid #bdc3c7;
                gridline-color: #bdc3c7;
            }
        """)
    
    def start_analysis(self):
        """开始分析"""
        code = self.code_input.text().strip()
        name = self.name_input.text().strip()
        analysis_type = self.type_combo.currentText()
        
        if not code:
            QMessageBox.warning(self, "警告", "请输入股票代码")
            return
            
        if not name:
            QMessageBox.warning(self, "警告", "请输入股票名称")
            return
        
        # 更新状态
        if analysis_type == "单股分析":
            self.status_bar.showMessage(f"正在获取 {name}({code}) 的数据...")
        else:
            self.status_bar.showMessage("正在进行市场扫描...")
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.analyze_btn.setEnabled(False)
        
        try:
            # 根据分析类型决定获取数据的方式
            if analysis_type == "单股分析":
                # 获取单只股票数据
                period_map = {"日线": 101, "周线": 102, "月线": 103}
                klt = period_map.get(self.period_combo.currentText(), 101)
                
                data = ef.stock.get_quote_history(code, klt=klt)
                
                if data is None or data.empty:
                    raise Exception("未获取到数据")
                
                # 数据预处理
                data = data.rename(columns={
                    '日期': 'date', '开盘': 'open', '最高': 'high', 
                    '最低': 'low', '收盘': 'close', '成交量': 'volume',
                    '成交额': 'amount', '涨跌幅': 'change_pct', '涨跌额': 'change'
                })
                
                data['date'] = pd.to_datetime(data['date'])
                data = data.sort_values('date')
                
                numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'change_pct', 'change']
                for col in numeric_cols:
                    if col in data.columns:
                        data[col] = pd.to_numeric(data[col], errors='coerce')
                
                data = data.dropna()
                
                if len(data) < 60:
                    raise Exception("数据量不足，至少需要60个交易日的数据进行分析")
                
                # 计算技术指标
                data = TechnicalIndicators.calculate_all_indicators(data)
                
                self.current_data = data
                
                # 启动分析线程
                self.analysis_thread = AnalysisWorker(data, code, name, "single")
                
            else:  # 市场扫描
                # 对于市场扫描，我们传递空数据，实际获取将在工作线程中完成
                self.current_data = None
                dummy_data = pd.DataFrame()
                self.analysis_thread = AnalysisWorker(dummy_data, code, name, "scan")
            
            # 连接信号
            self.analysis_thread.analysis_completed.connect(self.on_analysis_completed)
            self.analysis_thread.progress_updated.connect(self.progress_bar.setValue)
            self.analysis_thread.error_occurred.connect(self.on_analysis_error)
            self.analysis_thread.finished.connect(self.on_analysis_finished)
            
            # 启动线程
            self.analysis_thread.start()
            
        except Exception as e:
            self.on_analysis_error(str(e))
    
    def on_analysis_completed(self, result):
        """分析完成回调"""
        try:
            analysis_type = self.type_combo.currentText()
            
            if analysis_type == "单股分析":
                # 单股分析结果
                if result is None:
                    self.basic_info.setText("未能完成分析，请检查数据或重试")
                    return
                
                # 显示基本分析结果
                basic_text = f"""股票: {result.stock_name} ({result.stock_code})
当前价格: ¥{result.current_price:.2f}
分析日期: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

技术指标:
  SMA5:  ¥{getattr(result, 'technical_score', 0):.2f} (简化显示)
  信号: {result.signal.value}
  信心度: {result.confidence:.1f}%
  评分: {result.overall_score:.1f}/100"""
                
                self.basic_info.setText(basic_text)
                
                # 显示详细分析
                detailed_text = f"""详细分析:
投资建议: {result.signal.value}
信心度: {result.confidence:.1f}%
风险等级: {result.risk_level}
建议仓位: {result.position_size*100:.1f}%

价格建议:
  目标价: ¥{result.target_price:.2f} ({(result.target_price/result.current_price-1)*100:+.2f}%)
  止损价: ¥{result.stop_loss:.2f} ({(result.stop_loss/result.current_price-1)*100:+.2f}%)

技术评分: {result.technical_score:.1f}
基本面评分: {result.fundamental_score:.1f}
情绪面评分: {result.sentiment_score:.1f}

建议理由:
"""
                for i, reason in enumerate(result.reasons, 1):
                    detailed_text += f"  {i}. {reason}\n"
                
                self.detailed_analysis.setText(detailed_text)
                
                # 清空表格并添加结果
                self.advice_table.setRowCount(1)
                self.advice_table.setItem(0, 0, QTableWidgetItem(result.stock_code))
                self.advice_table.setItem(0, 1, QTableWidgetItem(result.stock_name))
                self.advice_table.setItem(0, 2, QTableWidgetItem(result.signal.value))
                self.advice_table.setItem(0, 3, QTableWidgetItem(f"{result.confidence:.1f}%"))
                self.advice_table.setItem(0, 4, QTableWidgetItem(f"¥{result.current_price:.2f}"))
                self.advice_table.setItem(0, 5, QTableWidgetItem(f"¥{result.target_price:.2f}"))
                self.advice_table.setItem(0, 6, QTableWidgetItem(f"¥{result.stop_loss:.2f}"))
                self.advice_table.setItem(0, 7, QTableWidgetItem(f"{result.overall_score:.1f}"))
                self.advice_table.setItem(0, 8, QTableWidgetItem("; ".join(result.reasons)))
                
                # 根据信号设置颜色
                signal_item = self.advice_table.item(0, 2)
                if "买入" in result.signal.value:
                    signal_item.setBackground(Qt.green)
                    signal_item.setForeground(Qt.black)
                elif "卖出" in result.signal.value:
                    signal_item.setBackground(Qt.red)
                    signal_item.setForeground(Qt.white)
                elif "持有" in result.signal.value:
                    signal_item.setBackground(Qt.yellow)
                    signal_item.setForeground(Qt.black)
                
                self.status_bar.showMessage(f"单股分析完成 - {result.stock_name}: {result.signal.value}")
                
            else:  # 市场扫描
                # 市场扫描结果
                if not result:
                    self.basic_info.setText("市场扫描未找到符合条件的投资机会")
                    return
                
                # 显示基本扫描结果
                top_picks = sorted(result, key=lambda x: x.overall_score, reverse=True)[:10]
                
                basic_text = f"""市场扫描结果:
扫描时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
发现 {len(result)} 个投资机会
显示前10个最佳机会"""
                
                self.basic_info.setText(basic_text)
                
                # 显示详细分析
                detailed_text = f"""市场扫描详情:
共分析了 {len(result)} 只股票
按综合评分排序显示前10只:
"""
                for i, advice in enumerate(top_picks[:5], 1):
                    detailed_text += f"  {i}. {advice.stock_name}: {advice.signal.value} (评分: {advice.overall_score:.1f})\n"
                
                self.detailed_analysis.setText(detailed_text)
                
                # 在表格中显示结果
                self.advice_table.setRowCount(len(top_picks))
                for row, advice in enumerate(top_picks):
                    self.advice_table.setItem(row, 0, QTableWidgetItem(advice.stock_code))
                    self.advice_table.setItem(row, 1, QTableWidgetItem(advice.stock_name))
                    self.advice_table.setItem(row, 2, QTableWidgetItem(advice.signal.value))
                    self.advice_table.setItem(row, 3, QTableWidgetItem(f"{advice.confidence:.1f}%"))
                    self.advice_table.setItem(row, 4, QTableWidgetItem(f"¥{advice.current_price:.2f}"))
                    self.advice_table.setItem(row, 5, QTableWidgetItem(f"¥{advice.target_price:.2f}"))
                    self.advice_table.setItem(row, 6, QTableWidgetItem(f"¥{advice.stop_loss:.2f}"))
                    self.advice_table.setItem(row, 7, QTableWidgetItem(f"{advice.overall_score:.1f}"))
                    self.advice_table.setItem(row, 8, QTableWidgetItem(advice.reasons[0] if advice.reasons else "待分析"))
                    
                    # 根据信号设置颜色
                    signal_item = self.advice_table.item(row, 2)
                    if "买入" in advice.signal.value:
                        signal_item.setBackground(Qt.green)
                        signal_item.setForeground(Qt.black)
                    elif "卖出" in advice.signal.value:
                        signal_item.setBackground(Qt.red)
                        signal_item.setForeground(Qt.white)
                    elif "持有" in advice.signal.value:
                        signal_item.setBackground(Qt.yellow)
                        signal_item.setForeground(Qt.black)
                
                self.status_bar.showMessage(f"市场扫描完成 - 找到 {len(result)} 个投资机会")
                
        except Exception as e:
            self.on_analysis_error(f"显示结果时出错: {str(e)}")
    
    def on_analysis_error(self, error_msg):
        """分析错误回调"""
        QMessageBox.critical(self, "分析错误", f"分析过程中出现错误:\n{error_msg}")
        self.status_bar.showMessage(f"分析失败: {error_msg}")
        self.basic_info.setText(f"分析失败: {error_msg}")
        
    def on_analysis_finished(self):
        """分析完成清理"""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
    
    def clear_results(self):
        """清空结果"""
        self.basic_info.clear()
        self.detailed_analysis.clear()
        self.advice_table.setRowCount(0)
        self.status_bar.showMessage("结果已清空")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 风格以获得更好的外观
    
    window = SimpleQuantAnalyzerGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()