"""
统计分析模块
提供金融数据分析的统计方法
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class StatisticalAnalysis:
    """统计分析类"""
    
    @staticmethod
    def calculate_returns(data: pd.Series, return_type: str = 'simple') -> pd.Series:
        """
        计算收益率
        
        Args:
            data: 价格数据
            return_type: 收益率类型 ('simple', 'log')
            
        Returns:
            收益率序列
        """
        if return_type == 'simple':
            returns = data.pct_change()
        elif return_type == 'log':
            returns = np.log(data / data.shift(1))
        else:
            raise ValueError("return_type must be 'simple' or 'log'")
            
        return returns.dropna()
    
    @staticmethod
    def calculate_descriptive_stats(returns: pd.Series) -> Dict[str, float]:
        """
        计算描述性统计
        
        Args:
            returns: 收益率序列
            
        Returns:
            统计指标字典
        """
        stats_dict = {
            'mean': returns.mean(),
            'std': returns.std(),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis(),
            'min': returns.min(),
            'max': returns.max(),
            'median': returns.median(),
            'q25': returns.quantile(0.25),
            'q75': returns.quantile(0.75)
        }
        
        return stats_dict
    
    @staticmethod
    def calculate_volatility(returns: pd.Series, window: int = 252) -> float:
        """
        计算波动率
        
        Args:
            returns: 收益率序列
            window: 年化窗口天数
            
        Returns:
            年化波动率
        """
        daily_vol = returns.std()
        annualized_vol = daily_vol * np.sqrt(window)
        return annualized_vol
    
    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02,
                             window: int = 252) -> float:
        """
        计算夏普比率
        
        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率
            window: 年化窗口天数
            
        Returns:
            夏普比率
        """
        excess_return = returns.mean() - risk_free_rate / window
        volatility = returns.std()
        
        if volatility == 0:
            return 0
            
        sharpe_ratio = excess_return / volatility * np.sqrt(window)
        return sharpe_ratio
    
    @staticmethod
    def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.02,
                              window: int = 252) -> float:
        """
        计算索提诺比率
        
        Args:
            returns: 收益率序列
            risk_free_rate: 无风险利率
            window: 年化窗口天数
            
        Returns:
            索提诺比率
        """
        excess_return = returns.mean() - risk_free_rate / window
        downside_returns = returns[returns < 0]
        downside_vol = downside_returns.std()
        
        if downside_vol == 0:
            return 0
            
        sortino_ratio = excess_return / downside_vol * np.sqrt(window)
        return sortino_ratio
    
    @staticmethod
    def calculate_max_drawdown(returns: pd.Series) -> Tuple[float, pd.Series]:
        """
        计算最大回撤
        
        Args:
            returns: 收益率序列
            
        Returns:
            (最大回撤, 回撤序列)
        """
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return max_drawdown, drawdown
    
    @staticmethod
    def calculate_var(returns: pd.Series, confidence_level: float = 0.05) -> float:
        """
        计算风险价值 (VaR)
        
        Args:
            returns: 收益率序列
            confidence_level: 置信水平
            
        Returns:
            VaR值
        """
        var = returns.quantile(confidence_level)
        return var
    
    @staticmethod
    def calculate_cvar(returns: pd.Series, confidence_level: float = 0.05) -> float:
        """
        计算条件风险价值 (CVaR)
        
        Args:
            returns: 收益率序列
            confidence_level: 置信水平
            
        Returns:
            CVaR值
        """
        var = StatisticalAnalysis.calculate_var(returns, confidence_level)
        cvar = returns[returns <= var].mean()
        return cvar
    
    @staticmethod
    def calculate_correlation_matrix(data_dict: Dict[str, pd.Series]) -> pd.DataFrame:
        """
        计算相关性矩阵
        
        Args:
            data_dict: 数据字典 {名称: 数据序列}
            
        Returns:
            相关性矩阵
        """
        df = pd.DataFrame(data_dict)
        correlation_matrix = df.corr()
        return correlation_matrix
    
    @staticmethod
    def calculate_beta(returns: pd.Series, market_returns: pd.Series) -> float:
        """
        计算贝塔系数
        
        Args:
            returns: 资产收益率
            market_returns: 市场收益率
            
        Returns:
            贝塔系数
        """
        covariance = np.cov(returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 0
            
        beta = covariance / market_variance
        return beta
    
    @staticmethod
    def calculate_alpha(returns: pd.Series, market_returns: pd.Series,
                       risk_free_rate: float = 0.02, window: int = 252) -> float:
        """
        计算阿尔法系数
        
        Args:
            returns: 资产收益率
            market_returns: 市场收益率
            risk_free_rate: 无风险利率
            window: 年化窗口天数
            
        Returns:
            阿尔法系数
        """
        beta = StatisticalAnalysis.calculate_beta(returns, market_returns)
        asset_return = returns.mean() * window
        market_return = market_returns.mean() * window
        alpha = asset_return - (risk_free_rate + beta * (market_return - risk_free_rate))
        return alpha
    
    @staticmethod
    def perform_linear_regression(x: pd.Series, y: pd.Series) -> Dict[str, float]:
        """
        执行线性回归分析
        
        Args:
            x: 自变量
            y: 因变量
            
        Returns:
            回归结果字典
        """
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        results = {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value ** 2,
            'p_value': p_value,
            'std_error': std_err,
            'correlation': r_value
        }
        
        return results
    
    @staticmethod
    def calculate_performance_metrics(returns: pd.Series, 
                                    benchmark_returns: Optional[pd.Series] = None,
                                    risk_free_rate: float = 0.02) -> Dict[str, float]:
        """
        计算综合绩效指标
        
        Args:
            returns: 收益率序列
            benchmark_returns: 基准收益率序列
            risk_free_rate: 无风险利率
            
        Returns:
            绩效指标字典
        """
        metrics = {}
        
        try:
            # 基础统计
            metrics.update(StatisticalAnalysis.calculate_descriptive_stats(returns))
            
            # 风险指标
            metrics['volatility'] = StatisticalAnalysis.calculate_volatility(returns)
            metrics['max_drawdown'] = StatisticalAnalysis.calculate_max_drawdown(returns)[0]
            metrics['var_5%'] = StatisticalAnalysis.calculate_var(returns, 0.05)
            metrics['cvar_5%'] = StatisticalAnalysis.calculate_cvar(returns, 0.05)
            
            # 风险调整收益
            metrics['sharpe_ratio'] = StatisticalAnalysis.calculate_sharpe_ratio(returns, risk_free_rate)
            metrics['sortino_ratio'] = StatisticalAnalysis.calculate_sortino_ratio(returns, risk_free_rate)
            
            # 相对指标（如果有基准）
            if benchmark_returns is not None:
                metrics['beta'] = StatisticalAnalysis.calculate_beta(returns, benchmark_returns)
                metrics['alpha'] = StatisticalAnalysis.calculate_alpha(returns, benchmark_returns, risk_free_rate)
                metrics['tracking_error'] = (returns - benchmark_returns).std()
                metrics['information_ratio'] = (returns - benchmark_returns).mean() / metrics['tracking_error']
            
            # 收益率统计
            metrics['total_return'] = (1 + returns).prod() - 1
            metrics['annual_return'] = (1 + metrics['total_return']) ** (252 / len(returns)) - 1
            metrics['win_rate'] = (returns > 0).mean()
            metrics['profit_factor'] = returns[returns > 0].sum() / abs(returns[returns < 0].sum())
            
            logger.info("绩效指标计算完成")
            
        except Exception as e:
            logger.error(f"计算绩效指标时出错: {str(e)}")
            
        return metrics
    
    @staticmethod
    def analyze_distribution(returns: pd.Series) -> Dict[str, float]:
        """
        分析收益率分布特征
        
        Args:
            returns: 收益率序列
            
        Returns:
            分布特征字典
        """
        # 正态性检验
        shapiro_stat, shapiro_p = stats.shapiro(returns)
        
        # 峰度和偏度检验
        skewness = returns.skew()
        kurtosis = returns.kurtosis()
        
        # Jarque-Bera检验
        jb_stat, jb_p = stats.jarque_bera(returns)
        
        distribution_stats = {
            'shapiro_statistic': shapiro_stat,
            'shapiro_p_value': shapiro_p,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'jb_statistic': jb_stat,
            'jb_p_value': jb_p,
            'is_normal': shapiro_p > 0.05
        }
        
        return distribution_stats