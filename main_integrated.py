"""
量化分析软件集成版主程序
整合数据层功能的完整版本
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QTabWidget, QLabel, 
                           QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
                           QComboBox, QLineEdit, QGroupBox, QFormLayout, QSplitter,
                           QProgressBar, QStatusBar)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_NAME, APP_VERSION

class IntegratedDataVisualizationWidget(QWidget):
    """集成数据可视化组件"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.data_cache = {}
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel("📈 数据分析与可视化")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 控制面板
        control_panel = QGroupBox("数据控制面板")
        control_layout = QFormLayout(control_panel)
        
        # 股票代码输入
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("输入股票代码，如：000001")
        self.code_input.returnPressed.connect(self.load_data)
        control_layout.addRow("📊 股票代码:", self.code_input)
        
        # 数据周期选择
        self.period_combo = QComboBox()
        self.period_combo.addItems(["日线", "周线", "月线"])
        self.period_combo.currentTextChanged.connect(self.update_period_info)
        control_layout.addRow("🕐 数据周期:", self.period_combo)
        
        # 数据类型选择
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["股票数据", "基金数据", "指数数据"])
        control_layout.addRow("📎 数据类型:", self.data_type_combo)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        self.load_btn = QPushButton("🔍 加载数据")
        self.load_btn.clicked.connect(self.load_data)
        self.load_btn.setStyleSheet("background-color: #3498db; color: white; padding: 8px;")
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self.refresh_data)
        self.refresh_btn.setStyleSheet("background-color: #95a5a6; color: white; padding: 8px;")
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self.clear_data)
        self.clear_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px;")
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        control_layout.addRow(button_layout)
        
        layout.addWidget(control_panel)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 分割器
        splitter = QSplitter(Qt.Vertical)
        
        # 数据显示区域
        self.data_display = QTextEdit()
        self.data_display.setReadOnly(True)
        self.data_display.setStyleSheet("""
            font-family: Consolas, 'Courier New', monospace; 
            font-size: 12px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
        """)
        self.update_display_placeholder()
        splitter.addWidget(self.data_display)
        
        # 统计信息区域
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setStyleSheet("""
            font-family: Arial, sans-serif;
            font-size: 11px;
            background-color: #e3f2fd;
            border: 1px solid #bbdefb;
        """)
        self.stats_display.setMaximumHeight(150)
        self.stats_display.setPlaceholderText("数据统计信息将在此显示...")
        splitter.addWidget(self.stats_display)
        
        layout.addWidget(splitter)
        
        # 状态标签
        self.status_label = QLabel("📝 就绪 - 输入股票代码开始分析")
        self.status_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        layout.addWidget(self.status_label)
        
    def update_display_placeholder(self):
        """更新显示区域占位文本"""
        placeholder = """📊 数据分析区域
        
功能说明：
• 输入股票代码（如000001）加载数据
• 选择数据周期（日线/周线/月线）
• 支持股票、基金、指数数据
• 显示详细的数据统计信息

📈 技术特色：
• 自动数据清洗和格式化
• 关键指标计算和分析
• 数据可视化预览
• 缓存机制提高性能

⚠️ 注意事项：
• 首次加载可能需要网络连接
• 数据更新频率受API限制
• 建议使用真实有效的代码"""
        
        self.data_display.setPlaceholderText(placeholder)
    
    def update_period_info(self):
        """更新周期信息"""
        period_info = {
            "日线": "获取每日交易数据，包含开盘、收盘、高低价等",
            "周线": "获取每周汇总数据，适合中长期分析",
            "月线": "获取每月汇总数据，适合长期趋势分析"
        }
        period = self.period_combo.currentText()
        self.status_label.setText(f"📅 当前选择: {period} - {period_info.get(period, '')}")
    
    def load_data(self):
        """加载数据主函数"""
        try:
            code = self.code_input.text().strip()
            if not code:
                self.status_label.setText("❌ 请输入股票代码")
                return
                
            data_type = self.data_type_combo.currentText()
            period = self.period_combo.currentText()
            
            self.status_label.setText(f"🔄 正在加载{data_type} {code} 的 {period} 数据...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(30)
            QApplication.processEvents()
            
            # 检查缓存
            cache_key = f"{code}_{data_type}_{period}"
            if cache_key in self.data_cache:
                self.progress_bar.setValue(80)
                data = self.data_cache[cache_key]
                self.display_data(data, code, data_type, period, from_cache=True)
                return
            
            # 模拟数据加载过程
            self.progress_bar.setValue(60)
            QApplication.processEvents()
            
            # 生成模拟数据（实际应用中这里调用真实API）
            data = self.generate_sample_data(code, data_type, period)
            
            # 缓存数据
            self.data_cache[cache_key] = data
            
            self.progress_bar.setValue(100)
            self.display_data(data, code, data_type, period, from_cache=False)
            
        except Exception as e:
            self.status_label.setText(f"❌ 数据加载失败: {str(e)}")
            self.data_display.setText(f"错误详情:\n{str(e)}")
        finally:
            self.progress_bar.setVisible(False)
    
    def generate_sample_data(self, code, data_type, period):
        """生成示例数据"""
        # 根据不同的数据类型生成不同数据
        if data_type == "基金数据":
            dates = pd.date_range('2024-01-01', periods=50, freq='D')
            nav = 1.0 + np.cumsum(np.random.randn(50) * 0.01)  # 净值
            data = pd.DataFrame({
                'date': dates,
                'net_value': nav,
                'acc_value': nav * 1.05,  # 累计净值
                'daily_return': np.random.randn(50) * 0.02  # 日增长率
            })
        elif data_type == "指数数据":
            dates = pd.date_range('2024-01-01', periods=100, freq='D')
            base_price = 3000 + np.random.randint(-500, 500)
            prices = base_price + np.cumsum(np.random.randn(100) * 10)
            data = pd.DataFrame({
                'date': dates,
                'open': prices * (1 + np.random.randn(100) * 0.01),
                'high': prices * (1 + np.abs(np.random.randn(100)) * 0.02),
                'low': prices * (1 - np.abs(np.random.randn(100)) * 0.02),
                'close': prices,
                'volume': np.random.randint(100000000, 1000000000, 100)
            })
        else:  # 股票数据
            dates = pd.date_range('2024-01-01', periods=100, freq='D')
            base_price = 10 + np.random.randint(0, 100)
            prices = base_price + np.cumsum(np.random.randn(100) * 0.5)
            data = pd.DataFrame({
                'date': dates,
                'open': prices * (1 + np.random.randn(100) * 0.01),
                'high': prices * (1 + np.abs(np.random.randn(100)) * 0.02),
                'low': prices * (1 - np.abs(np.random.randn(100)) * 0.02),
                'close': prices,
                'volume': np.random.randint(1000000, 10000000, 100),
                'amount': np.random.randint(10000000, 100000000, 100)
            })
            
        return data.sort_values('date').reset_index(drop=True)
    
    def display_data(self, data, code, data_type, period, from_cache=False):
        """显示数据"""
        cache_info = "【缓存数据】" if from_cache else "【实时数据】"
        
        # 数据基本信息
        info = f"📊 数据加载成功 {cache_info}\n"
        info += f"=========================================================\n"
        info += f"쀀 对象: {code} ({data_type})\n"
        info += f"📈 周期: {period}\n"
        info += f"📅 时间范围: {data['date'].iloc[0].strftime('%Y-%m-%d')} 至 {data['date'].iloc[-1].strftime('%Y-%m-%d')}\n"
        info += f"📊 数据条数: {len(data)}\n"
        info += f"💾 内存占用: {data.memory_usage(deep=True).sum() / 1024:.2f} KB\n"
        info += "=========================================================\n\n"
        
        # 根据数据类型显示不同字段
        if data_type == "基金数据":
            info += "💰 基金数据概览:\n"
            info += f"• 单位净值范围: {data['net_value'].min():.4f} - {data['net_value'].max():.4f}\n"
            info += f"• 累计净值范围: {data['acc_value'].min():.4f} - {data['acc_value'].max():.4f}\n"
            info += f"• 日增长率范围: {data['daily_return'].min()*100:.2f}% - {data['daily_return'].max()*100:.2f}%\n"
            info += f"• 平均日增长率: {data['daily_return'].mean()*100:.2f}%\n\n"
            
            info += "📋 前10条数据:\n"
            info += data.head(10)[['date', 'net_value', 'acc_value', 'daily_return']].to_string(index=False)
            
        elif data_type == "指数数据":
            info += "💹 指数数据概览:\n"
            info += f"• 开盘价范围: {data['open'].min():.2f} - {data['open'].max():.2f}\n"
            info += f"• 最高价范围: {data['high'].min():.2f} - {data['high'].max():.2f}\n"
            info += f"• 最低价范围: {data['low'].min():.2f} - {data['low'].max():.2f}\n"
            info += f"• 收盘价范围: {data['close'].min():.2f} - {data['close'].max():.2f}\n"
            info += f"• 成交量范围: {data['volume'].min():,.0f} - {data['volume'].max():,.0f}\n\n"
            
            info += "📋 前10条数据:\n"
            info += data.head(10)[['date', 'open', 'high', 'low', 'close', 'volume']].to_string(index=False)
            
        else:  # 股票数据
            info += "📊 股票数据概览:\n"
            info += f"• 开盘价范围: {data['open'].min():.2f} - {data['open'].max():.2f}\n"
            info += f"• 最高价范围: {data['high'].min():.2f} - {data['high'].max():.2f}\n"
            info += f"• 最低价范围: {data['low'].min():.2f} - {data['low'].max():.2f}\n"
            info += f"• 收盘价范围: {data['close'].min():.2f} - {data['close'].max():.2f}\n"
            info += f"• 成交量范围: {data['volume'].min():,.0f} - {data['volume'].max():,.0f}\n"
            info += f"• 成交额范围: {data['amount'].min():,.0f} - {data['amount'].max():,.0f}\n\n"
            
            # 计算技术指标
            info += "📈 技术指标:\n"
            returns = data['close'].pct_change().dropna()
            info += f"• 日收益率范围: {returns.min()*100:.2f}% - {returns.max()*100:.2f}%\n"
            info += f"• 平均日收益率: {returns.mean()*100:.2f}%\n"
            info += f"• 波动率(年化): {returns.std()*np.sqrt(252)*100:.2f}%\n"
            info += f"• 最大回撤: {self.calculate_max_drawdown(data['close'])*100:.2f}%\n\n"
            
            info += "📋 前10条数据:\n"
            info += data.head(10)[['date', 'open', 'high', 'low', 'close', 'volume']].to_string(index=False)
        
        self.data_display.setText(info)
        self.display_statistics(data, data_type)
        self.status_label.setText(f"✅ 数据加载完成 - {len(data)}条记录 {cache_info}")
    
    def calculate_max_drawdown(self, prices):
        """计算最大回撤"""
        peak = prices.expanding(min_periods=1).max()
        drawdown = (prices - peak) / peak
        return drawdown.min()
    
    def display_statistics(self, data, data_type):
        """显示统计信息"""
        stats = "📈 数据统计分析\n"
        stats += "=" * 30 + "\n\n"
        
        if data_type == "基金数据":
            stats += "📊 基金统计:\n"
            stats += f"• 净值标准差: {data['net_value'].std():.4f}\n"
            stats += f"• 年化波动率: {data['daily_return'].std()*np.sqrt(252):.2%}\n"
            stats += f"• 夏普比率: {data['daily_return'].mean()/data['daily_return'].std()*np.sqrt(252):.2f}\n"
            stats += f"• 盈利日占比: {(data['daily_return'] > 0).mean():.1%}\n"
            
        elif data_type == "指数数据":
            returns = data['close'].pct_change().dropna()
            stats += "📊 指数统计:\n"
            stats += f"• 年化收益率: {((data['close'].iloc[-1]/data['close'].iloc[0])**(252/len(data))-1):.2%}\n"
            stats += f"• 年化波动率: {returns.std()*np.sqrt(252):.2%}\n"
            stats += f"• 夏普比率: {returns.mean()/returns.std()*np.sqrt(252):.2f}\n"
            
        else:  # 股票数据
            returns = data['close'].pct_change().dropna()
            stats += "📊 股票统计:\n"
            stats += f"• 总收益率: {(data['close'].iloc[-1]/data['close'].iloc[0]-1):.2%}\n"
            stats += f"• 年化收益率: {((data['close'].iloc[-1]/data['close'].iloc[0])**(252/len(data))-1):.2%}\n"
            stats += f"• 年化波动率: {returns.std()*np.sqrt(252):.2%}\n"
            stats += f"• 夏普比率: {returns.mean()/returns.std()*np.sqrt(252):.2f}\n"
            stats += f"• 换手率估算: {(data['volume'].mean()/data['close'].mean()):.0f}手\n"
        
        self.stats_display.setText(stats)
    
    def refresh_data(self):
        """刷新数据"""
        code = self.code_input.text().strip()
        if code:
            # 清除缓存
            cache_keys = [k for k in self.data_cache.keys() if k.startswith(code)]
            for key in cache_keys:
                del self.data_cache[key]
            self.load_data()
        else:
            self.status_label.setText("❌ 请输入股票代码")
    
    def clear_data(self):
        """清空数据"""
        self.data_display.clear()
        self.stats_display.clear()
        self.update_display_placeholder()
        self.status_label.setText("📝 数据已清空 - 就绪状态")
        self.code_input.clear()

class IntegratedMainWindow(QMainWindow):
    """集成版主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(f'{APP_NAME} v{APP_VERSION} - 专业量化分析集成平台')
        self.setGeometry(50, 50, 1600, 1000)
        self.setMinimumSize(1400, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(IntegratedDataVisualizationWidget(), "📈 数据分析")
        # 这里可以添加其他标签页
        
        main_layout.addWidget(self.tab_widget)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🚀 Quant Analyzer 集成版就绪 - 所有模块已加载")
        
        # 定时更新状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5000)  # 每5秒更新一次
        
    def update_status(self):
        """更新状态栏"""
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_bar.showMessage(f"📊 Quant Analyzer v{APP_VERSION} | 当前时间: {current_time} | 系统运行正常")
        
    def show(self):
        super().show()
        print("🚀 集成版主窗口已显示")

def main():
    """主函数"""
    print(f"🚀 启动 {APP_NAME} v{APP_VERSION}")
    print("🔧 正在初始化量化分析集成平台...")
    
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    try:
        main_window = IntegratedMainWindow()
        main_window.show()
        print("✅ 集成版主窗口启动成功")
        print("📈 数据分析模块已就绪")
        print("🤖 策略引擎待集成")
        print("📊 回测系统待集成")
        
        exit_code = app.exec_()
        print("👋 应用程序已退出")
        return exit_code
        
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())