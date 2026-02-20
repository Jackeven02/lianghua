"""
回测系统模块
提供策略回测和绩效评估功能
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging
from data_layer import get_data_provider
from analysis_layer import StatisticalAnalysis

logger = logging.getLogger(__name__)

class BacktestingEngine:
    """回测引擎类"""
    
    def __init__(self, initial_capital: float = 1000000.0, 
                 commission: float = 0.001, slippage: float = 0.0005):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资金
            commission: 手续费率
            slippage: 滑点率
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.reset()
        
    def reset(self):
        """重置回测状态"""
        self.current_capital = self.initial_capital
        self.positions = {}  # {symbol: quantity}
        self.trades = []     # 交易记录
        self.portfolio_value = [self.initial_capital]  # 投资组合价值历史
        self.dates = []      # 日期历史
        
    def run_backtest(self, strategy, data: pd.DataFrame, 
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        运行回测
        
        Args:
            strategy: 策略对象
            data: 历史数据
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            回测结果
        """
        self.reset()
        
        # 数据过滤
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]
            
        if data.empty:
            raise ValueError("回测数据为空")
            
        logger.info(f"开始回测，数据范围: {data.index[0]} 到 {data.index[-1]}")
        
        # 按日期遍历数据
        for i, (date, row) in enumerate(data.iterrows()):
            self.dates.append(date)
            
            # 生成交易信号
            signal_data = data.iloc[:i+1]  # 截取到当前日期的数据
            signals = strategy.generate_signals(signal_data)
            
            # 执行交易
            if signals['signal'] != 'hold':
                self._execute_trade(signals['signal'], row, date, signals.get('confidence', 1.0))
            
            # 计算当前投资组合价值
            current_value = self._calculate_portfolio_value(row)
            self.portfolio_value.append(current_value)
            
        # 计算绩效指标
        performance = self._calculate_performance()
        
        logger.info("回测完成")
        return performance
    
    def _execute_trade(self, signal: str, current_data: pd.Series, 
                      date: datetime, confidence: float = 1.0):
        """
        执行交易
        
        Args:
            signal: 交易信号 ('buy' 或 'sell')
            current_data: 当前市场数据
            date: 交易日期
            confidence: 信号置信度
        """
        price = current_data['close']
        symbol = current_data.get('symbol', 'default')
        
        # 计算可交易金额（考虑置信度）
        available_capital = self.current_capital * confidence
        
        if signal == 'buy':
            # 计算可购买数量
            max_shares = int(available_capital / (price * (1 + self.slippage + self.commission)))
            
            if max_shares > 0:
                cost = max_shares * price * (1 + self.slippage + self.commission)
                
                if cost <= self.current_capital:
                    # 更新持仓
                    if symbol in self.positions:
                        self.positions[symbol] += max_shares
                    else:
                        self.positions[symbol] = max_shares
                    
                    # 更新资金
                    self.current_capital -= cost
                    
                    # 记录交易
                    self.trades.append({
                        'date': date,
                        'symbol': symbol,
                        'action': 'buy',
                        'quantity': max_shares,
                        'price': price,
                        'cost': cost,
                        'commission': cost * self.commission
                    })
                    
                    logger.debug(f"买入 {max_shares} 股 {symbol}，价格 {price}")
                    
        elif signal == 'sell':
            # 卖出持仓
            if symbol in self.positions and self.positions[symbol] > 0:
                quantity = self.positions[symbol]
                proceeds = quantity * price * (1 - self.slippage - self.commission)
                
                # 更新资金
                self.current_capital += proceeds
                
                # 清空持仓
                self.positions[symbol] = 0
                
                # 记录交易
                self.trades.append({
                    'date': date,
                    'symbol': symbol,
                    'action': 'sell',
                    'quantity': quantity,
                    'price': price,
                    'proceeds': proceeds,
                    'commission': proceeds * self.commission
                })
                
                logger.debug(f"卖出 {quantity} 股 {symbol}，价格 {price}")
    
    def _calculate_portfolio_value(self, current_data: pd.Series) -> float:
        """
        计算当前投资组合价值
        
        Args:
            current_data: 当前市场数据
            
        Returns:
            投资组合总价值
        """
        total_value = self.current_capital
        
        # 计算持仓价值
        for symbol, quantity in self.positions.items():
            if quantity > 0:
                price = current_data['close']  # 简化处理，假设所有持仓使用相同价格
                total_value += quantity * price
                
        return total_value
    
    def _calculate_performance(self) -> Dict[str, Any]:
        """
        计算回测绩效指标
        
        Returns:
            绩效指标字典
        """
        if len(self.portfolio_value) < 2:
            return {}
            
        # 计算收益率序列
        portfolio_series = pd.Series(self.portfolio_value[1:], index=self.dates)
        returns = portfolio_series.pct_change().dropna()
        
        # 基础指标
        total_return = (self.portfolio_value[-1] - self.initial_capital) / self.initial_capital
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1 if len(returns) > 0 else 0
        
        # 风险指标
        volatility = StatisticalAnalysis.calculate_volatility(returns)
        max_drawdown, drawdown_series = StatisticalAnalysis.calculate_max_drawdown(returns)
        var_5 = StatisticalAnalysis.calculate_var(returns, 0.05)
        cvar_5 = StatisticalAnalysis.calculate_cvar(returns, 0.05)
        
        # 风险调整收益
        sharpe_ratio = StatisticalAnalysis.calculate_sharpe_ratio(returns)
        sortino_ratio = StatisticalAnalysis.calculate_sortino_ratio(returns)
        
        # 交易统计
        buy_trades = [t for t in self.trades if t['action'] == 'buy']
        sell_trades = [t for t in self.trades if t['action'] == 'sell']
        
        win_trades = []
        loss_trades = []
        
        # 计算每笔交易的盈亏
        for i in range(len(buy_trades)):
            if i < len(sell_trades):
                buy_trade = buy_trades[i]
                sell_trade = sell_trades[i]
                
                if 'proceeds' in sell_trade and 'cost' in buy_trade:
                    profit = sell_trade['proceeds'] - buy_trade['cost']
                    if profit > 0:
                        win_trades.append(profit)
                    else:
                        loss_trades.append(profit)
        
        win_rate = len(win_trades) / len(buy_trades) if buy_trades else 0
        avg_win = np.mean(win_trades) if win_trades else 0
        avg_loss = np.mean(loss_trades) if loss_trades else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        performance = {
            # 基础指标
            'initial_capital': self.initial_capital,
            'final_capital': self.portfolio_value[-1],
            'total_return': total_return,
            'annual_return': annual_return,
            'total_trades': len(self.trades) // 2,  # 买入卖出算一笔交易
            
            # 风险指标
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'var_5%': var_5,
            'cvar_5%': cvar_5,
            
            # 风险调整收益
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            
            # 交易统计
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_consecutive_wins': self._calculate_max_consecutive_wins(),
            'max_consecutive_losses': self._calculate_max_consecutive_losses(),
            
            # 详细数据
            'portfolio_history': portfolio_series.to_dict(),
            'drawdown_history': drawdown_series.to_dict() if 'drawdown_series' in locals() else {},
            'trades': self.trades
        }
        
        return performance
    
    def _calculate_max_consecutive_wins(self) -> int:
        """计算最大连续盈利次数"""
        if not self.trades:
            return 0
            
        max_wins = 0
        current_wins = 0
        
        for trade in self.trades:
            if trade['action'] == 'sell':
                if trade.get('proceeds', 0) > trade.get('cost', 0):
                    current_wins += 1
                    max_wins = max(max_wins, current_wins)
                else:
                    current_wins = 0
                    
        return max_wins
    
    def _calculate_max_consecutive_losses(self) -> int:
        """计算最大连续亏损次数"""
        if not self.trades:
            return 0
            
        max_losses = 0
        current_losses = 0
        
        for trade in self.trades:
            if trade['action'] == 'sell':
                if trade.get('proceeds', 0) < trade.get('cost', 0):
                    current_losses += 1
                    max_losses = max(max_losses, current_losses)
                else:
                    current_losses = 0
                    
        return max_losses

class ParameterOptimizer:
    """参数优化器"""
    
    def __init__(self, engine: BacktestingEngine):
        self.engine = engine
        
    def grid_search(self, strategy_class, data: pd.DataFrame,
                   param_grid: Dict[str, List[Any]], 
                   optimization_metric: str = 'sharpe_ratio') -> Dict[str, Any]:
        """
        网格搜索参数优化
        
        Args:
            strategy_class: 策略类
            data: 历史数据
            param_grid: 参数网格
            optimization_metric: 优化指标
            
        Returns:
            最优参数和结果
        """
        best_params = None
        best_result = None
        best_metric = -np.inf if optimization_metric != 'max_drawdown' else np.inf
        
        # 生成参数组合
        param_combinations = self._generate_param_combinations(param_grid)
        
        logger.info(f"开始网格搜索，共 {len(param_combinations)} 种参数组合")
        
        for i, params in enumerate(param_combinations):
            try:
                # 创建策略实例
                strategy = strategy_class(**params)
                
                # 运行回测
                result = self.engine.run_backtest(strategy, data)
                
                # 评估结果
                current_metric = result.get(optimization_metric, 0)
                
                # 更新最优结果
                if optimization_metric == 'max_drawdown':
                    if current_metric < best_metric:
                        best_metric = current_metric
                        best_params = params
                        best_result = result
                else:
                    if current_metric > best_metric:
                        best_metric = current_metric
                        best_params = params
                        best_result = result
                        
                if (i + 1) % 10 == 0:
                    logger.info(f"已完成 {i + 1}/{len(param_combinations)} 种组合")
                    
            except Exception as e:
                logger.warning(f"参数组合 {params} 执行失败: {str(e)}")
                continue
                
        logger.info(f"网格搜索完成，最优参数: {best_params}")
        
        return {
            'best_params': best_params,
            'best_result': best_result,
            'best_metric': best_metric,
            'total_combinations': len(param_combinations)
        }
    
    def _generate_param_combinations(self, param_grid: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """生成参数组合"""
        import itertools
        
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        
        combinations = []
        for combination in itertools.product(*values):
            param_dict = dict(zip(keys, combination))
            combinations.append(param_dict)
            
        return combinations