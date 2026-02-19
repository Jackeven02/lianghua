"""
一体化简化版智能投资顾问GUI
所有功能整合到一个文件，避免导入问题
"""
import sys
import os
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                           QTableWidget, QTableWidgetItem, QComboBox, 
                           QLineEdit, QGroupBox, QFormLayout, QSplitter,
                           QProgressBar, QStatusBar, QMessageBox, QHeaderView,
                           QFrame)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import efinance as ef
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


# 定义信号强度枚举
class SignalStrength(Enum):
    """信号强度枚举"""
    STRONG_BUY = "强烈买入"
    BUY = "买入"
    HOLD = "持有"
    SELL = "卖出"
    STRONG_SELL = "强烈卖出"


# 定义投资建议数据类
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
    reasons: list
    risk_level: str  # 低/中/高
    position_size: float  # 建议仓位比例
    time_horizon: str  # 短期/中期/长期
    technical_score: float
    fundamental_score: float
    sentiment_score: float
    overall_score: float
    timestamp: datetime


# 简化版技术指标计算
class SimpleTechnicalIndicators:
    """简化版技术指标计算"""
    
    @staticmethod
    def calculate_sma(data, period):
        """计算简单移动平均线"""
        return data['close'].rolling(window=period).mean()
    
    @staticmethod
    def calculate_rsi(data, period=14):
        """计算RSI指标"""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_bollinger_bands(data, period=20):
        """计算布林带"""
        sma = data['close'].rolling(window=period).mean()
        std = data['close'].rolling(window=period).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        return upper_band, sma, lower_band
    
    @staticmethod
    def calculate_macd(data):
        """计算MACD"""
        exp1 = data['close'].ewm(span=12).mean()
        exp2 = data['close'].ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        return macd, signal, histogram
    
    @staticmethod
    def calculate_all_indicators(data):
        """计算所有技术指标"""
        try:
            # 计算各种技术指标
            data['SMA_5'] = SimpleTechnicalIndicators.calculate_sma(data, 5)
            data['SMA_20'] = SimpleTechnicalIndicators.calculate_sma(data, 20)
            data['SMA_60'] = SimpleTechnicalIndicators.calculate_sma(data, 60)
            data['RSI_14'] = SimpleTechnicalIndicators.calculate_rsi(data, 14)
            
            bb_upper, bb_middle, bb_lower = SimpleTechnicalIndicators.calculate_bollinger_bands(data)
            data['BB_upper'] = bb_upper
            data['BB_middle'] = bb_middle
            data['BB_lower'] = bb_lower
            
            macd, macd_signal, macd_hist = SimpleTechnicalIndicators.calculate_macd(data)
            data['MACD'] = macd
            data['MACD_signal'] = macd_signal
            data['MACD_histogram'] = macd_hist
            
            # 计算波动率相关指标
            data['ATR'] = data['high'] - data['low']  # 简化的ATR
            data['ADX'] = 25  # 简化，使用固定值
            
            # KDJ指标简化计算
            low_min = data['low'].rolling(window=9).min()
            high_max = data['high'].rolling(window=9).max()
            data['K'] = 50  # 简化
            data['D'] = 50  # 简化
            data['J'] = 50  # 简化
            
        except Exception as e:
            print(f"计算技术指标时出错: {e}")
        
        return data


# 简化版智能顾问
class SimpleSmartAdvisor:
    """简化版智能顾问"""
    
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
                     fundamental_data=None) -> InvestmentAdvice:
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
            print(f"{stock_code} 数据不足，无法分析")
            return None
            
        # 1. 技术面分析评分
        technical_score = self._analyze_technical(data)
        
        # 2. 基本面分析评分（简化）
        fundamental_score = self._analyze_fundamental(fundamental_data) if fundamental_data else 50
        
        # 3. 市场情绪分析评分（简化）
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
            
            # 2. RSI指标 (20分)
            if 'RSI_14' in data.columns:
                rsi = latest['RSI_14']
                if 30 < rsi < 70:
                    score += 20  # 正常区间
                elif 20 < rsi <= 30:
                    score += 15  # 接近超卖
                elif rsi <= 20:
                    score += 10  # 超卖（可能反弹）
                elif 70 <= rsi < 80:
                    score += 10  # 接近超买
                else:
                    score += 5   # 超买
            
            # 3. 布林带位置 (15分)
            if all(col in data.columns for col in ['close', 'BB_upper', 'BB_middle', 'BB_lower']):
                close = latest['close']
                bb_upper = latest['BB_upper']
                bb_middle = latest['BB_middle']
                bb_lower = latest['BB_lower']
                
                bb_position = (close - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
                if 0.3 < bb_position < 0.7:
                    score += 15  # 中轨附近
                elif bb_position <= 0.2:
                    score += 12  # 下轨附近（可能反弹）
                elif bb_position >= 0.8:
                    score += 8   # 上轨附近（可能回调）
                else:
                    score += 10
            
            # 4. 成交量分析 (10分)
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
            
            # 5. MACD指标 (15分) - 简化
            if 'MACD' in data.columns and 'MACD_signal' in data.columns:
                macd_diff = latest['MACD'] - latest['MACD_signal']
                if macd_diff > 0:
                    score += 15  # 多头
                else:
                    score += 5   # 空头
            
            # 6. KDJ指标 (10分) - 简化
            if 'K' in data.columns and 'D' in data.columns:
                k, d = latest['K'], latest['D']
                if k > d:
                    score += 10  # 金叉
                else:
                    score += 5   # 死叉
            
        except Exception as e:
            print(f"技术分析出错: {e}")
            score = 50  # 默认中性分数
        
        return min(score, max_score)
    
    def _analyze_fundamental(self, fundamental_data: dict) -> float:
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
            pe_ratio = fundamental_data.get('pe_ratio', 50)  # 市盈率
            pb_ratio = fundamental_data.get('pb_ratio', 5)  # 市净率
            
            if 0 < pe_ratio < 15 and 0 < pb_ratio < 2:
                score += 25  # 低估
            elif 15 <= pe_ratio < 30 and 2 <= pb_ratio < 4:
                score += 18  # 合理
            elif pe_ratio >= 30 or pb_ratio >= 4:
                score += 8   # 高估
            
            # 4. 财务健康 (20分)
            debt_ratio = fundamental_data.get('debt_ratio', 1)  # 资产负债率
            current_ratio = fundamental_data.get('current_ratio', 1)  # 流动比率
            
            if debt_ratio < 0.5 and current_ratio > 1.5:
                score += 20  # 财务健康
            elif debt_ratio < 0.7 and current_ratio > 1.0:
                score += 15  # 财务良好
            else:
                score += 8   # 财务一般
            
        except Exception as e:
            print(f"基本面分析出错: {e}")
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
            print(f"情绪分析出错: {e}")
        
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
                        data: pd.DataFrame) -> tuple:
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
                                data: pd.DataFrame) -> tuple:
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
                         fundamental_score: float, sentiment_score: float) -> list:
        """
        生成投资建议理由
        """
        reasons = []
        latest = data.iloc[-1]
        
        try:
            # 技术面理由
            if technical_score >= 70:
                if 'SMA_5' in data.columns and latest['SMA_5'] > latest['SMA_20']:
                    reasons.append("短期均线上穿长期均线，形成多头排列")
                if 'RSI_14' in data.columns and 30 < latest['RSI_14'] < 70:
                    reasons.append("RSI处于健康区间，无超买超卖")
            elif technical_score < 40:
                if 'SMA_5' in data.columns and latest['SMA_5'] < latest['SMA_20']:
                    reasons.append("短期均线下穿长期均线，形成空头排列")
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
            print(f"生成理由时出错: {e}")
            reasons.append("基于多维度量化分析")
        
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
            print(f"风险评估出错: {e}")
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
            print(f"时间范围判断出错: {e}")
            return "短期"


# 市场扫描器
class SimpleMarketScanner:
    """简化版市场扫描器"""
    
    def __init__(self, advisor: SimpleSmartAdvisor):
        self.advisor = advisor
        
    def scan_market(self, stock_list: list, 
                   min_confidence: float = 60) -> list:
        """
        扫描市场并生成投资建议列表
        
        Args:
            stock_list: 股票列表 [(代码, 名称), ...]
            min_confidence: 最低信心阈值
            
        Returns:
            投资建议列表（按评分排序）
        """
        advice_list = []
        
        print(f"开始扫描 {len(stock_list)} 只股票...")
        
        for stock_code, stock_name in stock_list:
            try:
                # 获取数据
                data = ef.stock.get_quote_history(stock_code)
                
                if data is None or data.empty or len(data) < 60:
                    continue
                
                # 数据预处理
                data = data.rename(columns={
                    '日期': 'date', '开盘': 'open', '最高': 'high', 
                    '最低': 'low', '收盘': 'close', '成交量': 'volume'
                })
                
                data['date'] = pd.to_datetime(data['date'])
                data = data.sort_values('date')
                
                numeric_cols = ['open', 'high', 'low', 'close', 'volume']
                for col in numeric_cols:
                    if col in data.columns:
                        data[col] = pd.to_numeric(data[col], errors='coerce')
                
                data = data.dropna()
                
                if len(data) < 60:
                    continue
                
                # 计算技术指标
                data = SimpleTechnicalIndicators.calculate_all_indicators(data)
                
                # 分析股票
                fundamental_data = self._get_sample_fundamental_data(stock_code)
                advice = self.advisor.analyze_stock(
                    stock_code, stock_name, data, fundamental_data
                )
                
                # 筛选符合条件的建议
                if advice and advice.confidence >= min_confidence:
                    if advice.signal in [SignalStrength.STRONG_BUY, SignalStrength.BUY, SignalStrength.HOLD]:
                        advice_list.append(advice)
                        
            except Exception as e:
                print(f"分析 {stock_code} 时出错: {e}")
                continue
        
        # 按综合评分排序
        advice_list.sort(key=lambda x: x.overall_score, reverse=True)
        
        print(f"扫描完成，找到 {len(advice_list)} 个投资机会")
        
        return advice_list
    
    def _get_sample_fundamental_data(self, stock_code):
        """获取示例基本面数据"""
        return {
            'roe': 15.0,  # 净资产收益率
            'revenue_growth': 10.0,  # 营收增长率
            'profit_growth': 12.0,  # 利润增长率
            'pe_ratio': 20.0,  # 市盈率
            'pb_ratio': 2.5,  # 市净率
            'debt_ratio': 0.4,  # 资产负债率
            'current_ratio': 1.8  # 流动比率
        }


# 分析工作线程
class AnalysisWorker(QThread):
    """分析工作线程"""
    analysis_completed = pyqtSignal(object)  # 发送分析结果
    progress_updated = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, data, stock_code, stock_name, analysis_type):
        super().__init__()
        self.data = data
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.analysis_type = analysis_type
        
    def run(self):
        try:
            self.progress_updated.emit(20)
            
            if self.analysis_type == "single":
                # 单股分析
                advisor = SimpleSmartAdvisor()
                self.progress_updated.emit(50)
                
                # 获取基本面数据（简化）
                fundamental_data = {
                    'roe': 15.0, 'revenue_growth': 10.0, 'profit_growth': 12.0,
                    'pe_ratio': 20.0, 'pb_ratio': 2.5, 'debt_ratio': 0.4, 'current_ratio': 1.8
                }
                self.progress_updated.emit(70)
                
                # 分析股票
                advice = advisor.analyze_stock(
                    self.stock_code, 
                    self.stock_name, 
                    self.data, 
                    fundamental_data
                )
                self.progress_updated.emit(90)
                
                self.analysis_completed.emit(advice)
                
            elif self.analysis_type == "scan":
                # 市场扫描
                advisor = SimpleSmartAdvisor()
                scanner = SimpleMarketScanner(advisor)
                self.progress_updated.emit(30)
                
                # 使用热门股票列表进行扫描
                hot_stocks = [
                    ("600519", "贵州茅台"),
                    ("000858", "五粮液"),
                    ("600036", "招商银行"),
                    ("601318", "中国平安"),
                    ("000333", "美的集团"),
                    ("600276", "恒瑞医药"),
                    ("000651", "格力电器"),
                    ("601888", "中国中免"),
                    ("300750", "宁德时代"),
                    ("002475", "立讯精密")
                ]
                
                self.progress_updated.emit(50)
                
                # 执行扫描
                advice_list = scanner.scan_market(hot_stocks)
                
                self.analysis_completed.emit(advice_list)
                
            self.progress_updated.emit(100)
            
        except Exception as e:
            self.error_occurred.emit(f"分析过程出错: {str(e)}")


# 主GUI类
class SimpleQuantAnalyzerGUI(QMainWindow):
    """简化版量化分析GUI"""
    
    def __init__(self):
        super().__init__()
        self.current_data = None
        self.analysis_thread = None
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('智能投资顾问 - 简化版')
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title_label = QLabel('智能投资顾问系统')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            margin: 15px; 
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        """)
        main_layout.addWidget(title_label)
        
        # 控制面板
        control_group = QGroupBox("分析控制")
        control_layout = QFormLayout(control_group)
        
        # 股票代码输入
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("输入股票代码，如：600519 或 000001")
        self.code_input.setText("600519")  # 默认贵州茅台
        control_layout.addRow("股票代码:", self.code_input)
        
        # 股票名称输入
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("输入股票名称，如：贵州茅台")
        self.name_input.setText("贵州茅台")  # 默认名称
        control_layout.addRow("股票名称:", self.name_input)
        
        # 分析类型选择
        self.type_combo = QComboBox()
        self.type_combo.addItems(["单股分析", "市场扫描"])
        control_layout.addRow("分析类型:", self.type_combo)
        
        # 数据周期选择
        self.period_combo = QComboBox()
        self.period_combo.addItems(["日线", "周线", "月线"])
        control_layout.addRow("数据周期:", self.period_combo)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        self.analyze_btn = QPushButton("开始分析")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.clear_btn = QPushButton("清空结果")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addWidget(self.analyze_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        control_layout.addRow(button_layout)
        
        main_layout.addWidget(control_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        main_layout.addWidget(self.progress_bar)
        
        # 结果显示区域 - 使用分割器
        splitter = QSplitter(Qt.Vertical)
        
        # 上半部分：基本分析结果
        top_group = QGroupBox("分析结果")
        top_layout = QVBoxLayout(top_group)
        
        # 基本信息显示
        self.basic_info = QTextEdit()
        self.basic_info.setPlaceholderText("分析结果将显示在这里...")
        self.basic_info.setMaximumHeight(150)
        self.basic_info.setFont(QFont("Consolas", 10))
        top_layout.addWidget(self.basic_info)
        
        splitter.addWidget(top_group)
        
        # 中间部分：详细分析
        middle_group = QGroupBox("详细分析")
        middle_layout = QVBoxLayout(middle_group)
        
        # 详细分析文本框
        self.detailed_analysis = QTextEdit()
        self.detailed_analysis.setPlaceholderText("详细分析将显示在这里...")
        self.detailed_analysis.setFont(QFont("Consolas", 10))
        middle_layout.addWidget(self.detailed_analysis)
        
        splitter.addWidget(middle_group)
        
        # 下半部分：投资建议表格
        bottom_group = QGroupBox("投资建议")
        bottom_layout = QVBoxLayout(bottom_group)
        
        self.advice_table = QTableWidget()
        self.advice_table.setColumnCount(9)
        self.advice_table.setHorizontalHeaderLabels([
            "股票代码", "股票名称", "操作建议", "置信度", "当前价格", 
            "目标价格", "止损价格", "评分", "建议理由"
        ])
        header = self.advice_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # 允许手动调整列宽
        bottom_layout.addWidget(self.advice_table)
        
        splitter.addWidget(bottom_group)
        
        # 设置分割器比例
        splitter.setSizes([150, 300, 250])
        main_layout.addWidget(splitter)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 - 请输入股票代码并点击'开始分析'")
        
        # 连接信号
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.clear_btn.clicked.connect(self.clear_results)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QComboBox, QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                padding: 5px;
            }
            QTableWidget {
                border: 1px solid #bdc3c7;
                gridline-color: #bdc3c7;
            }
        """)
    
    def start_analysis(self):
        """开始分析"""
        code = self.code_input.text().strip()
        name = self.name_input.text().strip()
        analysis_type = self.type_combo.currentText()
        
        if not code:
            QMessageBox.warning(self, "警告", "请输入股票代码")
            return
            
        if not name:
            QMessageBox.warning(self, "警告", "请输入股票名称")
            return
        
        # 更新状态
        if analysis_type == "单股分析":
            self.status_bar.showMessage(f"正在获取 {name}({code}) 的数据...")
        else:
            self.status_bar.showMessage("正在进行市场扫描...")
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.analyze_btn.setEnabled(False)
        
        try:
            # 根据分析类型决定获取数据的方式
            if analysis_type == "单股分析":
                # 获取单只股票数据
                period_map = {"日线": 101, "周线": 102, "月线": 103}
                klt = period_map.get(self.period_combo.currentText(), 101)
                
                data = ef.stock.get_quote_history(code, klt=klt)
                
                if data is None or data.empty:
                    raise Exception("未获取到数据")
                
                # 数据预处理
                data = data.rename(columns={
                    '日期': 'date', '开盘': 'open', '最高': 'high', 
                    '最低': 'low', '收盘': 'close', '成交量': 'volume',
                    '成交额': 'amount', '涨跌幅': 'change_pct', '涨跌额': 'change'
                })
                
                data['date'] = pd.to_datetime(data['date'])
                data = data.sort_values('date')
                
                numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount', 'change_pct', 'change']
                for col in numeric_cols:
                    if col in data.columns:
                        data[col] = pd.to_numeric(data[col], errors='coerce')
                
                data = data.dropna()
                
                if len(data) < 60:
                    raise Exception("数据量不足，至少需要60个交易日的数据进行分析")
                
                # 计算技术指标
                data = SimpleTechnicalIndicators.calculate_all_indicators(data)
                
                self.current_data = data
                
                # 启动分析线程
                self.analysis_thread = AnalysisWorker(data, code, name, "single")
                
            else:  # 市场扫描
                # 对于市场扫描，我们传递空数据，实际获取将在工作线程中完成
                self.current_data = None
                dummy_data = pd.DataFrame()
                self.analysis_thread = AnalysisWorker(dummy_data, code, name, "scan")
            
            # 连接信号
            self.analysis_thread.analysis_completed.connect(self.on_analysis_completed)
            self.analysis_thread.progress_updated.connect(self.progress_bar.setValue)
            self.analysis_thread.error_occurred.connect(self.on_analysis_error)
            self.analysis_thread.finished.connect(self.on_analysis_finished)
            
            # 启动线程
            self.analysis_thread.start()
            
        except Exception as e:
            self.on_analysis_error(str(e))
    
    def on_analysis_completed(self, result):
        """分析完成回调"""
        try:
            analysis_type = self.type_combo.currentText()
            
            if analysis_type == "单股分析":
                # 单股分析结果
                if result is None:
                    self.basic_info.setText("未能完成分析，请检查数据或重试")
                    return
                
                # 显示基本分析结果
                basic_text = f"""股票: {result.stock_name} ({result.stock_code})
当前价格: ¥{result.current_price:.2f}
分析日期: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

技术指标:
  SMA5:  ¥{getattr(result, 'technical_score', 0):.2f} (简化显示)
  信号: {result.signal.value}
  信心度: {result.confidence:.1f}%
  评分: {result.overall_score:.1f}/100"""
                
                self.basic_info.setText(basic_text)
                
                # 显示详细分析
                detailed_text = f"""详细分析:
投资建议: {result.signal.value}
信心度: {result.confidence:.1f}%
风险等级: {result.risk_level}
建议仓位: {result.position_size*100:.1f}%

价格建议:
  目标价: ¥{result.target_price:.2f} ({(result.target_price/result.current_price-1)*100:+.2f}%)
  止损价: ¥{result.stop_loss:.2f} ({(result.stop_loss/result.current_price-1)*100:+.2f}%)

技术评分: {result.technical_score:.1f}
基本面评分: {result.fundamental_score:.1f}
情绪面评分: {result.sentiment_score:.1f}

建议理由:
"""
                for i, reason in enumerate(result.reasons, 1):
                    detailed_text += f"  {i}. {reason}\n"
                
                self.detailed_analysis.setText(detailed_text)
                
                # 清空表格并添加结果
                self.advice_table.setRowCount(1)
                self.advice_table.setItem(0, 0, QTableWidgetItem(result.stock_code))
                self.advice_table.setItem(0, 1, QTableWidgetItem(result.stock_name))
                self.advice_table.setItem(0, 2, QTableWidgetItem(result.signal.value))
                self.advice_table.setItem(0, 3, QTableWidgetItem(f"{result.confidence:.1f}%"))
                self.advice_table.setItem(0, 4, QTableWidgetItem(f"¥{result.current_price:.2f}"))
                self.advice_table.setItem(0, 5, QTableWidgetItem(f"¥{result.target_price:.2f}"))
                self.advice_table.setItem(0, 6, QTableWidgetItem(f"¥{result.stop_loss:.2f}"))
                self.advice_table.setItem(0, 7, QTableWidgetItem(f"{result.overall_score:.1f}"))
                self.advice_table.setItem(0, 8, QTableWidgetItem("; ".join(result.reasons)))
                
                # 根据信号设置颜色
                signal_item = self.advice_table.item(0, 2)
                if "买入" in result.signal.value:
                    signal_item.setBackground(Qt.green)
                    signal_item.setForeground(Qt.black)
                elif "卖出" in result.signal.value:
                    signal_item.setBackground(Qt.red)
                    signal_item.setForeground(Qt.white)
                elif "持有" in result.signal.value:
                    signal_item.setBackground(Qt.yellow)
                    signal_item.setForeground(Qt.black)
                
                self.status_bar.showMessage(f"单股分析完成 - {result.stock_name}: {result.signal.value}")
                
            else:  # 市场扫描
                # 市场扫描结果
                if not result:
                    self.basic_info.setText("市场扫描未找到符合条件的投资机会")
                    return
                
                # 显示基本扫描结果
                top_picks = sorted(result, key=lambda x: x.overall_score, reverse=True)[:10]
                
                basic_text = f"""市场扫描结果:
扫描时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
发现 {len(result)} 个投资机会
显示前10个最佳机会"""
                
                self.basic_info.setText(basic_text)
                
                # 显示详细分析
                detailed_text = f"""市场扫描详情:
共分析了 {len(result)} 只股票
按综合评分排序显示前10只:
"""
                for i, advice in enumerate(top_picks[:5], 1):
                    detailed_text += f"  {i}. {advice.stock_name}: {advice.signal.value} (评分: {advice.overall_score:.1f})\n"
                
                self.detailed_analysis.setText(detailed_text)
                
                # 在表格中显示结果
                self.advice_table.setRowCount(len(top_picks))
                for row, advice in enumerate(top_picks):
                    self.advice_table.setItem(row, 0, QTableWidgetItem(advice.stock_code))
                    self.advice_table.setItem(row, 1, QTableWidgetItem(advice.stock_name))
                    self.advice_table.setItem(row, 2, QTableWidgetItem(advice.signal.value))
                    self.advice_table.setItem(row, 3, QTableWidgetItem(f"{advice.confidence:.1f}%"))
                    self.advice_table.setItem(row, 4, QTableWidgetItem(f"¥{advice.current_price:.2f}"))
                    self.advice_table.setItem(row, 5, QTableWidgetItem(f"¥{advice.target_price:.2f}"))
                    self.advice_table.setItem(row, 6, QTableWidgetItem(f"¥{advice.stop_loss:.2f}"))
                    self.advice_table.setItem(row, 7, QTableWidgetItem(f"{advice.overall_score:.1f}"))
                    self.advice_table.setItem(row, 8, QTableWidgetItem(advice.reasons[0] if advice.reasons else "待分析"))
                    
                    # 根据信号设置颜色
                    signal_item = self.advice_table.item(row, 2)
                    if "买入" in advice.signal.value:
                        signal_item.setBackground(Qt.green)
                        signal_item.setForeground(Qt.black)
                    elif "卖出" in advice.signal.value:
                        signal_item.setBackground(Qt.red)
                        signal_item.setForeground(Qt.white)
                    elif "持有" in advice.signal.value:
                        signal_item.setBackground(Qt.yellow)
                        signal_item.setForeground(Qt.black)
                
                self.status_bar.showMessage(f"市场扫描完成 - 找到 {len(result)} 个投资机会")
                
        except Exception as e:
            self.on_analysis_error(f"显示结果时出错: {str(e)}")
    
    def on_analysis_error(self, error_msg):
        """分析错误回调"""
        QMessageBox.critical(self, "分析错误", f"分析过程中出现错误:\n{error_msg}")
        self.status_bar.showMessage(f"分析失败: {error_msg}")
        self.basic_info.setText(f"分析失败: {error_msg}")
        
    def on_analysis_finished(self):
        """分析完成清理"""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
    
    def clear_results(self):
        """清空结果"""
        self.basic_info.clear()
        self.detailed_analysis.clear()
        self.advice_table.setRowCount(0)
        self.status_bar.showMessage("结果已清空")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用 Fusion 风格以获得更好的外观
    
    window = SimpleQuantAnalyzerGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()