"""
数据处理器模块
负责数据清洗、转换和特征工程
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """数据处理器类"""
    
    def __init__(self):
        pass
    
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        数据清洗
        
        Args:
            data: 原始数据
            
        Returns:
            清洗后的数据
        """
        if data.empty:
            return data
            
        # 删除重复数据
        data = data.drop_duplicates()
        
        # 处理缺失值
        data = self._handle_missing_values(data)
        
        # 处理异常值
        data = self._handle_outliers(data)
        
        logger.info(f"数据清洗完成，原始数据 {len(data)} 条记录")
        return data
    
    def add_technical_indicators(self, data: pd.DataFrame, 
                               indicators: List[str] = None) -> pd.DataFrame:
        """
        添加技术指标
        
        Args:
            data: 价格数据
            indicators: 要计算的指标列表
            
        Returns:
            包含技术指标的数据
        """
        if data.empty:
            return data
            
        if indicators is None:
            indicators = ['SMA', 'EMA', 'MACD', 'RSI', 'BOLL']
            
        # 确保数据按日期排序
        if 'date' in data.columns:
            data = data.sort_values('date')
            
        # 计算各种技术指标
        for indicator in indicators:
            try:
                if indicator == 'SMA':
                    data = self._calculate_sma(data)
                elif indicator == 'EMA':
                    data = self._calculate_ema(data)
                elif indicator == 'MACD':
                    data = self._calculate_macd(data)
                elif indicator == 'RSI':
                    data = self._calculate_rsi(data)
                elif indicator == 'BOLL':
                    data = self._calculate_bollinger_bands(data)
                elif indicator == 'KDJ':
                    data = self._calculate_kdj(data)
                elif indicator == 'CCI':
                    data = self._calculate_cci(data)
                elif indicator == 'ROC':
                    data = self._calculate_roc(data)
                    
            except Exception as e:
                logger.warning(f"计算指标 {indicator} 时出错: {str(e)}")
                continue
                
        logger.info(f"技术指标计算完成，添加了 {len(indicators)} 个指标")
        return data
    
    def resample_data(self, data: pd.DataFrame, frequency: str) -> pd.DataFrame:
        """
        数据重采样
        
        Args:
            data: 原始数据
            frequency: 重采样频率 ('D', 'W', 'M', 'H', etc.)
            
        Returns:
            重采样后的数据
        """
        if data.empty or 'date' not in data.columns:
            return data
            
        try:
            # 设置日期为索引
            data_indexed = data.set_index('date')
            
            # 重采样
            resampled = data_indexed.resample(frequency).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'amount': 'sum'
            })
            
            # 重置索引
            resampled = resampled.reset_index()
            resampled = resampled.dropna()
            
            logger.info(f"数据重采样完成，频率: {frequency}")
            return resampled
            
        except Exception as e:
            logger.error(f"数据重采样失败: {str(e)}")
            return data
    
    def calculate_returns(self, data: pd.DataFrame, 
                         return_type: str = 'simple') -> pd.DataFrame:
        """
        计算收益率
        
        Args:
            data: 价格数据
            return_type: 收益率类型 ('simple', 'log')
            
        Returns:
            包含收益率的数据
        """
        if data.empty or 'close' not in data.columns:
            return data
            
        try:
            if return_type == 'simple':
                data['simple_return'] = data['close'].pct_change()
            elif return_type == 'log':
                data['log_return'] = np.log(data['close'] / data['close'].shift(1))
                
            logger.info(f"收益率计算完成，类型: {return_type}")
            return data
            
        except Exception as e:
            logger.error(f"收益率计算失败: {str(e)}")
            return data
    
    def _handle_missing_values(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理缺失值"""
        # 对于数值列，使用前向填充
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        data[numeric_columns] = data[numeric_columns].fillna(method='ffill')
        
        # 删除仍然有缺失值的行
        data = data.dropna()
        
        return data
    
    def _handle_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理异常值"""
        # 使用IQR方法处理异常值
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if col in ['open', 'high', 'low', 'close']:
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # 将异常值替换为边界值
                data[col] = data[col].clip(lower=lower_bound, upper=upper_bound)
                
        return data
    
    def _calculate_sma(self, data: pd.DataFrame, periods: List[int] = None) -> pd.DataFrame:
        """计算简单移动平均线"""
        if periods is None:
            periods = [5, 10, 20, 30, 60]
            
        for period in periods:
            if 'close' in data.columns:
                data[f'SMA_{period}'] = data['close'].rolling(window=period).mean()
                
        return data
    
    def _calculate_ema(self, data: pd.DataFrame, periods: List[int] = None) -> pd.DataFrame:
        """计算指数移动平均线"""
        if periods is None:
            periods = [5, 10, 20, 30, 60]
            
        for period in periods:
            if 'close' in data.columns:
                data[f'EMA_{period}'] = data['close'].ewm(span=period).mean()
                
        return data
    
    def _calculate_macd(self, data: pd.DataFrame, 
                       fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """计算MACD指标"""
        if 'close' not in data.columns:
            return data
            
        ema_fast = data['close'].ewm(span=fast).mean()
        ema_slow = data['close'].ewm(span=slow).mean()
        
        data['MACD'] = ema_fast - ema_slow
        data['MACD_signal'] = data['MACD'].ewm(span=signal).mean()
        data['MACD_histogram'] = data['MACD'] - data['MACD_signal']
        
        return data
    
    def _calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """计算RSI指标"""
        if 'close' not in data.columns:
            return data
            
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        return data
    
    def _calculate_bollinger_bands(self, data: pd.DataFrame, 
                                 period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """计算布林带"""
        if 'close' not in data.columns:
            return data
            
        sma = data['close'].rolling(window=period).mean()
        std = data['close'].rolling(window=period).std()
        
        data['BB_upper'] = sma + (std * std_dev)
        data['BB_middle'] = sma
        data['BB_lower'] = sma - (std * std_dev)
        data['BB_width'] = (data['BB_upper'] - data['BB_lower']) / sma
        
        return data
    
    def _calculate_kdj(self, data: pd.DataFrame, 
                      n: int = 9, m1: int = 3, m2: int = 3) -> pd.DataFrame:
        """计算KDJ指标"""
        if not all(col in data.columns for col in ['high', 'low', 'close']):
            return data
            
        # 计算RSV
        low_min = data['low'].rolling(window=n).min()
        high_max = data['high'].rolling(window=n).max()
        data['RSV'] = (data['close'] - low_min) / (high_max - low_min) * 100
        
        # 计算K值
        data['K'] = data['RSV'].ewm(alpha=1/m1).mean()
        # 计算D值
        data['D'] = data['K'].ewm(alpha=1/m2).mean()
        # 计算J值
        data['J'] = 3 * data['K'] - 2 * data['D']
        
        return data
    
    def _calculate_cci(self, data: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """计算CCI指标"""
        if not all(col in data.columns for col in ['high', 'low', 'close']):
            return data
            
        # 计算典型价格
        tp = (data['high'] + data['low'] + data['close']) / 3
        
        # 计算MA
        ma = tp.rolling(window=period).mean()
        
        # 计算平均绝对偏差
        md = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        
        # 计算CCI
        data['CCI'] = (tp - ma) / (0.015 * md)
        
        return data
    
    def _calculate_roc(self, data: pd.DataFrame, period: int = 12) -> pd.DataFrame:
        """计算ROC指标"""
        if 'close' not in data.columns:
            return data
            
        data['ROC'] = (data['close'] - data['close'].shift(period)) / data['close'].shift(period) * 100
        
        return data