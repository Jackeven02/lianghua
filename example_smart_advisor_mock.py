"""
模拟数据提供者 - 用于测试
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from analysis_layer.technical_indicators import TechnicalIndicators


def generate_sample_data(stock_code: str, days: int = 120) -> pd.DataFrame:
    """
    生成示例数据
    """
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # 生成模拟价格数据
    np.random.seed(hash(stock_code) % 2**32)
    base_price = np.random.uniform(10, 100)
    
    # 生成随机游走价格
    returns = np.random.normal(0.001, 0.02, days)
    prices = base_price * np.exp(np.cumsum(returns))
    
    # 创建OHLCV数据
    data = pd.DataFrame({
        'date': dates,
        'open': prices * np.random.uniform(0.98, 1.02, days),
        'high': prices * np.random.uniform(1.00, 1.05, days),
        'low': prices * np.random.uniform(0.95, 1.00, days),
        'close': prices,
        'volume': np.random.uniform(1000000, 10000000, days)
    })
    
    return data


def generate_sample_fundamental() -> dict:
    """生成示例基本面数据"""
    return {
        'roe': np.random.uniform(8, 20),
        'revenue_growth': np.random.uniform(-5, 30),
        'profit_growth': np.random.uniform(-10, 40),
        'pe_ratio': np.random.uniform(10, 50),
        'pb_ratio': np.random.uniform(1, 6),
        'debt_ratio': np.random.uniform(0.2, 0.7),
        'current_ratio': np.random.uniform(0.8, 2.5)
    }


class MockDataProvider:
    """模拟数据提供者（用于测试）"""
    
    def get_stock_data(self, stock_code: str) -> pd.DataFrame:
        """获取股票数据"""
        # 生成原始数据
        data = generate_sample_data(stock_code)
        
        # 计算技术指标
        data_with_indicators = TechnicalIndicators.calculate_all_indicators(data)
        
        return data_with_indicators
    
    def get_fundamental_data(self, stock_code: str) -> dict:
        """获取基本面数据"""
        return generate_sample_fundamental()
