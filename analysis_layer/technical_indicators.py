"""
技术指标计算模块
提供各种技术分析指标的计算功能
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """技术指标计算类"""
    
    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """计算简单移动平均线 (SMA)"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """计算指数移动平均线 (EMA)"""
        return data.ewm(span=period).mean()
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, 
                      signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算MACD指标
        
        Returns:
            (MACD线, 信号线, 柱状图)
        """
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """计算相对强弱指数 (RSI)"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20, 
                                std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算布林带
        
        Returns:
            (上轨, 中轨, 下轨)
        """
        middle_band = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def calculate_kdj(high: pd.Series, low: pd.Series, close: pd.Series,
                     n: int = 9, m1: int = 3, m2: int = 3) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算KDJ指标
        
        Returns:
            (K值, D值, J值)
        """
        # 计算RSV
        low_min = low.rolling(window=n).min()
        high_max = high.rolling(window=n).max()
        rsv = (close - low_min) / (high_max - low_min) * 100
        
        # 计算K值
        k = rsv.ewm(alpha=1/m1).mean()
        # 计算D值
        d = k.ewm(alpha=1/m2).mean()
        # 计算J值
        j = 3 * k - 2 * d
        
        return k, d, j
    
    @staticmethod
    def calculate_cci(high: pd.Series, low: pd.Series, close: pd.Series,
                     period: int = 20) -> pd.Series:
        """计算商品通道指数 (CCI)"""
        # 计算典型价格
        tp = (high + low + close) / 3
        
        # 计算MA
        ma = tp.rolling(window=period).mean()
        
        # 计算平均绝对偏差
        md = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        
        # 计算CCI
        cci = (tp - ma) / (0.015 * md)
        return cci
    
    @staticmethod
    def calculate_roc(data: pd.Series, period: int = 12) -> pd.Series:
        """计算变动率指标 (ROC)"""
        return (data - data.shift(period)) / data.shift(period) * 100
    
    @staticmethod
    def calculate_williams_r(high: pd.Series, low: pd.Series, close: pd.Series,
                           period: int = 14) -> pd.Series:
        """计算威廉指标 (WR)"""
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        wr = (highest_high - close) / (highest_high - lowest_low) * -100
        return wr
    
    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """计算能量潮指标 (OBV)"""
        obv = pd.Series(index=close.index, dtype='float64')
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
                
        return obv
    
    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series,
                     period: int = 14) -> pd.Series:
        """计算平均真实波幅 (ATR)"""
        # 计算真实波幅
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # 计算ATR
        atr = tr.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series,
                     period: int = 14) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        计算平均趋向指数 (ADX)
        
        Returns:
            (ADX, +DI, -DI)
        """
        # 计算真实波幅
        tr = TechnicalIndicators._calculate_tr(high, low, close)
        
        # 计算方向运动
        up_move = high - high.shift(1)
        down_move = low.shift(1) - low
        
        # 计算+DM和-DM
        plus_dm = pd.Series(0, index=high.index)
        minus_dm = pd.Series(0, index=high.index)
        
        plus_dm[(up_move > down_move) & (up_move > 0)] = up_move
        minus_dm[(down_move > up_move) & (down_move > 0)] = down_move
        
        # 计算+DI和-DI
        plus_di = 100 * (plus_dm.rolling(period).mean() / tr.rolling(period).mean())
        minus_di = 100 * (minus_dm.rolling(period).mean() / tr.rolling(period).mean())
        
        # 计算DX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        
        # 计算ADX
        adx = dx.rolling(period).mean()
        
        return adx, plus_di, minus_di
    
    @staticmethod
    def calculate_all_indicators(data: pd.DataFrame) -> pd.DataFrame:
        """
        计算所有技术指标
        
        Args:
            data: 包含价格数据的DataFrame，必须包含open, high, low, close, volume列
            
        Returns:
            包含所有技术指标的DataFrame
        """
        if data.empty:
            return data
            
        result = data.copy()
        
        try:
            # 确保必要的列存在
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in data.columns for col in required_columns):
                logger.warning("数据缺少必要的价格列")
                return result
                
            close = data['close']
            high = data['high']
            low = data['low']
            volume = data['volume']
            
            # 计算移动平均线
            result['SMA_5'] = TechnicalIndicators.calculate_sma(close, 5)
            result['SMA_10'] = TechnicalIndicators.calculate_sma(close, 10)
            result['SMA_20'] = TechnicalIndicators.calculate_sma(close, 20)
            result['SMA_30'] = TechnicalIndicators.calculate_sma(close, 30)
            result['SMA_60'] = TechnicalIndicators.calculate_sma(close, 60)
            
            result['EMA_5'] = TechnicalIndicators.calculate_ema(close, 5)
            result['EMA_10'] = TechnicalIndicators.calculate_ema(close, 10)
            result['EMA_20'] = TechnicalIndicators.calculate_ema(close, 20)
            result['EMA_30'] = TechnicalIndicators.calculate_ema(close, 30)
            result['EMA_60'] = TechnicalIndicators.calculate_ema(close, 60)
            
            # 计算MACD
            macd_line, signal_line, histogram = TechnicalIndicators.calculate_macd(close)
            result['MACD'] = macd_line
            result['MACD_signal'] = signal_line
            result['MACD_histogram'] = histogram
            
            # 计算RSI
            result['RSI_6'] = TechnicalIndicators.calculate_rsi(close, 6)
            result['RSI_12'] = TechnicalIndicators.calculate_rsi(close, 12)
            result['RSI_14'] = TechnicalIndicators.calculate_rsi(close, 14)
            result['RSI_24'] = TechnicalIndicators.calculate_rsi(close, 24)
            
            # 计算布林带
            bb_upper, bb_middle, bb_lower = TechnicalIndicators.calculate_bollinger_bands(close)
            result['BB_upper'] = bb_upper
            result['BB_middle'] = bb_middle
            result['BB_lower'] = bb_lower
            result['BB_width'] = (bb_upper - bb_lower) / bb_middle
            
            # 计算KDJ
            k, d, j = TechnicalIndicators.calculate_kdj(high, low, close)
            result['K'] = k
            result['D'] = d
            result['J'] = j
            
            # 计算CCI
            result['CCI'] = TechnicalIndicators.calculate_cci(high, low, close)
            
            # 计算ROC
            result['ROC_6'] = TechnicalIndicators.calculate_roc(close, 6)
            result['ROC_12'] = TechnicalIndicators.calculate_roc(close, 12)
            
            # 计算威廉指标
            result['WR'] = TechnicalIndicators.calculate_williams_r(high, low, close)
            
            # 计算OBV
            result['OBV'] = TechnicalIndicators.calculate_obv(close, volume)
            
            # 计算ATR
            result['ATR'] = TechnicalIndicators.calculate_atr(high, low, close)
            
            # 计算ADX
            adx, plus_di, minus_di = TechnicalIndicators.calculate_adx(high, low, close)
            result['ADX'] = adx
            result['+DI'] = plus_di
            result['-DI'] = minus_di
            
            logger.info("所有技术指标计算完成")
            
        except Exception as e:
            logger.error(f"计算技术指标时出错: {str(e)}")
            
        return result
    
    @staticmethod
    def _calculate_tr(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
        """计算真实波幅 (True Range)"""
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    @staticmethod
    def get_indicator_signals(data: pd.DataFrame) -> Dict[str, List[str]]:
        """
        根据技术指标生成交易信号
        
        Args:
            data: 包含技术指标的数据
            
        Returns:
            交易信号字典
        """
        signals = {
            'buy_signals': [],
            'sell_signals': [],
            'neutral_signals': []
        }
        
        if data.empty:
            return signals
            
        try:
            latest = data.iloc[-1]
            
            # MACD信号
            if 'MACD' in data.columns and 'MACD_signal' in data.columns:
                if latest['MACD'] > latest['MACD_signal']:
                    signals['buy_signals'].append('MACD金叉')
                elif latest['MACD'] < latest['MACD_signal']:
                    signals['sell_signals'].append('MACD死叉')
            
            # RSI信号
            if 'RSI_14' in data.columns:
                if latest['RSI_14'] < 30:
                    signals['buy_signals'].append('RSI超卖')
                elif latest['RSI_14'] > 70:
                    signals['sell_signals'].append('RSI超买')
            
            # 布林带信号
            if all(col in data.columns for col in ['close', 'BB_upper', 'BB_lower']):
                if latest['close'] < latest['BB_lower']:
                    signals['buy_signals'].append('价格跌破布林下轨')
                elif latest['close'] > latest['BB_upper']:
                    signals['sell_signals'].append('价格突破布林上轨')
            
            # KDJ信号
            if all(col in data.columns for col in ['K', 'D', 'J']):
                if latest['K'] < 20 and latest['D'] < 20:
                    signals['buy_signals'].append('KDJ超卖')
                elif latest['K'] > 80 and latest['D'] > 80:
                    signals['sell_signals'].append('KDJ超买')
            
            logger.info("交易信号生成完成")
            
        except Exception as e:
            logger.error(f"生成交易信号时出错: {str(e)}")
            
        return signals