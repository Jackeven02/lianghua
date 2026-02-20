"""
策略引擎模块
提供策略定义、执行和管理功能
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Strategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str, params: Dict[str, Any] = None):
        self.name = name
        self.params = params or {}
        self.signals = []
        self.positions = {}
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        生成交易信号
        
        Args:
            data: 市场数据
            
        Returns:
            交易信号字典
        """
        pass
    
    def get_name(self) -> str:
        """获取策略名称"""
        return self.name
    
    def get_params(self) -> Dict[str, Any]:
        """获取策略参数"""
        return self.params.copy()

class TechnicalStrategy(Strategy):
    """技术分析策略"""
    
    def __init__(self, name: str, indicators: List[str] = None, 
                 params: Dict[str, Any] = None):
        super().__init__(name, params)
        self.indicators = indicators or ['SMA', 'RSI', 'MACD']
        
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """基于技术指标生成信号"""
        if data.empty:
            return {'signal': 'hold', 'confidence': 0}
            
        signals = []
        confidence = 0
        
        # SMA策略
        if 'SMA' in self.indicators and 'SMA_5' in data.columns and 'SMA_20' in data.columns:
            latest = data.iloc[-1]
            if latest['SMA_5'] > latest['SMA_20']:
                signals.append('buy')
                confidence += 0.3
            elif latest['SMA_5'] < latest['SMA_20']:
                signals.append('sell')
                confidence += 0.3
                
        # RSI策略
        if 'RSI' in self.indicators and 'RSI_14' in data.columns:
            latest_rsi = data['RSI_14'].iloc[-1]
            if latest_rsi < 30:
                signals.append('buy')
                confidence += 0.2
            elif latest_rsi > 70:
                signals.append('sell')
                confidence += 0.2
                
        # MACD策略
        if 'MACD' in self.indicators and 'MACD' in data.columns and 'MACD_signal' in data.columns:
            latest = data.iloc[-1]
            if latest['MACD'] > latest['MACD_signal']:
                signals.append('buy')
                confidence += 0.25
            elif latest['MACD'] < latest['MACD_signal']:
                signals.append('sell')
                confidence += 0.25
                
        # 确定最终信号
        if signals.count('buy') > signals.count('sell'):
            final_signal = 'buy'
        elif signals.count('sell') > signals.count('buy'):
            final_signal = 'sell'
        else:
            final_signal = 'hold'
            
        confidence = min(confidence, 1.0)
        
        return {
            'signal': final_signal,
            'confidence': confidence,
            'indicators_used': self.indicators,
            'details': signals
        }

class MeanReversionStrategy(Strategy):
    """均值回归策略"""
    
    def __init__(self, name: str, window: int = 20, std_dev: float = 2.0,
                 params: Dict[str, Any] = None):
        super().__init__(name, params)
        self.window = window
        self.std_dev = std_dev
        
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """基于均值回归生成信号"""
        if len(data) < self.window:
            return {'signal': 'hold', 'confidence': 0}
            
        close_prices = data['close']
        current_price = close_prices.iloc[-1]
        
        # 计算移动平均和标准差
        ma = close_prices.rolling(window=self.window).mean().iloc[-1]
        std = close_prices.rolling(window=self.window).std().iloc[-1]
        
        upper_band = ma + (std * self.std_dev)
        lower_band = ma - (std * self.std_dev)
        
        # 生成信号
        if current_price < lower_band:
            signal = 'buy'
            confidence = min((lower_band - current_price) / std, 1.0)
        elif current_price > upper_band:
            signal = 'sell'
            confidence = min((current_price - upper_band) / std, 1.0)
        else:
            signal = 'hold'
            confidence = 0
            
        return {
            'signal': signal,
            'confidence': confidence,
            'upper_band': upper_band,
            'lower_band': lower_band,
            'moving_average': ma
        }

class MomentumStrategy(Strategy):
    """动量策略"""
    
    def __init__(self, name: str, lookback_period: int = 20,
                 params: Dict[str, Any] = None):
        super().__init__(name, params)
        self.lookback_period = lookback_period
        
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """基于动量生成信号"""
        if len(data) < self.lookback_period:
            return {'signal': 'hold', 'confidence': 0}
            
        close_prices = data['close']
        returns = close_prices.pct_change().dropna()
        
        # 计算动量
        momentum = (close_prices.iloc[-1] / close_prices.iloc[-self.lookback_period] - 1)
        
        # 生成信号
        if momentum > 0.05:  # 5%正动量
            signal = 'buy'
            confidence = min(momentum / 0.1, 1.0)  # 最大10%动量对应100%信心
        elif momentum < -0.05:  # 5%负动量
            signal = 'sell'
            confidence = min(abs(momentum) / 0.1, 1.0)
        else:
            signal = 'hold'
            confidence = 0
            
        return {
            'signal': signal,
            'confidence': confidence,
            'momentum': momentum,
            'lookback_period': self.lookback_period
        }

class StrategyEngine:
    """策略引擎类"""
    
    def __init__(self):
        self.strategies = {}
        self.active_strategy = None
        
    def register_strategy(self, strategy: Strategy):
        """注册策略"""
        self.strategies[strategy.get_name()] = strategy
        logger.info(f"策略 {strategy.get_name()} 已注册")
        
    def get_strategy(self, name: str) -> Optional[Strategy]:
        """获取策略"""
        return self.strategies.get(name)
        
    def get_all_strategies(self) -> List[str]:
        """获取所有策略名称"""
        return list(self.strategies.keys())
        
    def set_active_strategy(self, name: str):
        """设置活跃策略"""
        if name in self.strategies:
            self.active_strategy = name
            logger.info(f"活跃策略设置为: {name}")
        else:
            raise ValueError(f"策略 {name} 未注册")
            
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, Any]:
        """使用活跃策略生成信号"""
        if self.active_strategy is None:
            raise ValueError("未设置活跃策略")
            
        strategy = self.strategies[self.active_strategy]
        return strategy.generate_signals(data)
        
    def run_strategy_analysis(self, data: pd.DataFrame, 
                            strategy_names: List[str] = None) -> Dict[str, Any]:
        """
        运行多个策略分析
        
        Args:
            data: 市场数据
            strategy_names: 要分析的策略名称列表
            
        Returns:
            策略分析结果
        """
        if strategy_names is None:
            strategy_names = list(self.strategies.keys())
            
        results = {}
        
        for name in strategy_names:
            if name in self.strategies:
                try:
                    strategy = self.strategies[name]
                    signals = strategy.generate_signals(data)
                    results[name] = signals
                except Exception as e:
                    logger.error(f"策略 {name} 执行出错: {str(e)}")
                    results[name] = {'signal': 'error', 'error': str(e)}
            else:
                results[name] = {'signal': 'not_found', 'error': '策略未注册'}
                
        return results

# 预定义策略实例
def create_default_strategies() -> Dict[str, Strategy]:
    """创建默认策略"""
    strategies = {
        'sma_crossover': TechnicalStrategy(
            'SMA交叉策略',
            indicators=['SMA'],
            params={'fast_period': 5, 'slow_period': 20}
        ),
        'rsi_strategy': TechnicalStrategy(
            'RSI策略',
            indicators=['RSI'],
            params={'overbought': 70, 'oversold': 30}
        ),
        'macd_strategy': TechnicalStrategy(
            'MACD策略',
            indicators=['MACD'],
            params={'fast': 12, 'slow': 26, 'signal': 9}
        ),
        'mean_reversion': MeanReversionStrategy(
            '均值回归策略',
            window=20,
            std_dev=2.0
        ),
        'momentum': MomentumStrategy(
            '动量策略',
            lookback_period=20
        )
    }
    
    return strategies