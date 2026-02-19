"""
智能投资顾问模块
自动分析市场并提供投资建议
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SignalStrength(Enum):
    """信号强度枚举"""
    STRONG_BUY = "强烈买入"
    BUY = "买入"
    HOLD = "持有"
    SELL = "卖出"
    STRONG_SELL = "强烈卖出"


@dataclass
class InvestmentAdvice:
    """投资建议数据类"""
    stock_code: str
    stock_name: str
    signal: SignalStrength
    confidence: float  # 0-100
    current_price: float
    target_price: float
    stop_loss: float
    reasons: List[str]
    risk_level: str  # 低/中/高
    position_size: float  # 建议仓位比例
    time_horizon: str  # 短期/中期/长期
    technical_score: float
    fundamental_score: float
    sentiment_score: float
    overall_score: float
    timestamp: datetime


class SmartAdvisor:
    """智能投资顾问类"""
    
    def __init__(self, risk_tolerance: str = "中等"):
        """
        初始化智能顾问
        
        Args:
            risk_tolerance: 风险承受能力 (保守/中等/激进)
        """
        self.risk_tolerance = risk_tolerance
        self.min_confidence = 60  # 最低信心阈值
        
        # 风险参数配置
        self.risk_params = {
            "保守": {"max_position": 0.05, "stop_loss_pct": 0.05, "min_score": 75},
            "中等": {"max_position": 0.10, "stop_loss_pct": 0.08, "min_score": 65},
            "激进": {"max_position": 0.15, "stop_loss_pct": 0.12, "min_score": 55}
        }
        
    def analyze_stock(self, stock_code: str, stock_name: str, 
                     data: pd.DataFrame, 
                     fundamental_data: Optional[Dict] = None) -> InvestmentAdvice:
        """
        分析单只股票并生成投资建议
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            data: 历史价格数据（包含技术指标）
            fundamental_data: 基本面数据
            
        Returns:
            投资建议对象
        """
        if data.empty or len(data) < 60:
            logger.warning(f"{stock_code} 数据不足，无法分析")
            return None
            
        # 1. 技术面分析评分
        technical_score = self._analyze_technical(data)
        
        # 2. 基本面分析评分
        fundamental_score = self._analyze_fundamental(fundamental_data) if fundamental_data else 50
        
        # 3. 市场情绪分析评分
        sentiment_score = self._analyze_sentiment(data)
        
        # 4. 计算综合评分
        overall_score = self._calculate_overall_score(
            technical_score, fundamental_score, sentiment_score
        )
        
        # 5. 生成交易信号
        signal, confidence = self._generate_signal(overall_score, data)
        
        # 6. 计算目标价和止损价
        current_price = data['close'].iloc[-1]
        target_price, stop_loss = self._calculate_price_targets(
            current_price, signal, data
        )
        
        # 7. 生成建议理由
        reasons = self._generate_reasons(data, technical_score, fundamental_score, sentiment_score)
        
        # 8. 评估风险等级
        risk_level = self._assess_risk_level(data, overall_score)
        
        # 9. 计算建议仓位
        position_size = self._calculate_position_size(confidence, risk_level)
        
        # 10. 确定投资时间范围
        time_horizon = self._determine_time_horizon(signal, data)
        
        advice = InvestmentAdvice(
            stock_code=stock_code,
            stock_name=stock_name,
            signal=signal,
            confidence=confidence,
            current_price=current_price,
            target_price=target_price,
            stop_loss=stop_loss,
            reasons=reasons,
            risk_level=risk_level,
            position_size=position_size,
            time_horizon=time_horizon,
            technical_score=technical_score,
            fundamental_score=fundamental_score,
            sentiment_score=sentiment_score,
            overall_score=overall_score,
            timestamp=datetime.now()
        )
        
        return advice
    
    def _analyze_technical(self, data: pd.DataFrame) -> float:
        """
        技术面分析评分 (0-100)
        """
        score = 0
        max_score = 100
        latest = data.iloc[-1]
        
        try:
            # 1. 趋势分析 (30分)
            if 'SMA_5' in data.columns and 'SMA_20' in data.columns and 'SMA_60' in data.columns:
                if latest['SMA_5'] > latest['SMA_20'] > latest['SMA_60']:
                    score += 30  # 多头排列
                elif latest['SMA_5'] > latest['SMA_20']:
                    score += 20  # 短期上涨
                elif latest['SMA_5'] < latest['SMA_20'] < latest['SMA_60']:
                    score += 0   # 空头排列
                else:
                    score += 10  # 震荡
            
            # 2. MACD指标 (20分)
            if 'MACD' in data.columns and 'MACD_signal' in data.columns:
                macd_diff = latest['MACD'] - latest['MACD_signal']
                if macd_diff > 0:
                    if data['MACD'].iloc[-2] <= data['MACD_signal'].iloc[-2]:
                        score += 20  # 金叉
                    else:
                        score += 15  # 持续多头
                elif macd_diff < 0:
                    if data['MACD'].iloc[-2] >= data['MACD_signal'].iloc[-2]:
                        score += 0   # 死叉
                    else:
                        score += 5   # 持续空头
            
            # 3. RSI指标 (15分)
            if 'RSI_14' in data.columns:
                rsi = latest['RSI_14']
                if 30 < rsi < 70:
                    score += 15  # 正常区间
                elif 20 < rsi <= 30:
                    score += 12  # 接近超卖
                elif rsi <= 20:
                    score += 8   # 超卖（可能反弹）
                elif 70 <= rsi < 80:
                    score += 8   # 接近超买
                else:
                    score += 3   # 超买
            
            # 4. 布林带位置 (15分)
            if all(col in data.columns for col in ['close', 'BB_upper', 'BB_middle', 'BB_lower']):
                close = latest['close']
                bb_upper = latest['BB_upper']
                bb_middle = latest['BB_middle']
                bb_lower = latest['BB_lower']
                
                bb_position = (close - bb_lower) / (bb_upper - bb_lower)
                if 0.3 < bb_position < 0.7:
                    score += 15  # 中轨附近
                elif bb_position <= 0.2:
                    score += 12  # 下轨附近（可能反弹）
                elif bb_position >= 0.8:
                    score += 8   # 上轨附近（可能回调）
                else:
                    score += 10
            
            # 5. 成交量分析 (10分)
            if 'volume' in data.columns:
                recent_volume = data['volume'].iloc[-5:].mean()
                avg_volume = data['volume'].iloc[-60:].mean()
                volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
                
                if 1.2 < volume_ratio < 2.5:
                    score += 10  # 温和放量
                elif volume_ratio >= 2.5:
                    score += 7   # 巨量（需警惕）
                elif volume_ratio < 0.8:
                    score += 5   # 缩量
                else:
                    score += 8
            
            # 6. KDJ指标 (10分)
            if all(col in data.columns for col in ['K', 'D', 'J']):
                k, d, j = latest['K'], latest['D'], latest['J']
                if k > d and 20 < k < 80:
                    score += 10  # 金叉且在合理区间
                elif k < d and k > 20:
                    score += 5   # 死叉但未超卖
                elif k < 20:
                    score += 7   # 超卖区
                else:
                    score += 6
            
        except Exception as e:
            logger.error(f"技术分析出错: {str(e)}")
            score = 50  # 默认中性分数
        
        return min(score, max_score)
    
    def _analyze_fundamental(self, fundamental_data: Dict) -> float:
        """
        基本面分析评分 (0-100)
        """
        if not fundamental_data:
            return 50  # 无数据时返回中性分数
        
        score = 0
        
        try:
            # 1. 盈利能力 (30分)
            roe = fundamental_data.get('roe', 0)  # 净资产收益率
            if roe > 15:
                score += 30
            elif roe > 10:
                score += 20
            elif roe > 5:
                score += 10
            
            # 2. 成长性 (25分)
            revenue_growth = fundamental_data.get('revenue_growth', 0)  # 营收增长率
            profit_growth = fundamental_data.get('profit_growth', 0)    # 利润增长率
            
            if revenue_growth > 20 and profit_growth > 20:
                score += 25
            elif revenue_growth > 10 and profit_growth > 10:
                score += 18
            elif revenue_growth > 0 and profit_growth > 0:
                score += 10
            
            # 3. 估值水平 (25分)
            pe_ratio = fundamental_data.get('pe_ratio', 0)  # 市盈率
            pb_ratio = fundamental_data.get('pb_ratio', 0)  # 市净率
            
            if 0 < pe_ratio < 15 and 0 < pb_ratio < 2:
                score += 25  # 低估
            elif 15 <= pe_ratio < 30 and 2 <= pb_ratio < 4:
                score += 18  # 合理
            elif pe_ratio >= 30 or pb_ratio >= 4:
                score += 8   # 高估
            
            # 4. 财务健康 (20分)
            debt_ratio = fundamental_data.get('debt_ratio', 0)  # 资产负债率
            current_ratio = fundamental_data.get('current_ratio', 0)  # 流动比率
            
            if debt_ratio < 0.5 and current_ratio > 1.5:
                score += 20  # 财务健康
            elif debt_ratio < 0.7 and current_ratio > 1.0:
                score += 15  # 财务良好
            else:
                score += 8   # 财务一般
            
        except Exception as e:
            logger.error(f"基本面分析出错: {str(e)}")
            score = 50
        
        return min(score, 100)
    
    def _analyze_sentiment(self, data: pd.DataFrame) -> float:
        """
        市场情绪分析评分 (0-100)
        """
        score = 50  # 基础分数
        
        try:
            # 1. 价格动量
            if len(data) >= 20:
                returns_5d = (data['close'].iloc[-1] / data['close'].iloc[-5] - 1) * 100
                returns_20d = (data['close'].iloc[-1] / data['close'].iloc[-20] - 1) * 100
                
                if returns_5d > 5 and returns_20d > 10:
                    score += 25  # 强势上涨
                elif returns_5d > 0 and returns_20d > 0:
                    score += 15  # 温和上涨
                elif returns_5d < -5 and returns_20d < -10:
                    score -= 25  # 强势下跌
                elif returns_5d < 0 and returns_20d < 0:
                    score -= 15  # 温和下跌
            
            # 2. 波动率分析
            if 'ATR' in data.columns:
                recent_atr = data['ATR'].iloc[-5:].mean()
                avg_atr = data['ATR'].iloc[-60:].mean()
                
                if recent_atr < avg_atr * 0.8:
                    score += 10  # 波动率降低（稳定）
                elif recent_atr > avg_atr * 1.5:
                    score -= 10  # 波动率升高（风险）
            
            # 3. 趋势强度
            if 'ADX' in data.columns:
                adx = data['ADX'].iloc[-1]
                if adx > 25:
                    score += 15  # 趋势明显
                elif adx > 20:
                    score += 10  # 趋势一般
                else:
                    score += 5   # 无明显趋势
            
        except Exception as e:
            logger.error(f"情绪分析出错: {str(e)}")
        
        return max(0, min(score, 100))
    
    def _calculate_overall_score(self, technical: float, fundamental: float, 
                                sentiment: float) -> float:
        """
        计算综合评分
        权重: 技术40%, 基本面35%, 情绪25%
        """
        weights = {
            "保守": {"technical": 0.30, "fundamental": 0.50, "sentiment": 0.20},
            "中等": {"technical": 0.40, "fundamental": 0.35, "sentiment": 0.25},
            "激进": {"technical": 0.50, "fundamental": 0.25, "sentiment": 0.25}
        }
        
        w = weights.get(self.risk_tolerance, weights["中等"])
        overall = (technical * w["technical"] + 
                  fundamental * w["fundamental"] + 
                  sentiment * w["sentiment"])
        
        return round(overall, 2)
    
    def _generate_signal(self, overall_score: float, 
                        data: pd.DataFrame) -> Tuple[SignalStrength, float]:
        """
        根据综合评分生成交易信号
        """
        params = self.risk_params[self.risk_tolerance]
        min_score = params["min_score"]
        
        # 计算信心度
        confidence = min(overall_score, 100)
        
        # 生成信号
        if overall_score >= 80:
            signal = SignalStrength.STRONG_BUY
        elif overall_score >= min_score:
            signal = SignalStrength.BUY
        elif overall_score >= 45:
            signal = SignalStrength.HOLD
        elif overall_score >= 30:
            signal = SignalStrength.SELL
        else:
            signal = SignalStrength.STRONG_SELL
        
        return signal, confidence
    
    def _calculate_price_targets(self, current_price: float, 
                                signal: SignalStrength, 
                                data: pd.DataFrame) -> Tuple[float, float]:
        """
        计算目标价和止损价
        """
        params = self.risk_params[self.risk_tolerance]
        stop_loss_pct = params["stop_loss_pct"]
        
        # 计算ATR用于动态止损
        atr = data['ATR'].iloc[-1] if 'ATR' in data.columns else current_price * 0.02
        
        if signal in [SignalStrength.STRONG_BUY, SignalStrength.BUY]:
            # 买入信号
            target_price = current_price * (1 + stop_loss_pct * 3)  # 盈亏比3:1
            stop_loss = current_price * (1 - stop_loss_pct)
        elif signal in [SignalStrength.STRONG_SELL, SignalStrength.SELL]:
            # 卖出信号
            target_price = current_price * (1 - stop_loss_pct * 2)
            stop_loss = current_price * (1 + stop_loss_pct)
        else:
            # 持有信号
            target_price = current_price
            stop_loss = current_price * (1 - stop_loss_pct)
        
        return round(target_price, 2), round(stop_loss, 2)
    
    def _generate_reasons(self, data: pd.DataFrame, technical_score: float,
                         fundamental_score: float, sentiment_score: float) -> List[str]:
        """
        生成投资建议理由
        """
        reasons = []
        latest = data.iloc[-1]
        
        try:
            # 技术面理由
            if technical_score >= 70:
                if 'SMA_5' in data.columns and latest['SMA_5'] > latest['SMA_20']:
                    reasons.append("短期均线上穿长期均线，形成金叉")
                if 'MACD' in data.columns and latest['MACD'] > latest['MACD_signal']:
                    reasons.append("MACD指标显示多头信号")
                if 'RSI_14' in data.columns and 30 < latest['RSI_14'] < 70:
                    reasons.append("RSI处于健康区间，无超买超卖")
            elif technical_score < 40:
                if 'SMA_5' in data.columns and latest['SMA_5'] < latest['SMA_20']:
                    reasons.append("短期均线下穿长期均线，形成死叉")
                if 'RSI_14' in data.columns and latest['RSI_14'] > 70:
                    reasons.append("RSI超买，存在回调风险")
            
            # 基本面理由
            if fundamental_score >= 70:
                reasons.append("基本面优秀，盈利能力强")
            elif fundamental_score < 40:
                reasons.append("基本面较弱，需谨慎")
            
            # 情绪面理由
            if sentiment_score >= 70:
                reasons.append("市场情绪积极，资金流入")
            elif sentiment_score < 40:
                reasons.append("市场情绪低迷，资金流出")
            
            # 成交量理由
            if 'volume' in data.columns:
                recent_vol = data['volume'].iloc[-5:].mean()
                avg_vol = data['volume'].iloc[-60:].mean()
                if recent_vol > avg_vol * 1.5:
                    reasons.append("成交量放大，市场关注度高")
            
        except Exception as e:
            logger.error(f"生成理由时出错: {str(e)}")
            reasons.append("综合技术指标分析")
        
        return reasons if reasons else ["基于多维度量化分析"]
    
    def _assess_risk_level(self, data: pd.DataFrame, overall_score: float) -> str:
        """
        评估风险等级
        """
        risk_score = 0
        
        try:
            # 1. 波动率风险
            if 'ATR' in data.columns:
                atr_pct = data['ATR'].iloc[-1] / data['close'].iloc[-1]
                if atr_pct > 0.05:
                    risk_score += 2
                elif atr_pct > 0.03:
                    risk_score += 1
            
            # 2. 评分风险
            if overall_score < 50:
                risk_score += 2
            elif overall_score < 65:
                risk_score += 1
            
            # 3. 趋势风险
            if len(data) >= 20:
                returns = (data['close'].iloc[-1] / data['close'].iloc[-20] - 1)
                if abs(returns) > 0.2:
                    risk_score += 1
            
        except Exception as e:
            logger.error(f"风险评估出错: {str(e)}")
            return "中"
        
        if risk_score >= 4:
            return "高"
        elif risk_score >= 2:
            return "中"
        else:
            return "低"
    
    def _calculate_position_size(self, confidence: float, risk_level: str) -> float:
        """
        计算建议仓位比例
        """
        params = self.risk_params[self.risk_tolerance]
        max_position = params["max_position"]
        
        # 根据信心度调整
        base_position = max_position * (confidence / 100)
        
        # 根据风险等级调整
        risk_multiplier = {"低": 1.0, "中": 0.8, "高": 0.5}
        adjusted_position = base_position * risk_multiplier.get(risk_level, 0.8)
        
        return round(adjusted_position, 3)
    
    def _determine_time_horizon(self, signal: SignalStrength, 
                               data: pd.DataFrame) -> str:
        """
        确定投资时间范围
        """
        try:
            # 基于趋势强度判断
            if 'ADX' in data.columns:
                adx = data['ADX'].iloc[-1]
                if adx > 30:
                    return "中期"  # 强趋势适合中期持有
                elif adx > 20:
                    return "短期"  # 中等趋势适合短期
                else:
                    return "短期"  # 弱趋势快进快出
            
            # 基于信号类型判断
            if signal in [SignalStrength.STRONG_BUY, SignalStrength.STRONG_SELL]:
                return "中期"
            else:
                return "短期"
                
        except Exception as e:
            logger.error(f"时间范围判断出错: {str(e)}")
            return "短期"


class MarketScanner:
    """市场扫描器 - 自动扫描并筛选股票"""
    
    def __init__(self, advisor: SmartAdvisor):
        self.advisor = advisor
        
    def scan_market(self, stock_list: List[Tuple[str, str]], 
                   data_provider,
                   min_confidence: float = 60) -> List[InvestmentAdvice]:
        """
        扫描市场并生成投资建议列表
        
        Args:
            stock_list: 股票列表 [(代码, 名称), ...]
            data_provider: 数据提供者对象
            min_confidence: 最低信心阈值
            
        Returns:
            投资建议列表（按评分排序）
        """
        advice_list = []
        
        logger.info(f"开始扫描 {len(stock_list)} 只股票...")
        
        for stock_code, stock_name in stock_list:
            try:
                # 获取数据
                data = data_provider.get_stock_data(stock_code)
                fundamental = data_provider.get_fundamental_data(stock_code)
                
                # 分析股票
                advice = self.advisor.analyze_stock(
                    stock_code, stock_name, data, fundamental
                )
                
                # 筛选符合条件的建议
                if advice and advice.confidence >= min_confidence:
                    if advice.signal in [SignalStrength.STRONG_BUY, SignalStrength.BUY]:
                        advice_list.append(advice)
                        
            except Exception as e:
                logger.error(f"分析 {stock_code} 时出错: {str(e)}")
                continue
        
        # 按综合评分排序
        advice_list.sort(key=lambda x: x.overall_score, reverse=True)
        
        logger.info(f"扫描完成，找到 {len(advice_list)} 个投资机会")
        
        return advice_list
    
    def get_top_picks(self, advice_list: List[InvestmentAdvice], 
                     top_n: int = 10) -> List[InvestmentAdvice]:
        """
        获取最佳投资标的
        
        Args:
            advice_list: 投资建议列表
            top_n: 返回前N个
            
        Returns:
            最佳投资建议列表
        """
        return advice_list[:top_n]
