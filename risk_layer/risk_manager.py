"""
风险管理模块
提供风险监控、仓位管理和风险预警功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
from analysis_layer import StatisticalAnalysis

logger = logging.getLogger(__name__)

class RiskManager:
    """风险管理器"""
    
    def __init__(self, max_position_size: float = 0.1, 
                 max_portfolio_risk: float = 0.02,
                 stop_loss_pct: float = 0.05,
                 take_profit_pct: float = 0.1):
        """
        初始化风险管理器
        
        Args:
            max_position_size: 最大单笔仓位比例
            max_portfolio_risk: 最大投资组合风险比例
            stop_loss_pct: 止损比例
            take_profit_pct: 止盈比例
        """
        self.max_position_size = max_position_size
        self.max_portfolio_risk = max_portfolio_risk
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.positions = {}  # {symbol: {'size': float, 'entry_price': float, 'entry_date': datetime}}
        self.risk_limits = {}
        
    def set_risk_limits(self, symbol: str, max_loss: float, max_exposure: float):
        """设置特定标的的风险限制"""
        self.risk_limits[symbol] = {
            'max_loss': max_loss,
            'max_exposure': max_exposure
        }
        
    def calculate_position_size(self, capital: float, entry_price: float, 
                              stop_loss_price: float, symbol: str = None) -> float:
        """
        计算合适的仓位大小
        
        Args:
            capital: 可用资金
            entry_price: 入场价格
            stop_loss_price: 止损价格
            symbol: 标的代码
            
        Returns:
            建议仓位大小
        """
        # 计算每份风险
        risk_per_share = abs(entry_price - stop_loss_price)
        if risk_per_share == 0:
            return 0
            
        # 计算最大可承受风险金额
        max_risk_amount = capital * self.max_portfolio_risk
        
        # 计算最大仓位
        max_shares_by_risk = max_risk_amount / risk_per_share
        max_shares_by_position = (capital * self.max_position_size) / entry_price
        
        # 取较小值
        position_size = min(max_shares_by_risk, max_shares_by_position)
        
        # 检查特定标的限制
        if symbol and symbol in self.risk_limits:
            limits = self.risk_limits[symbol]
            max_shares_by_limit = limits['max_exposure'] / entry_price
            position_size = min(position_size, max_shares_by_limit)
            
        return int(position_size)
    
    def check_position_risk(self, symbol: str, current_price: float) -> Dict[str, Any]:
        """
        检查持仓风险
        
        Args:
            symbol: 标的代码
            current_price: 当前价格
            
        Returns:
            风险检查结果
        """
        if symbol not in self.positions:
            return {'status': 'no_position', 'risk': 0}
            
        position = self.positions[symbol]
        entry_price = position['entry_price']
        current_size = position['size']
        
        # 计算收益率
        if entry_price > 0:
            return_rate = (current_price - entry_price) / entry_price
        else:
            return_rate = 0
            
        # 检查止损和止盈
        stop_loss_triggered = return_rate <= -self.stop_loss_pct
        take_profit_triggered = return_rate >= self.take_profit_pct
        
        # 计算当前风险
        current_value = current_size * current_price
        entry_value = current_size * entry_price
        current_risk = (entry_value - current_value) / entry_value if entry_value > 0 else 0
        
        risk_status = {
            'symbol': symbol,
            'current_size': current_size,
            'entry_price': entry_price,
            'current_price': current_price,
            'return_rate': return_rate,
            'current_value': current_value,
            'current_risk': current_risk,
            'stop_loss_triggered': stop_loss_triggered,
            'take_profit_triggered': take_profit_triggered,
            'stop_loss_price': entry_price * (1 - self.stop_loss_pct),
            'take_profit_price': entry_price * (1 + self.take_profit_pct)
        }
        
        # 确定风险等级
        if stop_loss_triggered:
            risk_status['risk_level'] = 'high'
            risk_status['action'] = 'sell_stop_loss'
        elif take_profit_triggered:
            risk_status['risk_level'] = 'low'
            risk_status['action'] = 'sell_take_profit'
        elif current_risk > 0.03:  # 3%风险警告
            risk_status['risk_level'] = 'medium'
            risk_status['action'] = 'monitor'
        else:
            risk_status['risk_level'] = 'low'
            risk_status['action'] = 'hold'
            
        return risk_status
    
    def update_position(self, symbol: str, size: float, entry_price: float):
        """更新持仓信息"""
        self.positions[symbol] = {
            'size': size,
            'entry_price': entry_price,
            'entry_date': datetime.now()
        }
        
    def close_position(self, symbol: str):
        """平仓"""
        if symbol in self.positions:
            del self.positions[symbol]
            logger.info(f"已平仓: {symbol}")
    
    def get_portfolio_risk(self) -> Dict[str, Any]:
        """获取投资组合整体风险"""
        total_risk = 0
        position_risks = []
        
        for symbol, position in self.positions.items():
            risk_status = self.check_position_risk(symbol, position['entry_price'])
            position_risks.append(risk_status)
            total_risk += risk_status['current_risk'] * risk_status['current_value']
            
        avg_risk = total_risk / len(self.positions) if self.positions else 0
        
        return {
            'total_positions': len(self.positions),
            'average_risk': avg_risk,
            'high_risk_positions': [p for p in position_risks if p['risk_level'] == 'high'],
            'medium_risk_positions': [p for p in position_risks if p['risk_level'] == 'medium'],
            'position_details': position_risks
        }

class MarketRiskMonitor:
    """市场风险监控器"""
    
    def __init__(self, volatility_window: int = 30):
        self.volatility_window = volatility_window
        self.historical_data = {}
        
    def add_market_data(self, symbol: str, data: pd.Series):
        """添加市场数据"""
        if symbol not in self.historical_data:
            self.historical_data[symbol] = []
        self.historical_data[symbol].append(data)
        
        # 保持数据窗口
        if len(self.historical_data[symbol]) > self.volatility_window:
            self.historical_data[symbol] = self.historical_data[symbol][-self.volatility_window:]
    
    def calculate_market_volatility(self, symbol: str) -> float:
        """计算市场波动率"""
        if symbol not in self.historical_data or len(self.historical_data[symbol]) < 2:
            return 0
            
        data = pd.concat(self.historical_data[symbol])
        returns = data.pct_change().dropna()
        
        if len(returns) > 0:
            volatility = returns.std() * np.sqrt(252)  # 年化波动率
            return volatility
        else:
            return 0
    
    def detect_market_anomalies(self, current_data: pd.Series, 
                              symbol: str) -> Dict[str, Any]:
        """检测市场异常"""
        if symbol not in self.historical_data:
            return {'anomaly_detected': False}
            
        historical_returns = []
        for data in self.historical_data[symbol]:
            returns = data.pct_change().dropna()
            historical_returns.extend(returns.tolist())
            
        if len(historical_returns) < 10:
            return {'anomaly_detected': False}
            
        # 计算当前收益率
        current_return = current_data.iloc[-1] / current_data.iloc[-2] - 1 if len(current_data) >= 2 else 0
        
        # 统计分析
        mean_return = np.mean(historical_returns)
        std_return = np.std(historical_returns)
        
        # 检测异常（超过2个标准差）
        z_score = abs(current_return - mean_return) / std_return if std_return > 0 else 0
        anomaly_detected = z_score > 2.0
        
        return {
            'anomaly_detected': anomaly_detected,
            'z_score': z_score,
            'current_return': current_return,
            'historical_mean': mean_return,
            'historical_std': std_return,
            'volatility': std_return * np.sqrt(252)
        }
    
    def generate_risk_alerts(self) -> List[Dict[str, Any]]:
        """生成风险警报"""
        alerts = []
        
        for symbol in self.historical_data.keys():
            if len(self.historical_data[symbol]) > 0:
                latest_data = self.historical_data[symbol][-1]
                anomaly_result = self.detect_market_anomalies(latest_data, symbol)
                
                if anomaly_result['anomaly_detected']:
                    alerts.append({
                        'symbol': symbol,
                        'type': 'market_anomaly',
                        'severity': 'high' if anomaly_result['z_score'] > 3 else 'medium',
                        'details': anomaly_result
                    })
                    
                # 波动率警报
                volatility = self.calculate_market_volatility(symbol)
                if volatility > 0.3:  # 30%年化波动率警报
                    alerts.append({
                        'symbol': symbol,
                        'type': 'high_volatility',
                        'severity': 'high',
                        'details': {'volatility': volatility}
                    })
                    
        return alerts

class PositionSizing:
    """仓位管理"""
    
    @staticmethod
    def kelly_criterion(win_rate: float, win_loss_ratio: float) -> float:
        """
        凯利公式计算最优仓位
        
        Args:
            win_rate: 胜率
            win_loss_ratio: 盈亏比
            
        Returns:
            最优仓位比例
        """
        if win_loss_ratio <= 0:
            return 0
            
        kelly_fraction = win_rate - (1 - win_rate) / win_loss_ratio
        return max(0, min(kelly_fraction, 1.0))  # 限制在0-1之间
    
    @staticmethod
    def fixed_fractional_sizing(capital: float, risk_percent: float, 
                              entry_price: float, stop_loss_price: float) -> float:
        """
        固定比例仓位管理
        
        Args:
            capital: 总资金
            risk_percent: 愿意承担的风险比例
            entry_price: 入场价格
            stop_loss_price: 止损价格
            
        Returns:
            仓位大小
        """
        risk_amount = capital * risk_percent
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share == 0:
            return 0
            
        position_size = risk_amount / risk_per_share
        return int(position_size)
    
    @staticmethod
    def volatility_adjusted_sizing(capital: float, entry_price: float,
                                 volatility: float, target_risk: float = 0.02) -> float:
        """
        波动率调整仓位管理
        
        Args:
            capital: 总资金
            entry_price: 入场价格
            volatility: 波动率
            target_risk: 目标风险比例
            
        Returns:
            仓位大小
        """
        if volatility <= 0:
            return 0
            
        # 基于波动率调整风险
        adjusted_risk = target_risk / volatility
        risk_amount = capital * adjusted_risk
        position_size = risk_amount / entry_price
        
        return int(position_size)