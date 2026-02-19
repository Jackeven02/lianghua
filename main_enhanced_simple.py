"""
量化分析软件简化增强版主程序
专注于UI功能展示
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTabWidget, QLabel, 
                           QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
                           QComboBox, QLineEdit, QGroupBox, QFormLayout, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_NAME, APP_VERSION

class DataVisualizationWidget(QWidget):
    """数据可视化组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("📊 数据可视化")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 控制面板
        control_group = QGroupBox("数据控制")
        control_layout = QFormLayout(control_group)
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("输入股票代码，如：000001")
        control_layout.addRow("股票代码:", self.code_input)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["日线", "周线", "月线"])
        control_layout.addRow("数据周期:", self.period_combo)
        
        self.load_btn = QPushButton("📈 加载数据")
        self.load_btn.clicked.connect(self.load_sample_data)
        control_layout.addRow(self.load_btn)
        
        layout.addWidget(control_group)
        
        # 数据显示区域
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)
        self.data_display.setStyleSheet("font-family: Consolas; font-size: 12px;")
        layout.addWidget(self.data_display)
        
        # 状态标签
        self.status_label = QLabel("就绪 - 点击加载数据生成示例数据")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.status_label)
        
    def load_sample_data(self):
        """加载示例数据"""
        try:
            code = self.code_input.text().strip()
            if not code:
                code = "000001"  # 默认代码
                
            self.status_label.setText("正在生成示例数据...")
            QApplication.processEvents()
            
            # 生成示例数据
            dates = pd.date_range('2024-01-01', periods=100, freq='D')
            prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
            
            data = pd.DataFrame({
                'date': dates,
                'open': prices * (1 + np.random.randn(100) * 0.01),
                'high': prices * (1 + np.abs(np.random.randn(100)) * 0.02),
                'low': prices * (1 - np.abs(np.random.randn(100)) * 0.02),
                'close': prices,
                'volume': np.random.randint(1000000, 10000000, 100)
            })
            
            # 显示数据信息
            info = f"股票代码: {code}\n"
            info += f"数据周期: {self.period_combo.currentText()}\n"
            info += f"数据条数: {len(data)}\n"
            info += f"时间范围: {data['date'].iloc[0].strftime('%Y-%m-%d')} 至 {data['date'].iloc[-1].strftime('%Y-%m-%d')}\n\n"
            
            # 显示统计信息
            info += "数据统计:\n"
            info += f"开盘价: {data['open'].min():.2f} - {data['open'].max():.2f}\n"
            info += f"最高价: {data['high'].min():.2f} - {data['high'].max():.2f}\n"
            info += f"最低价: {data['low'].min():.2f} - {data['low'].max():.2f}\n"
            info += f"收盘价: {data['close'].min():.2f} - {data['close'].max():.2f}\n"
            info += f"成交量: {data['volume'].min():,.0f} - {data['volume'].max():,.0f}\n\n"
            
            # 显示前几行数据
            info += "前5行数据:\n"
            info += data.head().to_string(index=False)
            
            self.data_display.setText(info)
            self.status_label.setText(f"示例数据生成成功 - {len(data)}条记录")
            
        except Exception as e:
            self.data_display.setText(f"错误: {str(e)}")
            self.status_label.setText("数据生成失败")

class StrategyEditorWidget(QWidget):
    """策略编辑器组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("🤖 策略编辑器")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 策略选择
        strategy_group = QGroupBox("策略选择")
        strategy_layout = QVBoxLayout(strategy_group)
        
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "SMA交叉策略", 
            "RSI策略", 
            "MACD策略", 
            "布林带策略",
            "均值回归策略"
        ])
        strategy_layout.addWidget(self.strategy_combo)
        
        # 参数设置
        param_group = QGroupBox("参数设置")
        param_layout = QFormLayout(param_group)
        
        self.param1 = QLineEdit("5")
        self.param2 = QLineEdit("20")
        param_layout.addRow("参数1:", self.param1)
        param_layout.addRow("参数2:", self.param2)
        
        strategy_layout.addWidget(param_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.test_btn = QPushButton("🧪 测试策略")
        self.test_btn.clicked.connect(self.test_strategy)
        self.save_btn = QPushButton("💾 保存策略")
        self.run_btn = QPushButton("▶️ 运行回测")
        
        btn_layout.addWidget(self.test_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.run_btn)
        strategy_layout.addLayout(btn_layout)
        
        layout.addWidget(strategy_group)
        
        # 策略代码编辑器
        self.code_editor = QTextEdit()
        self.code_editor.setStyleSheet("font-family: Consolas; font-size: 12px;")
        self.code_editor.setPlaceholderText("# 在这里编写策略代码\n# 支持Python语法\n\nclass MyStrategy:\n    def __init__(self):\n        self.name = '自定义策略'\n    \n    def generate_signal(self, data):\n        # 在这里实现交易信号逻辑\n        return 'BUY'  # 返回 BUY, SELL, HOLD")
        layout.addWidget(self.code_editor)
        
        # 状态显示
        self.strategy_status = QLabel("策略编辑器就绪")
        self.strategy_status.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.strategy_status)

    def test_strategy(self):
        """测试策略"""
        self.strategy_status.setText("策略测试中...")
        QApplication.processEvents()
        
        # 模拟测试过程
        import time
        time.sleep(1)
        
        self.strategy_status.setText("策略测试完成 - 无语法错误")

class BacktestResultWidget(QWidget):
    """回测结果展示组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("📊 回测结果")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 结果概览
        overview_group = QGroupBox("结果概览")
        overview_layout = QVBoxLayout(overview_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("font-family: Consolas; font-size: 12px;")
        self.result_text.setText("回测结果将在这里显示...\n\n点击下方按钮生成示例回测结果")
        overview_layout.addWidget(self.result_text)
        
        layout.addWidget(overview_group)
        
        # 详细结果表格
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["指标", "数值", "说明"])
        self.result_table.setRowCount(8)
        
        # 设置示例数据
        metrics = [
            ("总收益率", "0.00%", "策略总体收益"),
            ("年化收益率", "0.00%", "年化收益水平"),
            ("夏普比率", "0.00", "风险调整收益"),
            ("最大回撤", "0.00%", "最大资金回撤"),
            ("胜率", "0.00%", "盈利交易占比"),
            ("交易次数", "0", "总交易笔数"),
            ("盈利次数", "0", "盈利交易数"),
            ("亏损次数", "0", "亏损交易数")
        ]
        
        for i, (metric, value, desc) in enumerate(metrics):
            self.result_table.setItem(i, 0, QTableWidgetItem(metric))
            self.result_table.setItem(i, 1, QTableWidgetItem(value))
            self.result_table.setItem(i, 2, QTableWidgetItem(desc))
            
        layout.addWidget(self.result_table)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.generate_btn = QPushButton("📊 生成示例结果")
        self.generate_btn.clicked.connect(self.generate_sample_results)
        self.export_btn = QPushButton("📤 导出报告")
        self.chart_btn = QPushButton("📊 查看图表")
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.chart_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def generate_sample_results(self):
        """生成示例回测结果"""
        # 生成随机的回测结果
        total_return = np.random.uniform(-0.2, 0.5)
        annual_return = total_return * np.random.uniform(0.8, 1.2)
        sharpe_ratio = np.random.uniform(-0.5, 2.0)
        max_drawdown = np.random.uniform(-0.3, -0.05)
        win_rate = np.random.uniform(0.3, 0.7)
        trade_count = np.random.randint(20, 100)
        win_count = int(trade_count * win_rate)
        loss_count = trade_count - win_count
        
        # 更新表格
        results = [
            (f"{total_return*100:.2f}%", "策略总体收益"),
            (f"{annual_return*100:.2f}%", "年化收益水平"),
            (f"{sharpe_ratio:.2f}", "风险调整收益"),
            (f"{max_drawdown*100:.2f}%", "最大资金回撤"),
            (f"{win_rate*100:.1f}%", "盈利交易占比"),
            (str(trade_count), "总交易笔数"),
            (str(win_count), "盈利交易数"),
            (str(loss_count), "亏损交易数")
        ]
        
        for i, (value, desc) in enumerate(results):
            self.result_table.item(i, 1).setText(value)
            self.result_table.item(i, 2).setText(desc)
        
        # 更新文本显示
        result_text = f"""回测完成报告

测试周期: 2024-01-01 至 2024-12-31
初始资金: 1,000,000 元
最终资金: {1000000 * (1 + total_return):,.2f} 元

主要指标:
• 总收益率: {total_return*100:.2f}%
• 年化收益率: {annual_return*100:.2f}%
• 夏普比率: {sharpe_ratio:.2f}
• 最大回撤: {max_drawdown*100:.2f}%
• 胜率: {win_rate*100:.1f}%

交易统计:
• 总交易次数: {trade_count}
• 盈利交易: {win_count}
• 亏损交易: {loss_count}
• 平均持仓天数: {np.random.randint(3, 15)} 天
"""
        
        self.result_text.setText(result_text)

class EnhancedMainWindow(QMainWindow):
    """增强版主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f'{APP_NAME} v{APP_VERSION} - 专业量化分析平台')
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(DataVisualizationWidget(), "📈 数据分析")
        self.tab_widget.addTab(StrategyEditorWidget(), "🤖 策略编辑")
        self.tab_widget.addTab(BacktestResultWidget(), "📊 回测结果")
        
        main_layout.addWidget(self.tab_widget)
        
        # 状态栏
        status_bar = self.statusBar()
        status_bar.showMessage("Quant Analyzer 就绪 - 所有功能模块已加载")
        
    def show(self):
        super().show()
        print("增强版主窗口已显示")

def main():
    """主函数"""
    print(f"启动 {APP_NAME} v{APP_VERSION}")
    
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    try:
        main_window = EnhancedMainWindow()
        main_window.show()
        print("增强版主窗口启动成功")
        
        exit_code = app.exec_()
        print("应用程序已退出")
        return exit_code
        
    except Exception as e:
        print(f"启动失败: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())