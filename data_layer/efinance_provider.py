# -*- coding: utf-8 -*-
"""
efinance数据提供者
使用efinance库获取真实的市场数据
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

# 添加efinance路径
efinance_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'efinance')
if efinance_path not in sys.path:
    sys.path.insert(0, efinance_path)

try:
    import efinance as ef
except ImportError:
    print("警告: 无法导入efinance库，请确保已安装")
    ef = None

from analysis_layer.technical_indicators import TechnicalIndicators

logger = logging.getLogger(__name__)


class EFinanceProvider:
    """efinance数据提供者"""
    
    def __init__(self):
        """初始化数据提供者"""
        if ef is None:
            raise ImportError("efinance库未安装，请先安装: pip install efinance")
        
        self.cache = {}
        self.cache_timeout = 300
        
    def get_stock_data(self, stock_code: str, days: int = 120, klt: int = 101) -> pd.DataFrame:
        """
        获取股票历史数据并计算技术指标
        
        Parameters:
        -----------
        stock_code : str
            股票代码
        days : int
            获取天数（对于分钟数据，表示获取的数据条数）
        klt : int
            K线类型
            - 1: 1分钟
            - 5: 5分钟
            - 15: 15分钟
            - 30: 30分钟
            - 60: 60分钟
            - 101: 日线（默认）
            - 102: 周线
            - 103: 月线
        """
        try:
            cache_key = f"stock_{stock_code}_{days}_{klt}"
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                # 分钟数据缓存时间更短（1分钟），日线数据5分钟
                cache_timeout = 60 if klt < 101 else self.cache_timeout
                if (datetime.now() - cached_time).seconds < cache_timeout:
                    logger.info(f"使用缓存数据: {stock_code} (klt={klt})")
                    return cached_data
            
            logger.info(f"获取股票数据: {stock_code} (klt={klt})")
            
            # 获取指定频率的K线数据
            df = ef.stock.get_quote_history(stock_code, klt=klt)
            
            if df is None or df.empty:
                logger.warning(f"无法获取 {stock_code} 的数据")
                return pd.DataFrame()
            
            df = self._preprocess_stock_data(df)
            
            # 限制数据条数
            if len(df) > days:
                df = df.iloc[-days:].copy()
            
            df_with_indicators = TechnicalIndicators.calculate_all_indicators(df)
            
            self.cache[cache_key] = (df_with_indicators, datetime.now())
            
            logger.info(f"成功获取 {stock_code} 数据，共 {len(df_with_indicators)} 条 (klt={klt})")
            
            return df_with_indicators
            
        except Exception as e:
            logger.error(f"获取股票数据失败 {stock_code}: {str(e)}")
            return pd.DataFrame()

    def _preprocess_stock_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """预处理股票数据，统一列名"""
        column_mapping = {
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount',
            '涨跌幅': 'change_pct',
            '涨跌额': 'change',
            '换手率': 'turnover'
        }
        
        df = df.rename(columns=column_mapping)
        
        required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                logger.warning(f"缺少必要列: {col}")
                return pd.DataFrame()
        
        df['date'] = pd.to_datetime(df['date'])
        
        price_columns = ['open', 'high', 'low', 'close']
        for col in price_columns:
            if col in df.columns:
                df[col] = df[col].abs()
        
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def get_fundamental_data(self, stock_code: str) -> Dict:
        """获取基本面数据"""
        try:
            cache_key = f"fundamental_{stock_code}"
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if (datetime.now() - cached_time).seconds < self.cache_timeout:
                    return cached_data
            
            logger.info(f"获取基本面数据: {stock_code}")
            
            try:
                performance_df = ef.stock.get_all_company_performance()
                
                if performance_df is not None and not performance_df.empty:
                    stock_data = performance_df[performance_df['股票代码'] == stock_code]
                    
                    if not stock_data.empty:
                        row = stock_data.iloc[0]
                        
                        fundamental = {
                            'roe': self._safe_float(row.get('净资产收益率', 0)),
                            'revenue_growth': self._safe_float(row.get('营业收入同比增长', 0)),
                            'profit_growth': self._safe_float(row.get('净利润同比增长', 0)),
                            'pe_ratio': 0,
                            'pb_ratio': 0,
                            'debt_ratio': 0,
                            'current_ratio': 0,
                            'eps': self._safe_float(row.get('每股收益', 0)),
                            'bps': self._safe_float(row.get('每股净资产', 0)),
                            'gross_margin': self._safe_float(row.get('销售毛利率', 0)),
                        }
                        
                        self.cache[cache_key] = (fundamental, datetime.now())
                        
                        logger.info(f"成功获取 {stock_code} 基本面数据")
                        return fundamental
            except Exception as e:
                logger.warning(f"获取业绩数据失败: {str(e)}")
            
            logger.warning(f"无法获取 {stock_code} 的基本面数据，使用默认值")
            return self._get_default_fundamental()
            
        except Exception as e:
            logger.error(f"获取基本面数据失败 {stock_code}: {str(e)}")
            return self._get_default_fundamental()
    
    def _safe_float(self, value, default=0.0) -> float:
        """安全转换为浮点数"""
        try:
            if pd.isna(value):
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _get_default_fundamental(self) -> Dict:
        """返回默认基本面数据"""
        return {
            'roe': 10.0,
            'revenue_growth': 5.0,
            'profit_growth': 5.0,
            'pe_ratio': 20.0,
            'pb_ratio': 2.0,
            'debt_ratio': 0.5,
            'current_ratio': 1.5,
            'eps': 1.0,
            'bps': 10.0,
            'gross_margin': 20.0,
        }

    def get_realtime_quotes(self, stock_codes: List[str] = None) -> pd.DataFrame:
        """获取实时行情"""
        try:
            logger.info("获取实时行情...")
            
            df = ef.stock.get_realtime_quotes()
            
            if df is None or df.empty:
                logger.warning("无法获取实时行情")
                return pd.DataFrame()
            
            if stock_codes:
                df = df[df['股票代码'].isin(stock_codes)]
            
            logger.info(f"成功获取 {len(df)} 只股票的实时行情")
            
            return df
            
        except Exception as e:
            logger.error(f"获取实时行情失败: {str(e)}")
            return pd.DataFrame()
    
    def get_stock_list(self, market: str = "沪深A股") -> List[Tuple[str, str]]:
        """获取股票列表"""
        try:
            logger.info(f"获取{market}股票列表...")
            
            df = self.get_realtime_quotes()
            
            if df.empty:
                return []
            
            if market == "沪A":
                df = df[df['股票代码'].str.startswith('6')]
            elif market == "深A":
                df = df[df['股票代码'].str.startswith(('0', '3'))]
            elif market == "创业板":
                df = df[df['股票代码'].str.startswith('3')]
            elif market == "科创板":
                df = df[df['股票代码'].str.startswith('688')]
            
            stock_list = list(zip(df['股票代码'].tolist(), df['股票名称'].tolist()))
            
            logger.info(f"获取到 {len(stock_list)} 只{market}股票")
            
            return stock_list
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {str(e)}")
            return []
    
    def get_hot_stocks(self, top_n: int = 50) -> List[Tuple[str, str]]:
        """获取热门股票（按成交额排序）"""
        try:
            logger.info(f"获取热门股票 Top {top_n}...")
            
            df = self.get_realtime_quotes()
            
            if df.empty:
                return []
            
            if '成交额' in df.columns:
                df = df.sort_values('成交额', ascending=False)
            
            df = df.head(top_n)
            
            stock_list = list(zip(df['股票代码'].tolist(), df['股票名称'].tolist()))
            
            logger.info(f"获取到 {len(stock_list)} 只热门股票")
            
            return stock_list
            
        except Exception as e:
            logger.error(f"获取热门股票失败: {str(e)}")
            return []
    
    def get_stock_info(self, stock_code: str) -> Dict:
        """获取股票基本信息"""
        try:
            logger.info(f"获取股票信息: {stock_code}")
            
            df = self.get_realtime_quotes([stock_code])
            
            if df.empty:
                return {}
            
            row = df.iloc[0]
            
            info = {
                'code': stock_code,
                'name': row.get('股票名称', ''),
                'price': self._safe_float(row.get('最新价', 0)),
                'change_pct': self._safe_float(row.get('涨跌幅', 0)),
                'volume': self._safe_float(row.get('成交量', 0)),
                'amount': self._safe_float(row.get('成交额', 0)),
                'turnover': self._safe_float(row.get('换手率', 0)),
                'market_value': self._safe_float(row.get('总市值', 0)),
                'pe_ratio': self._safe_float(row.get('动态市盈率', 0)),
            }
            
            return info
            
        except Exception as e:
            logger.error(f"获取股票信息失败 {stock_code}: {str(e)}")
            return {}
    
    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()
        logger.info("缓存已清除")


def get_provider() -> EFinanceProvider:
    """获取默认数据提供者"""
    return EFinanceProvider()
