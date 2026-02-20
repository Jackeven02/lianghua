# 📊 分钟级数据使用指南

## 概述

QuantAnalyzer系统现已支持多种时间频率的K线数据，包括：
- **1分钟** - 超短线交易、实时监控
- **5分钟** - 日内分析、短线交易
- **15分钟** - 短期趋势分析
- **30分钟** - 短期趋势分析
- **60分钟** - 中期趋势分析
- **日线** - 长期投资分析（默认）
- **周线** - 长期趋势分析
- **月线** - 超长期分析

---

## 🚀 快速开始

### 1. 基本用法

```python
from data_layer.efinance_provider import EFinanceProvider

# 创建数据提供者
provider = EFinanceProvider()

# 获取1分钟数据（最近100条）
df_1min = provider.get_stock_data("600519", days=100, klt=1)

# 获取5分钟数据
df_5min = provider.get_stock_data("600519", days=100, klt=5)

# 获取日线数据（默认）
df_daily = provider.get_stock_data("600519", days=100, klt=101)
```

### 2. K线类型参数 (klt)

| klt值 | 频率 | 说明 | 适用场景 |
|-------|------|------|----------|
| 1 | 1分钟 | 最细粒度 | 超短线交易、实时监控 |
| 5 | 5分钟 | 日内分析 | 短线交易、日内波段 |
| 15 | 15分钟 | 短期趋势 | 短线趋势跟踪 |
| 30 | 30分钟 | 短期趋势 | 短线趋势跟踪 |
| 60 | 60分钟 | 中期趋势 | 中短期趋势分析 |
| 101 | 日线 | 标准周期 | 长期投资分析（默认） |
| 102 | 周线 | 长期趋势 | 长期趋势分析 |
| 103 | 月线 | 超长期 | 超长期趋势分析 |

---

## 💡 使用场景

### 场景1: 实时监控（1分钟数据）

```python
from data_layer.efinance_provider import EFinanceProvider
import time

provider = EFinanceProvider()

# 监控股票列表
watch_list = ["600519", "000858", "600036"]

while True:
    for stock_code in watch_list:
        # 获取最新10条1分钟数据
        df = provider.get_stock_data(stock_code, days=10, klt=1)
        
        if not df.empty:
            latest = df.iloc[-1]
            print(f"{stock_code}: {latest['close']:.2f} @ {latest['date']}")
    
    # 每分钟更新一次
    time.sleep(60)
```

### 场景2: 日内分析（5分钟数据）

```python
from data_layer.efinance_provider import EFinanceProvider

provider = EFinanceProvider()

# 获取今日5分钟数据（约48条，一天交易4小时）
df = provider.get_stock_data("600519", days=50, klt=5)

# 计算日内统计
print(f"开盘价: {df.iloc[0]['open']:.2f}")
print(f"最新价: {df.iloc[-1]['close']:.2f}")
print(f"最高价: {df['high'].max():.2f}")
print(f"最低价: {df['low'].min():.2f}")

# 计算涨跌
change = df.iloc[-1]['close'] - df.iloc[0]['open']
change_pct = (change / df.iloc[0]['open']) * 100
print(f"涨跌幅: {change_pct:+.2f}%")
```

### 场景3: 短线趋势分析（15分钟数据）

```python
from data_layer.efinance_provider import EFinanceProvider

provider = EFinanceProvider()

# 获取最近100条15分钟数据
df = provider.get_stock_data("600519", days=100, klt=15)

# 分析短期趋势
latest = df.iloc[-1]

# 均线判断
if latest['MA5'] > latest['MA10'] > latest['MA20']:
    print("短期趋势: 多头排列 ↗")
elif latest['MA5'] < latest['MA10'] < latest['MA20']:
    print("短期趋势: 空头排列 ↘")
else:
    print("短期趋势: 震荡整理 ↔")

# MACD判断
if latest['MACD'] > latest['Signal']:
    print("MACD: 金叉 ✅")
else:
    print("MACD: 死叉 ❌")
```

### 场景4: 多周期分析

```python
from data_layer.efinance_provider import EFinanceProvider

provider = EFinanceProvider()
stock_code = "600519"

# 获取不同周期数据
df_5min = provider.get_stock_data(stock_code, days=50, klt=5)
df_15min = provider.get_stock_data(stock_code, days=100, klt=15)
df_60min = provider.get_stock_data(stock_code, days=100, klt=60)
df_daily = provider.get_stock_data(stock_code, days=120, klt=101)

# 多周期共振分析
def check_trend(df):
    latest = df.iloc[-1]
    if latest['MA5'] > latest['MA10'] > latest['MA20']:
        return "多头"
    elif latest['MA5'] < latest['MA10'] < latest['MA20']:
        return "空头"
    else:
        return "震荡"

print(f"5分钟趋势: {check_trend(df_5min)}")
print(f"15分钟趋势: {check_trend(df_15min)}")
print(f"60分钟趋势: {check_trend(df_60min)}")
print(f"日线趋势: {check_trend(df_daily)}")

# 如果多个周期都是多头，则趋势更强
```

---

## ⚙️ 缓存机制

系统对不同频率的数据使用不同的缓存策略：

| 数据频率 | 缓存时间 | 说明 |
|---------|---------|------|
| 分钟级 (klt < 101) | 60秒 | 快速更新，适合实时监控 |
| 日线及以上 (klt >= 101) | 300秒 (5分钟) | 更新频率较低 |

```python
# 清除缓存，强制重新获取数据
provider.clear_cache()
```

---

## 📈 技术指标

所有频率的数据都会自动计算以下技术指标：

### 趋势指标
- **MA5, MA10, MA20, MA60** - 移动平均线
- **EMA12, EMA26** - 指数移动平均线

### 动量指标
- **RSI** - 相对强弱指标
- **MACD, Signal, MACD_Hist** - MACD指标

### 波动率指标
- **BOLL_UPPER, BOLL_MIDDLE, BOLL_LOWER** - 布林带
- **ATR** - 平均真实波幅

### 成交量指标
- **Volume_MA5, Volume_MA10** - 成交量均线

---

## 🎯 最佳实践

### 1. 选择合适的时间周期

```python
# 根据交易风格选择周期
trading_styles = {
    "超短线": 1,      # 1分钟
    "短线": 5,        # 5分钟
    "日内": 15,       # 15分钟
    "短期": 60,       # 60分钟
    "中期": 101,      # 日线
    "长期": 102,      # 周线
}

# 示例：短线交易者使用5分钟数据
klt = trading_styles["短线"]
df = provider.get_stock_data("600519", days=100, klt=klt)
```

### 2. 数据量控制

```python
# 不同周期建议的数据量
data_amounts = {
    1: 100,      # 1分钟: 100条 ≈ 1.5小时
    5: 100,      # 5分钟: 100条 ≈ 8小时
    15: 100,     # 15分钟: 100条 ≈ 1天
    60: 100,     # 60分钟: 100条 ≈ 4天
    101: 120,    # 日线: 120条 ≈ 6个月
}

klt = 5
days = data_amounts[klt]
df = provider.get_stock_data("600519", days=days, klt=klt)
```

### 3. 错误处理

```python
from data_layer.efinance_provider import EFinanceProvider

provider = EFinanceProvider()

try:
    df = provider.get_stock_data("600519", days=100, klt=1)
    
    if df.empty:
        print("警告: 未获取到数据")
    else:
        print(f"成功获取 {len(df)} 条数据")
        # 进行分析...
        
except Exception as e:
    print(f"错误: {str(e)}")
```

---

## 🔧 演示程序

运行演示程序查看分钟级数据的使用：

```bash
# 运行分钟级数据演示
python demo_minute_data.py
```

演示内容包括：
1. 不同频率数据获取演示
2. 实时监控演示（1分钟数据）
3. 日内分析演示（5分钟数据）

---

## ⚠️ 注意事项

### 1. 数据可用性
- 分钟级数据通常只保留最近一段时间（如最近几个月）
- 历史久远的分钟数据可能无法获取
- 建议使用日线数据进行长期历史分析

### 2. 性能考虑
- 分钟级数据量大，计算技术指标耗时较长
- 建议合理控制数据量（如100-200条）
- 使用缓存机制避免频繁请求

### 3. 交易时间
- 分钟级数据仅在交易时间内更新
- 交易时间: 9:30-11:30, 13:00-15:00
- 非交易时间获取的是最后一个交易日的数据

### 4. 数据延迟
- 实时数据可能有1-3分钟延迟
- 不建议用于高频交易
- 适合短线和日内交易

---

## 📚 相关文档

- [REAL_DATA_GUIDE.md](REAL_DATA_GUIDE.md) - 真实数据使用指南
- [SMART_ADVISOR_GUIDE.md](SMART_ADVISOR_GUIDE.md) - 智能投资顾问指南
- [MODERN_GUI_GUIDE.md](MODERN_GUI_GUIDE.md) - 现代化GUI使用指南

---

## 🎓 学习资源

### 推荐阅读
1. K线理论基础
2. 技术指标详解
3. 多周期分析方法
4. 短线交易策略

### 实战建议
1. 从日线数据开始学习
2. 逐步过渡到小时线
3. 熟练后再使用分钟线
4. 多周期结合使用效果更好

---

**更新时间:** 2024年2月  
**版本:** v2.1  
**作者:** QuantAnalyzer Team
