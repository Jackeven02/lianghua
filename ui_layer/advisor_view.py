"""
智能投资顾问视图
展示投资建议和组合管理界面
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QComboBox,
                             QGroupBox, QTextEdit, QProgressBar, QTabWidget,
                             QHeaderView, QMessageBox, QSpinBox, QDoubleSpinBox,
                             QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QColor, QFont
import logging
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class AdvisorView(QWidget):
    """智能投资顾问视图"""
    
    # 信号
    scan_requested = pyqtSignal(list, str)  # 扫描请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.advice_list = []
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 1. 投资建议标签页
        self.advice_tab = self._create_advice_tab()
        self.tab_widget.addTab(self.advice_tab, "💡 投资建议")
        
        # 2. 组合管理标签页
        self.portfolio_tab = self._create_portfolio_tab()
        self.tab_widget.addTab(self.portfolio_tab, "📊 组合管理")
        
        # 3. 风险监控标签页
        self.risk_tab = self._create_risk_tab()
        self.tab_widget.addTab(self.risk_tab, "⚠️ 风险监控")
        
        layout.addWidget(self.tab_widget)
        
    def _create_advice_tab(self) -> QWidget:
        """创建投资建议标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 控制面板
        control_group = QGroupBox("扫描设置")
        control_layout = QHBoxLayout()
        
        # 数据源选择
        control_layout.addWidget(QLabel("数据源:"))
        self.data_source_combo = QComboBox()
        self.data_source_combo.addItems(["真实数据(efinance)", "模拟数据(测试)"])
        control_layout.addWidget(self.data_source_combo)
        
        # 风险偏好选择
        control_layout.addWidget(QLabel("风险偏好:"))
        self.risk_combo = QComboBox()
        self.risk_combo.addItems(["保守", "中等", "激进"])
        self.risk_combo.setCurrentText("中等")
        control_layout.addWidget(self.risk_combo)
        
        # 最低信心度
        control_layout.addWidget(QLabel("最低信心度:"))
        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(50, 90)
        self.confidence_spin.setValue(60)
        self.confidence_spin.setSuffix("%")
        control_layout.addWidget(self.confidence_spin)
        
        # 股票数量
        control_layout.addWidget(QLabel("扫描数量:"))
        self.stock_count_spin = QSpinBox()
        self.stock_count_spin.setRange(10, 100)
        self.stock_count_spin.setValue(20)
        self.stock_count_spin.setSuffix("只")
        control_layout.addWidget(self.stock_count_spin)
        
        # 扫描按钮
        self.scan_btn = QPushButton("🔍 开始扫描市场")
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.scan_btn.clicked.connect(self._on_scan_clicked)
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
        self.stats_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(self.stats_label)
        
        # 投资建议表格
        self.advice_table = QTableWidget()
        self.advice_table.setColumnCount(11)
        self.advice_table.setHorizontalHeaderLabels([
            "代码", "名称", "信号", "信心度", "当前价", "目标价", 
            "止损价", "综合评分", "风险", "建议仓位", "操作"
        ])
        
        # 设置表格样式
        self.advice_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.advice_table.setAlternatingRowColors(True)
        self.advice_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.advice_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.advice_table.itemSelectionChanged.connect(self._on_advice_selected)
        
        layout.addWidget(self.advice_table)
        
        # 详细信息面板
        detail_group = QGroupBox("详细分析")
        detail_layout = QVBoxLayout()
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(150)
        detail_layout.addWidget(self.detail_text)
        
        detail_group.setLayout(detail_layout)
        layout.addWidget(detail_group)
        
        return widget
    
    def _create_portfolio_tab(self) -> QWidget:
        """创建组合管理标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 组合概况
        summary_group = QGroupBox("组合概况")
        summary_layout = QVBoxLayout()
        
        self.portfolio_summary = QLabel("暂无组合数据")
        self.portfolio_summary.setStyleSheet("""
            QLabel {
                font-size: 14px;
                padding: 10px;
                background-color: #f5f5f5;
                border-radius: 4px;
            }
        """)
        summary_layout.addWidget(self.portfolio_summary)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        self.build_portfolio_btn = QPushButton("📦 构建组合")
        self.build_portfolio_btn.clicked.connect(self._on_build_portfolio)
        btn_layout.addWidget(self.build_portfolio_btn)
        
        self.rebalance_btn = QPushButton("⚖️ 再平衡")
        self.rebalance_btn.clicked.connect(self._on_rebalance)
        btn_layout.addWidget(self.rebalance_btn)
        
        self.export_btn = QPushButton("📄 导出报告")
        self.export_btn.clicked.connect(self._on_export_report)
        btn_layout.addWidget(self.export_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 持仓表格
        self.position_table = QTableWidget()
        self.position_table.setColumnCount(10)
        self.position_table.setHorizontalHeaderLabels([
            "代码", "名称", "数量", "成本价", "现价", 
            "市值", "盈亏", "盈亏率", "权重", "持仓天数"
        ])
        self.position_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.position_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.position_table)
        
        return widget
    
    def _create_risk_tab(self) -> QWidget:
        """创建风险监控标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 风险指标
        metrics_group = QGroupBox("风险指标")
        metrics_layout = QVBoxLayout()
        
        self.risk_metrics = QLabel("暂无风险数据")
        self.risk_metrics.setStyleSheet("""
            QLabel {
                font-size: 13px;
                padding: 10px;
                background-color: #fff3cd;
                border-radius: 4px;
            }
        """)
        metrics_layout.addWidget(self.risk_metrics)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        # 风险警告
        warning_group = QGroupBox("⚠️ 风险警告")
        warning_layout = QVBoxLayout()
        
        self.warning_text = QTextEdit()
        self.warning_text.setReadOnly(True)
        self.warning_text.setMaximumHeight(200)
        warning_layout.addWidget(self.warning_text)
        
        warning_group.setLayout(warning_layout)
        layout.addWidget(warning_group)
        
        # 建议操作
        action_group = QGroupBox("💡 建议操作")
        action_layout = QVBoxLayout()
        
        self.action_text = QTextEdit()
        self.action_text.setReadOnly(True)
        action_layout.addWidget(self.action_text)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        return widget
    
    def _on_scan_clicked(self):
        """扫描按钮点击事件"""
        risk_tolerance = self.risk_combo.currentText()
        min_confidence = self.confidence_spin.value()
        use_real_data = (self.data_source_combo.currentIndex() == 0)
        stock_count = self.stock_count_spin.value()
        
        # 获取股票列表
        stock_list = self._get_stock_list(use_real_data, stock_count)
        
        if not stock_list:
            QMessageBox.warning(self, "警告", "没有可扫描的股票列表")
            return
        
        # 显示进度
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(stock_list))
        self.progress_bar.setValue(0)
        self.scan_btn.setEnabled(False)
        
        # 发送扫描信号（包含数据源信息）
        self.scan_requested.emit(stock_list, risk_tolerance)
        
    def _get_stock_list(self, use_real_data: bool, count: int = 20) -> list:
        """获取股票列表"""
        if use_real_data:
            try:
                from data_layer.efinance_provider import EFinanceProvider
                provider = EFinanceProvider()
                
                # 获取热门股票
                stock_list = provider.get_hot_stocks(count)
                
                if stock_list:
                    return stock_list
                else:
                    QMessageBox.warning(self, "警告", "无法获取股票列表，使用默认列表")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"获取股票列表失败: {str(e)}\n使用默认列表")
        
        # 默认列表
        return [
            ("600519", "贵州茅台"),
            ("000858", "五粮液"),
            ("600036", "招商银行"),
            ("601318", "中国平安"),
            ("000333", "美的集团"),
            ("600276", "恒瑞医药"),
            ("000651", "格力电器"),
            ("601888", "中国中免"),
            ("300750", "宁德时代"),
            ("002475", "立讯精密"),
        ][:count]
    
    def update_advice_list(self, advice_list: list):
        """更新投资建议列表"""
        self.advice_list = advice_list
        self.advice_table.setRowCount(len(advice_list))
        
        for row, advice in enumerate(advice_list):
            # 代码
            self.advice_table.setItem(row, 0, QTableWidgetItem(advice.stock_code))
            
            # 名称
            self.advice_table.setItem(row, 1, QTableWidgetItem(advice.stock_name))
            
            # 信号
            signal_item = QTableWidgetItem(advice.signal.value)
            if advice.signal.value == "强烈买入":
                signal_item.setBackground(QColor("#4CAF50"))
                signal_item.setForeground(QColor("white"))
            elif advice.signal.value == "买入":
                signal_item.setBackground(QColor("#8BC34A"))
            self.advice_table.setItem(row, 2, signal_item)
            
            # 信心度
            confidence_item = QTableWidgetItem(f"{advice.confidence:.1f}%")
            self.advice_table.setItem(row, 3, confidence_item)
            
            # 价格信息
            self.advice_table.setItem(row, 4, QTableWidgetItem(f"¥{advice.current_price:.2f}"))
            self.advice_table.setItem(row, 5, QTableWidgetItem(f"¥{advice.target_price:.2f}"))
            self.advice_table.setItem(row, 6, QTableWidgetItem(f"¥{advice.stop_loss:.2f}"))
            
            # 综合评分
            score_item = QTableWidgetItem(f"{advice.overall_score:.1f}")
            if advice.overall_score >= 80:
                score_item.setBackground(QColor("#4CAF50"))
                score_item.setForeground(QColor("white"))
            elif advice.overall_score >= 65:
                score_item.setBackground(QColor("#8BC34A"))
            self.advice_table.setItem(row, 7, score_item)
            
            # 风险等级
            risk_item = QTableWidgetItem(advice.risk_level)
            if advice.risk_level == "高":
                risk_item.setForeground(QColor("red"))
            elif advice.risk_level == "低":
                risk_item.setForeground(QColor("green"))
            self.advice_table.setItem(row, 8, risk_item)
            
            # 建议仓位
            self.advice_table.setItem(row, 9, QTableWidgetItem(f"{advice.position_size*100:.1f}%"))
            
            # 操作按钮
            btn = QPushButton("查看详情")
            btn.clicked.connect(lambda checked, r=row: self._show_detail(r))
            self.advice_table.setCellWidget(row, 10, btn)
        
        # 更新统计信息
        self.stats_label.setText(
            f"找到 {len(advice_list)} 个投资机会 | "
            f"平均评分: {sum(a.overall_score for a in advice_list)/len(advice_list):.1f} | "
            f"强烈买入: {sum(1 for a in advice_list if a.signal.value=='强烈买入')} | "
            f"买入: {sum(1 for a in advice_list if a.signal.value=='买入')}"
        )
        
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)
    
    def _on_advice_selected(self):
        """建议选中事件"""
        selected_rows = self.advice_table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            self._show_detail(row)
    
    def _show_detail(self, row: int):
        """显示详细信息"""
        if row >= len(self.advice_list):
            return
        
        advice = self.advice_list[row]
        
        detail_html = f"""
        <h3>{advice.stock_name} ({advice.stock_code})</h3>
        <p><b>投资信号:</b> <span style="color: {'green' if '买入' in advice.signal.value else 'red'}; font-size: 16px;">
        {advice.signal.value}</span> (信心度: {advice.confidence:.1f}%)</p>
        
        <p><b>价格信息:</b><br>
        当前价: ¥{advice.current_price:.2f} | 
        目标价: ¥{advice.target_price:.2f} ({(advice.target_price/advice.current_price-1)*100:+.1f}%) | 
        止损价: ¥{advice.stop_loss:.2f} ({(advice.stop_loss/advice.current_price-1)*100:+.1f}%)</p>
        
        <p><b>评分详情:</b><br>
        综合评分: {advice.overall_score:.1f} | 
        技术面: {advice.technical_score:.1f} | 
        基本面: {advice.fundamental_score:.1f} | 
        情绪面: {advice.sentiment_score:.1f}</p>
        
        <p><b>投资建议:</b><br>
        风险等级: {advice.risk_level} | 
        建议仓位: {advice.position_size*100:.1f}% | 
        投资期限: {advice.time_horizon}</p>
        
        <p><b>理由分析:</b></p>
        <ul>
        {''.join(f'<li>{reason}</li>' for reason in advice.reasons)}
        </ul>
        
        <p style="color: #666; font-size: 11px;">
        生成时间: {advice.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
        </p>
        """
        
        self.detail_text.setHtml(detail_html)
    
    def _on_build_portfolio(self):
        """构建组合"""
        if not self.advice_list:
            QMessageBox.warning(self, "警告", "请先扫描市场获取投资建议")
            return
        
        # 这里应该调用组合管理器构建组合
        QMessageBox.information(self, "提示", "组合构建功能开发中...")
    
    def _on_rebalance(self):
        """再平衡组合"""
        QMessageBox.information(self, "提示", "再平衡功能开发中...")
    
    def _on_export_report(self):
        """导出报告"""
        QMessageBox.information(self, "提示", "报告导出功能开发中...")
    
    def update_portfolio(self, portfolio):
        """更新组合信息"""
        # 更新概况
        summary_text = f"""
        <b>总资产:</b> ¥{portfolio.total_value:,.2f}<br>
        <b>现金:</b> ¥{portfolio.cash:,.2f} ({portfolio.cash/portfolio.total_value*100:.1f}%)<br>
        <b>持仓数量:</b> {portfolio.get_position_count()}<br>
        <b>总盈亏:</b> <span style="color: {'green' if portfolio.total_profit_loss >= 0 else 'red'};">
        ¥{portfolio.total_profit_loss:,.2f} ({portfolio.total_profit_loss_pct:+.2f}%)</span><br>
        <b>胜率:</b> {portfolio.win_rate:.1f}%
        """
        
        if portfolio.sharpe_ratio != 0:
            summary_text += f"<br><b>夏普比率:</b> {portfolio.sharpe_ratio:.2f}"
        if portfolio.max_drawdown != 0:
            summary_text += f"<br><b>最大回撤:</b> {portfolio.max_drawdown:.2f}%"
        
        self.portfolio_summary.setText(summary_text)
        
        # 更新持仓表格
        self.position_table.setRowCount(len(portfolio.positions))
        
        for row, pos in enumerate(portfolio.positions):
            self.position_table.setItem(row, 0, QTableWidgetItem(pos.stock_code))
            self.position_table.setItem(row, 1, QTableWidgetItem(pos.stock_name))
            self.position_table.setItem(row, 2, QTableWidgetItem(str(pos.quantity)))
            self.position_table.setItem(row, 3, QTableWidgetItem(f"¥{pos.avg_cost:.2f}"))
            self.position_table.setItem(row, 4, QTableWidgetItem(f"¥{pos.current_price:.2f}"))
            self.position_table.setItem(row, 5, QTableWidgetItem(f"¥{pos.market_value:,.2f}"))
            
            # 盈亏
            pl_item = QTableWidgetItem(f"¥{pos.profit_loss:,.2f}")
            pl_item.setForeground(QColor("green" if pos.profit_loss >= 0 else "red"))
            self.position_table.setItem(row, 6, pl_item)
            
            # 盈亏率
            pl_pct_item = QTableWidgetItem(f"{pos.profit_loss_pct:+.2f}%")
            pl_pct_item.setForeground(QColor("green" if pos.profit_loss_pct >= 0 else "red"))
            self.position_table.setItem(row, 7, pl_pct_item)
            
            self.position_table.setItem(row, 8, QTableWidgetItem(f"{pos.weight*100:.1f}%"))
            self.position_table.setItem(row, 9, QTableWidgetItem(str(pos.hold_days)))
    
    def update_risk_info(self, risk_check: dict):
        """更新风险信息"""
        # 更新风险指标
        metrics_text = f"""
        <b>风险等级:</b> <span style="color: {'red' if risk_check['risk_level']=='高' else 'orange' if risk_check['risk_level']=='中' else 'green'}; font-size: 16px;">
        {risk_check['risk_level']}</span>
        """
        self.risk_metrics.setText(metrics_text)
        
        # 更新警告
        if risk_check.get('warnings'):
            warning_html = "<ul>"
            for warning in risk_check['warnings']:
                warning_html += f"<li style='color: red;'>{warning}</li>"
            warning_html += "</ul>"
            self.warning_text.setHtml(warning_html)
        else:
            self.warning_text.setHtml("<p style='color: green;'>✓ 暂无风险警告</p>")
        
        # 更新建议
        if risk_check.get('suggestions'):
            action_html = "<ul>"
            for suggestion in risk_check['suggestions']:
                action_html += f"<li>{suggestion}</li>"
            action_html += "</ul>"
            self.action_text.setHtml(action_html)
        else:
            self.action_text.setHtml("<p>暂无特别建议</p>")
