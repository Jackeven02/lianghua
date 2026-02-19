# 智能投资顾问系统使用指南

## 📋 系统概述

智能投资顾问系统是一个基于多维度量化分析的自动化投资建议平台，能够：

- 🔍 **自动扫描市场**：批量分析股票，筛选投资机会
- 📊 **多维度评分**：技术面、基本面、市场情绪综合评估
- 💡 **智能建议**：生成具体的买入/卖出信号和目标价
- 📦 **组合管理**：自动构建和优化投资组合
- ⚠️ **风险控制**：实时监控风险并提供预警

## 🎯 核心功能

### 1. 智能分析引擎 (SmartAdvisor)

#### 分析维度

**技术面分析 (40%权重)**
- 趋势分析：均线系统（SMA 5/20/60）
- 动量指标：MACD、RSI、KDJ
- 波动指标：布林带、ATR
- 成交量分析：量价配合
- 趋势强度：ADX指标

**基本面分析 (35%权重)**
- 盈利能力：ROE（净资产收益率）
- 成长性：营收增长率、利润增长率
- 估值水平：PE、PB比率
- 财务健康：资产负债率、流动比率

**市场情绪 (25%权重)**
- 价格动量：短期和中期涨跌幅
- 波动率变化：ATR趋势
- 趋势强度：ADX指标

#### 评分系统

```
综合评分 = 技术面×40% + 基本面×35% + 情绪面×25%

信号等级：
- 80-100分：强烈买入 🔥
- 65-79分：买入 ✅
- 45-64分：持有 ⏸️
- 30-44分：卖出 ⚠️
- 0-29分：强烈卖出 ❌
```

### 2. 风险管理系统

#### 风险偏好配置

**保守型**
- 最大单只仓位：5%
- 止损比例：5%
- 最低评分要求：75分

**中等型**
- 最大单只仓位：10%
- 止损比例：8%
- 最低评分要求：65分

**激进型**
- 最大单只仓位：15%
- 止损比例：12%
- 最低评分要求：55分

#### 风险控制措施

1. **止损机制**：自动计算止损价，触发即提醒
2. **仓位控制**：根据信心度和风险等级动态调整
3. **集中度管理**：限制单只股票最大权重
4. **回撤监控**：实时跟踪最大回撤

### 3. 投资组合管理

#### 组合构建策略

```python
# 资金分配算法
权重 = (评分占比 × 信心度 × 风险调整系数)

风险调整系数：
- 低风险：1.2
- 中风险：1.0
- 高风险：0.7
```

#### 再平衡规则

**触发条件：**
1. 持仓触及止损价
2. 持仓达到目标价
3. 评级下调至卖出
4. 亏损超过5%且不在推荐列表

**操作建议：**
- 自动识别需要调整的持仓
- 推荐新的投资机会
- 优化组合配置

## 🚀 使用方法

### 基础使用

```python
from strategy_layer.smart_advisor import SmartAdvisor, MarketScanner
from strategy_layer.portfolio_manager import PortfolioManager

# 1. 创建智能顾问（设置风险偏好）
advisor = SmartAdvisor(risk_tolerance="中等")

# 2. 分析单只股票
advice = advisor.analyze_stock(
    stock_code="600519",
    stock_name="贵州茅台",
    data=stock_data,  # 包含技术指标的DataFrame
    fundamental_data=fundamental_info  # 基本面数据字典
)

# 3. 查看建议
print(f"信号: {advice.signal.value}")
print(f"信心度: {advice.confidence}%")
print(f"目标价: {advice.target_price}")
print(f"止损价: {advice.stop_loss}")
print(f"建议仓位: {advice.position_size*100}%")
print(f"理由: {advice.reasons}")
```

### 市场扫描

```python
# 1. 创建市场扫描器
scanner = MarketScanner(advisor)

# 2. 准备股票列表
stock_list = [
    ("600519", "贵州茅台"),
    ("000858", "五粮液"),
    ("600036", "招商银行"),
    # ... 更多股票
]

# 3. 扫描市场
advice_list = scanner.scan_market(
    stock_list=stock_list,
    data_provider=data_provider,  # 数据提供者
    min_confidence=60  # 最低信心度
)

# 4. 获取最佳投资标的
top_picks = scanner.get_top_picks(advice_list, top_n=10)

for advice in top_picks:
    print(f"{advice.stock_name}: {advice.signal.value} "
          f"(评分: {advice.overall_score:.1f})")
```

### 组合管理

```python
# 1. 创建组合管理器
portfolio_mgr = PortfolioManager(initial_capital=1000000)

# 2. 构建投资组合
portfolio = portfolio_mgr.build_portfolio(
    advice_list=top_picks,
    available_capital=800000  # 使用80%资金
)

# 3. 查看组合
print(portfolio_mgr.generate_portfolio_report(portfolio))

# 4. 再平衡
rebalance_actions = portfolio_mgr.rebalance_portfolio(
    current_portfolio=portfolio,
    new_advice_list=new_advice_list
)

for stock_code, action in rebalance_actions.items():
    print(f"{stock_code}: {action}")
```

### 风险监控

```python
from strategy_layer.portfolio_manager import RiskManager

# 1. 创建风险管理器
risk_mgr = RiskManager(max_portfolio_risk=0.20)

# 2. 检查组合风险
risk_check = risk_mgr.check_portfolio_risk(portfolio)

print(f"风险等级: {risk_check['risk_level']}")
print(f"警告: {risk_check['warnings']}")
print(f"建议: {risk_check['suggestions']}")

# 3. 检查单个持仓风险
for position in portfolio.positions:
    pos_risk = risk_mgr.check_position_risk(position, portfolio.total_value)
    if not pos_risk['is_safe']:
        print(f"{position.stock_name}: {pos_risk['warnings']}")
```

## 📊 UI界面使用

### 投资建议页面

1. **设置参数**
   - 选择风险偏好（保守/中等/激进）
   - 设置最低信心度（50-90%）

2. **扫描市场**
   - 点击"开始扫描市场"按钮
   - 系统自动分析所有股票
   - 显示符合条件的投资机会

3. **查看建议**
   - 表格显示所有建议
   - 点击行查看详细分析
   - 绿色表示买入，红色表示卖出

### 组合管理页面

1. **构建组合**
   - 基于投资建议自动构建
   - 显示持仓明细和盈亏

2. **再平衡**
   - 检查是否需要调整
   - 提供具体操作建议

3. **导出报告**
   - 生成完整的组合报告
   - 包含所有关键指标

### 风险监控页面

1. **风险指标**
   - 显示当前风险等级
   - 关键风险指标

2. **风险警告**
   - 实时风险提醒
   - 触发止损提示

3. **建议操作**
   - 风险应对建议
   - 优化方案

## 🎓 最佳实践

### 1. 数据准备

```python
# 确保数据包含所有必要的技术指标
from analysis_layer.technical_indicators import TechnicalIndicators

# 计算所有指标
data_with_indicators = TechnicalIndicators.calculate_all_indicators(raw_data)
```

### 2. 定期扫描

```python
# 建议每日收盘后扫描
import schedule

def daily_scan():
    advice_list = scanner.scan_market(stock_list, data_provider)
    # 保存结果或发送通知
    
schedule.every().day.at("15:30").do(daily_scan)
```

### 3. 风险控制

```python
# 始终设置止损
# 不要超过建议仓位
# 定期检查风险指标
# 及时止盈止损
```

### 4. 组合优化

```python
# 每周检查一次组合
# 根据市场变化调整
# 保持适当的现金比例（10-20%）
# 分散投资，不要过度集中
```

## ⚙️ 高级配置

### 自定义评分权重

```python
# 修改 SmartAdvisor._calculate_overall_score 方法
weights = {
    "technical": 0.50,    # 技术面权重
    "fundamental": 0.30,  # 基本面权重
    "sentiment": 0.20     # 情绪面权重
}
```

### 自定义风险参数

```python
advisor.risk_params = {
    "保守": {
        "max_position": 0.05,
        "stop_loss_pct": 0.05,
        "min_score": 75
    },
    # ... 其他配置
}
```

### 自定义信号阈值

```python
# 修改 _generate_signal 方法中的阈值
if overall_score >= 85:  # 提高强烈买入门槛
    signal = SignalStrength.STRONG_BUY
```

## 📈 性能优化

### 批量处理

```python
# 使用多线程加速扫描
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(advisor.analyze_stock, code, name, data) 
               for code, name, data in stock_data_list]
    results = [f.result() for f in futures]
```

### 缓存机制

```python
# 缓存技术指标计算结果
from functools import lru_cache

@lru_cache(maxsize=100)
def get_indicators(stock_code):
    return TechnicalIndicators.calculate_all_indicators(data)
```

## 🔧 故障排除

### 常见问题

1. **数据不足**
   - 确保至少有60天的历史数据
   - 检查数据是否包含必要的列

2. **评分异常**
   - 检查技术指标是否正确计算
   - 验证基本面数据的完整性

3. **信号不准确**
   - 调整评分权重
   - 提高最低信心度阈值
   - 结合人工判断

## 📝 注意事项

⚠️ **重要提醒**

1. 本系统仅供参考，不构成投资建议
2. 投资有风险，入市需谨慎
3. 建议结合基本面研究和市场环境
4. 严格执行止损，控制风险
5. 不要过度依赖单一指标或系统
6. 定期回测和优化策略参数

## 🔄 更新日志

### v1.0.0 (2024-02)
- ✅ 智能分析引擎
- ✅ 多维度评分系统
- ✅ 投资组合管理
- ✅ 风险监控系统
- ✅ UI界面

### 未来计划
- 🔜 机器学习模型集成
- 🔜 情绪分析增强
- 🔜 自动交易接口
- 🔜 回测系统优化
- 🔜 移动端支持

## 📞 技术支持

如有问题或建议，请联系开发团队或提交Issue。
