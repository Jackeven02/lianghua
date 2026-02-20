# Smart Strategy Engine
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class InvestmentSuggestion:
    stock_code: str
    action: str
    confidence: float
    price_target: float
    stop_loss: float
    time_frame: str
    recommendation_reason: str
    risk_level: str

class SmartMarketAnalyzer:
    def __init__(self):
        self.strategy_database = {}
    
    def analyze_market_condition(self, data):
        if len(data) < 50:
            return 'insufficient_data'
        
        # Calculate trend indicators
        prices = data['close'].values
        returns = np.diff(np.log(prices))
        
        # Trend strength
        trend_strength = abs(np.mean(returns[-20:])) / np.std(returns[-20:])
        
        # Determine market state
        if trend_strength > 0.5 and abs(np.mean(returns[-20:])) > 0.02:
            return 'trending_up' if np.mean(returns[-20:]) > 0 else 'trending_down'
        else:
            return 'ranging'
    
    def generate_investment_suggestions(self, data, stock_code):
        suggestions = []
        current_price = data['close'].iloc[-1] if len(data) > 0 else 100
        
        # Analyze market environment
        market_condition = self.analyze_market_condition(data)
        
        # Get technical indicators
        sma_20 = data['close'].rolling(20).mean().iloc[-1] if len(data) >= 20 else current_price
        sma_50 = data['close'].rolling(50).mean().iloc[-1] if len(data) >= 50 else current_price
        rsi = self._calculate_rsi(data, 14).iloc[-1] if len(data) >= 14 else 50
        
        # Generate suggestions
        if self._should_buy(current_price, sma_20, sma_50, rsi, market_condition):
            suggestion = InvestmentSuggestion(
                stock_code=stock_code,
                action='buy',
                confidence=self._calculate_buy_confidence(current_price, sma_20, sma_50, rsi),
                price_target=current_price * 1.10,
                stop_loss=current_price * 0.95,
                time_frame='short',
                recommendation_reason=self._generate_buy_reason(current_price, sma_20, sma_50, rsi),
                risk_level='medium'
            )
        elif self._should_sell(current_price, sma_20, sma_50, rsi, market_condition):
            suggestion = InvestmentSuggestion(
                stock_code=stock_code,
                action='sell',
                confidence=self._calculate_sell_confidence(current_price, sma_20, sma_50, rsi),
                price_target=current_price * 0.90,
                stop_loss=current_price * 1.05,
                time_frame='short',
                recommendation_reason=self._generate_sell_reason(current_price, sma_20, sma_50, rsi),
                risk_level='medium'
            )
        else:
            suggestion = InvestmentSuggestion(
                stock_code=stock_code,
                action='hold',
                confidence=60,
                price_target=current_price,
                stop_loss=current_price * 0.92,
                time_frame='short',
                recommendation_reason='Market in consolidation, suggest watching',
                risk_level='low'
            )
        
        suggestions.append(suggestion)
        return suggestions
    
    def _calculate_rsi(self, data, period=14):
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _should_buy(self, price, sma_20, sma_50, rsi, market_condition):
        golden_cross = sma_20 >= sma_50 * 0.98 if sma_50 > 0 else False
        rsi_ok = 30 <= rsi <= 60
        price_ok = 0.9 <= (price / max(sma_20, sma_50) if max(sma_20, sma_50) > 0 else 1) <= 1.05
        return golden_cross and rsi_ok and price_ok
    
    def _should_sell(self, price, sma_20, sma_50, rsi, market_condition):
        death_cross = sma_20 <= sma_50 * 1.02 if sma_50 > 0 else False
        rsi_high = rsi >= 70
        price_high = (price / max(sma_20, sma_50) if max(sma_20, sma_50) > 0 else 1) >= 1.15
        return death_cross and (rsi_high or price_high)
    
    def _calculate_buy_confidence(self, price, sma_20, sma_50, rsi):
        trend_strength = abs((sma_20 - sma_50) / sma_50) * 100 if sma_50 > 0 else 0
        rsi_factor = max(0, 50 - abs(rsi - 50))
        confidence = min(90, trend_strength + rsi_factor + 20)
        return confidence
    
    def _calculate_sell_confidence(self, price, sma_20, sma_50, rsi):
        trend_strength = abs((sma_20 - sma_50) / sma_50) * 100 if sma_50 > 0 else 0
        rsi_factor = max(0, abs(rsi - 50)) if rsi > 50 else 0
        confidence = min(90, trend_strength + rsi_factor + 20)
        return confidence
    
    def _generate_buy_reason(self, price, sma_20, sma_50, rsi):
        reasons = []
        if sma_20 > sma_50:
            reasons.append('Short-term MA crosses above long-term MA (Golden Cross)')
        if 30 <= rsi <= 60:
            reasons.append(f'RSI indicator in reasonable range({rsi:.1f})')
        if price < max(sma_20, sma_50):
            reasons.append('Current price below important MA support')
        return '; '.join(reasons) if reasons else 'Technical analysis shows buying opportunity'
    
    def _generate_sell_reason(self, price, sma_20, sma_50, rsi):
        reasons = []
        if sma_20 < sma_50:
            reasons.append('Short-term MA crosses below long-term MA (Death Cross)')
        if rsi > 70:
            reasons.append(f'RSI indicator overbought({rsi:.1f})')
        if price > max(sma_20, sma_50) * 1.1:
            reasons.append('Current price significantly higher than important MA')
        return '; '.join(reasons) if reasons else 'Technical analysis shows selling signal'

class SmartStrategyEngine(SmartMarketAnalyzer):
    pass
