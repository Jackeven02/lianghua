"""
投资组合管理模块
提供组合构建、优化和风险管理功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """持仓信息"""
    stock_code: str
    stock_name: str
    quantity: int
    avg_cost: float
    current_price: float
    market_value: float
    profit_loss: float
    profit_loss_pct: float
    weight: float  # 占组合比例
    stop_loss: float
    target_price: float
    hold_days: int
    entry_date: datetime


@dataclass
class Portfolio:
    """投资组合"""
    total_value: float
    cash: float
    positions: List[Position] = field(default_factory=list)
    total_profit_loss: float = 0.0
    total_profit_loss_pct: float = 0.0
    win_rate: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    
    def get_position_count(self) -> int:
        """获取持仓数量"""
        return len(self.positions)
    
    def get_stock_weight(self, stock_code: str) -> float:
        """获取某只股票的权重"""
        for pos in self.positions:
            if pos.stock_code == stock_code:
                return pos.weight
        return 0.0


class PortfolioManager:
    """投资组合管理器"""
    
    def __init__(self, initial_capital: float = 1000000):
        """
        初始化组合管理器
        
        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trade_history = []
        self.max_positions = 10  # 最大持仓数量
        self.max_single_position = 0.15  # 单只股票最大仓位
        
    def build_portfolio(self, advice_list: List, 
                       available_capital: float = None) -> Portfolio:
        """
        根据投资建议构建投资组合
        
        Args:
            advice_list: 投资建议列表
            available_capital: 可用资金
            
        Returns:
            投资组合对象
        """
        if available_capital is None:
            available_capital = self.cash
        
        # 筛选买入信号
        buy_signals = [adv for adv in advice_list 
                      if adv.signal.value in ["强烈买入", "买入"]]
        
        if not buy_signals:
            logger.info("没有买入信号，保持现金")
            return self._get_current_portfolio()
        
        # 限制持仓数量
        buy_signals = buy_signals[:self.max_positions]
        
        # 计算每只股票的分配资金
        allocations = self._calculate_allocations(buy_signals, available_capital)
        
        # 构建持仓列表
        positions = []
        total_allocated = 0
        
        for advice, allocation in allocations.items():
            if allocation > 0:
                quantity = int(allocation / advice.current_price / 100) * 100  # 按手买入
                if quantity > 0:
                    actual_cost = quantity * advice.current_price
                    position = Position(
                        stock_code=advice.stock_code,
                        stock_name=advice.stock_name,
                        quantity=quantity,
                        avg_cost=advice.current_price,
                        current_price=advice.current_price,
                        market_value=actual_cost,
                        profit_loss=0,
                        profit_loss_pct=0,
                        weight=actual_cost / available_capital,
                        stop_loss=advice.stop_loss,
                        target_price=advice.target_price,
                        hold_days=0,
                        entry_date=datetime.now()
                    )
                    positions.append(position)
                    total_allocated += actual_cost
        
        # 创建组合对象
        portfolio = Portfolio(
            total_value=available_capital,
            cash=available_capital - total_allocated,
            positions=positions
        )
        
        logger.info(f"构建组合完成: {len(positions)} 个持仓, 使用资金 {total_allocated:.2f}")
        
        return portfolio
    
    def _calculate_allocations(self, advice_list: List, 
                              total_capital: float) -> Dict:
        """
        计算资金分配
        使用风险平价和评分加权的混合方法
        """
        allocations = {}
        
        # 1. 基于评分的初始权重
        total_score = sum(adv.overall_score for adv in advice_list)
        
        for advice in advice_list:
            # 基础权重 = 评分占比
            base_weight = advice.overall_score / total_score if total_score > 0 else 1.0 / len(advice_list)
            
            # 根据信心度调整
            confidence_adj = advice.confidence / 100
            
            # 根据风险等级调整
            risk_adj = {"低": 1.2, "中": 1.0, "高": 0.7}.get(advice.risk_level, 1.0)
            
            # 最终权重
            final_weight = base_weight * confidence_adj * risk_adj
            
            # 限制单只股票最大仓位
            final_weight = min(final_weight, self.max_single_position)
            
            allocations[advice] = final_weight * total_capital
        
        # 归一化，确保总和不超过可用资金
        total_allocated = sum(allocations.values())
        if total_allocated > total_capital:
            scale_factor = total_capital / total_allocated
            allocations = {k: v * scale_factor for k, v in allocations.items()}
        
        return allocations
    
    def rebalance_portfolio(self, current_portfolio: Portfolio, 
                           new_advice_list: List) -> Dict[str, str]:
        """
        再平衡投资组合
        
        Args:
            current_portfolio: 当前组合
            new_advice_list: 新的投资建议
            
        Returns:
            调整建议字典
        """
        rebalance_actions = {}
        
        # 1. 检查现有持仓是否需要卖出
        for position in current_portfolio.positions:
            # 检查止损
            if position.current_price <= position.stop_loss:
                rebalance_actions[position.stock_code] = f"触发止损，建议卖出"
                continue
            
            # 检查目标价
            if position.current_price >= position.target_price:
                rebalance_actions[position.stock_code] = f"达到目标价，建议止盈"
                continue
            
            # 检查新建议中的评级
            advice = next((adv for adv in new_advice_list 
                          if adv.stock_code == position.stock_code), None)
            
            if advice:
                if advice.signal.value in ["卖出", "强烈卖出"]:
                    rebalance_actions[position.stock_code] = f"评级下调为{advice.signal.value}，建议卖出"
                elif advice.signal.value == "持有":
                    rebalance_actions[position.stock_code] = "继续持有"
            else:
                # 不在新建议中，考虑卖出
                if position.profit_loss_pct < -0.05:  # 亏损超过5%
                    rebalance_actions[position.stock_code] = "不在推荐列表且亏损，建议卖出"
        
        # 2. 检查是否有新的买入机会
        current_codes = {pos.stock_code for pos in current_portfolio.positions}
        new_opportunities = [adv for adv in new_advice_list 
                           if adv.stock_code not in current_codes 
                           and adv.signal.value in ["强烈买入", "买入"]]
        
        if new_opportunities and current_portfolio.cash > 0:
            for adv in new_opportunities[:3]:  # 最多推荐3个新机会
                rebalance_actions[adv.stock_code] = f"新机会: {adv.signal.value}, 评分{adv.overall_score:.1f}"
        
        return rebalance_actions
    
    def calculate_portfolio_metrics(self, portfolio: Portfolio, 
                                   returns_history: pd.Series = None) -> Portfolio:
        """
        计算组合绩效指标
        
        Args:
            portfolio: 投资组合
            returns_history: 历史收益率序列
            
        Returns:
            更新后的组合对象
        """
        if not portfolio.positions:
            return portfolio
        
        # 计算总盈亏
        total_pl = sum(pos.profit_loss for pos in portfolio.positions)
        total_cost = sum(pos.avg_cost * pos.quantity for pos in portfolio.positions)
        
        portfolio.total_profit_loss = total_pl
        portfolio.total_profit_loss_pct = (total_pl / total_cost * 100) if total_cost > 0 else 0
        
        # 计算胜率
        winning_positions = sum(1 for pos in portfolio.positions if pos.profit_loss > 0)
        portfolio.win_rate = (winning_positions / len(portfolio.positions) * 100) if portfolio.positions else 0
        
        # 如果有历史收益率，计算更多指标
        if returns_history is not None and len(returns_history) > 0:
            # 最大回撤
            cumulative = (1 + returns_history).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            portfolio.max_drawdown = drawdown.min() * 100
            
            # 夏普比率
            if returns_history.std() > 0:
                portfolio.sharpe_ratio = (returns_history.mean() / returns_history.std() * 
                                        np.sqrt(252))
        
        return portfolio
    
    def get_risk_exposure(self, portfolio: Portfolio) -> Dict[str, float]:
        """
        分析组合风险暴露
        
        Args:
            portfolio: 投资组合
            
        Returns:
            风险暴露字典
        """
        exposure = {
            "高风险": 0.0,
            "中风险": 0.0,
            "低风险": 0.0,
            "现金": portfolio.cash / portfolio.total_value if portfolio.total_value > 0 else 1.0
        }
        
        for position in portfolio.positions:
            # 这里需要从建议中获取风险等级，简化处理
            # 实际应用中应该保存风险等级信息
            risk_level = "中风险"  # 默认
            exposure[risk_level] += position.weight
        
        return exposure
    
    def generate_portfolio_report(self, portfolio: Portfolio) -> str:
        """
        生成组合报告
        
        Args:
            portfolio: 投资组合
            
        Returns:
            报告文本
        """
        report = []
        report.append("=" * 60)
        report.append("投资组合报告")
        report.append("=" * 60)
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 组合概况
        report.append("【组合概况】")
        report.append(f"总资产: ¥{portfolio.total_value:,.2f}")
        report.append(f"现金: ¥{portfolio.cash:,.2f} ({portfolio.cash/portfolio.total_value*100:.1f}%)")
        report.append(f"持仓数量: {portfolio.get_position_count()}")
        report.append(f"总盈亏: ¥{portfolio.total_profit_loss:,.2f} ({portfolio.total_profit_loss_pct:+.2f}%)")
        report.append(f"胜率: {portfolio.win_rate:.1f}%")
        if portfolio.sharpe_ratio != 0:
            report.append(f"夏普比率: {portfolio.sharpe_ratio:.2f}")
        if portfolio.max_drawdown != 0:
            report.append(f"最大回撤: {portfolio.max_drawdown:.2f}%")
        report.append("")
        
        # 持仓明细
        if portfolio.positions:
            report.append("【持仓明细】")
            report.append(f"{'代码':<10} {'名称':<10} {'数量':<8} {'成本':<10} {'现价':<10} {'盈亏':<12} {'权重':<8}")
            report.append("-" * 80)
            
            for pos in sorted(portfolio.positions, key=lambda x: x.weight, reverse=True):
                report.append(
                    f"{pos.stock_code:<10} {pos.stock_name:<10} {pos.quantity:<8} "
                    f"¥{pos.avg_cost:<9.2f} ¥{pos.current_price:<9.2f} "
                    f"¥{pos.profit_loss:>7.2f}({pos.profit_loss_pct:+.1f}%) "
                    f"{pos.weight*100:>6.1f}%"
                )
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def _get_current_portfolio(self) -> Portfolio:
        """获取当前组合状态"""
        positions = list(self.positions.values())
        total_value = self.cash + sum(pos.market_value for pos in positions)
        
        return Portfolio(
            total_value=total_value,
            cash=self.cash,
            positions=positions
        )


class RiskManager:
    """风险管理器"""
    
    def __init__(self, max_portfolio_risk: float = 0.20):
        """
        初始化风险管理器
        
        Args:
            max_portfolio_risk: 组合最大风险容忍度
        """
        self.max_portfolio_risk = max_portfolio_risk
        self.max_single_loss = 0.02  # 单笔最大亏损2%
        self.max_daily_loss = 0.05   # 单日最大亏损5%
        
    def check_position_risk(self, position: Position, 
                           portfolio_value: float) -> Dict[str, any]:
        """
        检查单个持仓风险
        
        Args:
            position: 持仓信息
            portfolio_value: 组合总值
            
        Returns:
            风险检查结果
        """
        risk_check = {
            "is_safe": True,
            "warnings": [],
            "actions": []
        }
        
        # 1. 检查止损
        if position.current_price <= position.stop_loss:
            risk_check["is_safe"] = False
            risk_check["warnings"].append("触发止损价")
            risk_check["actions"].append("立即卖出")
        
        # 2. 检查单笔亏损
        loss_pct = position.profit_loss / portfolio_value
        if loss_pct < -self.max_single_loss:
            risk_check["is_safe"] = False
            risk_check["warnings"].append(f"单笔亏损超过{self.max_single_loss*100}%")
            risk_check["actions"].append("考虑止损")
        
        # 3. 检查持仓时间
        if position.hold_days > 60 and position.profit_loss_pct < 0:
            risk_check["warnings"].append("长期亏损持仓")
            risk_check["actions"].append("重新评估")
        
        return risk_check
    
    def check_portfolio_risk(self, portfolio: Portfolio) -> Dict[str, any]:
        """
        检查组合整体风险
        
        Args:
            portfolio: 投资组合
            
        Returns:
            风险检查结果
        """
        risk_check = {
            "risk_level": "低",
            "warnings": [],
            "suggestions": []
        }
        
        # 1. 检查集中度风险
        if portfolio.positions:
            max_weight = max(pos.weight for pos in portfolio.positions)
            if max_weight > 0.25:
                risk_check["warnings"].append(f"单只股票权重过高: {max_weight*100:.1f}%")
                risk_check["suggestions"].append("建议分散投资")
                risk_check["risk_level"] = "高"
        
        # 2. 检查整体亏损
        if portfolio.total_profit_loss_pct < -10:
            risk_check["warnings"].append(f"组合亏损较大: {portfolio.total_profit_loss_pct:.1f}%")
            risk_check["suggestions"].append("考虑降低仓位或调整策略")
            risk_check["risk_level"] = "高"
        
        # 3. 检查现金比例
        cash_ratio = portfolio.cash / portfolio.total_value if portfolio.total_value > 0 else 1.0
        if cash_ratio < 0.1:
            risk_check["warnings"].append("现金比例过低")
            risk_check["suggestions"].append("保持适当现金储备")
        
        # 4. 检查最大回撤
        if portfolio.max_drawdown < -15:
            risk_check["warnings"].append(f"最大回撤过大: {portfolio.max_drawdown:.1f}%")
            risk_check["risk_level"] = "高"
        
        return risk_check
