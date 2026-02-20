# 真实数据使用指南

## 📋 概述

系统现已集成 **efinance** 库，可以获取真实的A股市场数据，包括：
- 📈 历史K线数据（日线）
- 📊 实时行情数据
- 💰 基本面数据（业绩、财务指标）
- 🔥 热门股票列表
- 📑 市场概况信息

## 🚀 快速开始

### 1. 安装依赖

确保已安装 efinance 库：

```bash
pip install efinance
```

### 2. 测试数据连接

运行测试脚本验证数据获取是否正常：

```bash
cd quant_finance/quant_analyzer
python test_real_data.py
```

如果看到 "✓ 所有测试通过！" 说明数据连接正常。

### 3. 运行示例程序

```bash
python example_smart_advisor.py
```

选择 "1. 真实市场数据 (efinance)" 即可使用真实数据。

## 📚 数据提供者使用

### 基础使用

```python
from data_layer.efinance_provider import EFinanceProvider

# 创建数据提供者
provider = EFinanceProvider()

# 获取股票历史数据（包含技术指标）
data = provider.get_stock_data("600519")  # 贵州茅台

# 获取基本面数据
fundamental = provider.get_fundamental_data("600519")

# 获取实时行情
quotes = provider.get_realtime_quotes()

# 获取热门股票
hot_stocks = provider.get_hot_stocks(50)

# 获取股票信息
info = provider.get_stock_info("600519")
```

### 数据结构

#### 1. 历史数据 (get_stock_data)

返回包含技术指标的 DataFrame：

```python
列名:
- date: 日期
- open, high, low, close: OHLC价格
- volume: 成交量
- SMA_5, SMA_20, SMA_60: 简单移动平均
- EMA_5, EMA_20, EMA_60: 指数移动平均
- MACD, MACD_signal, MACD_histogram: MACD指标
- RSI_6, RSI_14, RSI_24: RSI指标
- BB_upper, BB_middle, BB_lower: 布林带
- K, D, J: KDJ指标
- CCI, ROC, WR, OBV, ATR, ADX: 其他技术指标
```

#### 2. 基本面数据 (get_fundamental_data)

返回字典：

```python
{
    'roe': 净资产收益率 (%),
    'revenue_growth': 营收增长率 (%),
    'profit_growth': 利润增长率 (%),
    'pe_ratio': 市盈率,
    'pb_ratio': 市净率,
    'debt_ratio': 资产负债率,
    'current_ratio': 流动比率,
    'eps': 每股收益,
    'bps': 每股净资产,
    'gross_margin': 销售毛利率 (%)
}
```

#### 3. 实时行情 (get_realtime_quotes)

返回 DataFrame，包含所有A股的实时数据：

```python
列名:
- 股票代码, 股票名称
- 最新价, 涨跌幅, 涨跌额
- 成交量, 成交额, 换手率
- 总市值, 流通市值
- 动态市盈率
等...
```

## 🔧 高级功能

### 1. 获取特定市场股票

```python
# 获取沪A股票
stock_list = provider.get_stock_list("沪A")

# 获取深A股票
stock_list = provider.get_stock_list("深A")

# 获取创业板股票
stock_list = provider.get_stock_list("创业板")

# 获取科创板股票
stock_list = provider.get_stock_list("科创板")
```

### 2. 获取指数成分股

```python
# 获取沪深300成分股
stock_list = provider.get_index_stocks("000300")

# 获取上证50成分股
stock_list = provider.get_index_stocks("000016")

# 获取创业板指成分股
stock_list = provider.get_index_stocks("399006")
```

### 3. 数据缓存

数据提供者内置缓存机制，默认缓存5分钟：

```python
# 清除缓存
provider.clear_cache()

# 修改缓存时间（秒）
provider.cache_timeout = 600  # 10分钟
```

## 🎯 完整示例

### 示例1: 分析单只股票

```python
from data_layer.efinance_provider import EFinanceProvider
from strategy_layer.smart_advisor import SmartAdvisor

# 创建提供者和顾问
provider = EFinanceProvider()
advisor = SmartAdvisor(risk_tolerance="中等")

# 获取数据
stock_code = "600519"
stock_name = "贵州茅台"
data = provider.get_stock_data(stock_code)
fundamental = provider.get_fundamental_data(stock_code)

# 分析
advice = advisor.analyze_stock(stock_code, stock_name, data, fundamental)

# 查看建议
print(f"信号: {advice.signal.value}")
print(f"信心度: {advice.confidence:.1f}%")
print(f"目标价: ¥{advice.target_price:.2f}")
print(f"止损价: ¥{advice.stop_loss:.2f}")
```

### 示例2: 扫描市场

```python
from data_layer.efinance_provider import EFinanceProvider
from strategy_layer.smart_advisor import SmartAdvisor, MarketScanner

# 创建扫描器
provider = EFinanceProvider()
advisor = SmartAdvisor(risk_tolerance="中等")
scanner = MarketScanner(advisor)

# 获取热门股票
stock_list = provider.get_hot_stocks(50)

# 扫描市场
advice_list = scanner.scan_market(
    stock_list=stock_list,
    data_provider=provider,
    min_confidence=60
)

# 获取最佳标的
top_picks = scanner.get_top_picks(advice_list, top_n=10)

for advice in top_picks:
    print(f"{advice.stock_name}: {advice.signal.value} "
          f"(评分: {advice.overall_score:.1f})")
```

### 示例3: 实时监控

```python
import time
from data_layer.efinance_provider import EFinanceProvider

provider = EFinanceProvider()

# 监控列表
watch_list = ["600519", "000858", "600036"]

while True:
    print("\n实时行情:")
    for code in watch_list:
        info = provider.get_stock_info(code)
        print(f"{info['name']}: ¥{info['price']:.2f} "
              f"({info['change_pct']:+.2f}%)")
    
    time.sleep(60)  # 每分钟更新
```

## ⚙️ 配置选项

### 数据提供者工厂

使用工厂模式创建不同类型的数据提供者：

```python
from data_layer.efinance_provider import DataProviderFactory

# 创建真实数据提供者
provider = DataProviderFactory.create_provider("efinance")

# 创建模拟数据提供者（用于测试）
provider = DataProviderFactory.create_provider("mock")
```

### 便捷函数

```python
from data_layer.efinance_provider import get_provider

# 快速获取默认提供者
provider = get_provider()
```

## 🐛 故障排除

### 问题1: 无法导入 efinance

**错误信息:**
```
ImportError: No module named 'efinance'
```

**解决方案:**
```bash
pip install efinance
```

### 问题2: 获取数据失败

**可能原因:**
1. 网络连接问题
2. efinance 服务暂时不可用
3. 股票代码错误

**解决方案:**
```python
# 检查网络连接
import requests
response = requests.get("https://www.baidu.com")
print(response.status_code)  # 应该返回 200

# 验证股票代码
# 确保使用正确的6位代码，如 "600519" 而不是 "sh600519"

# 查看详细错误信息
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 问题3: 数据不完整

**现象:**
- 基本面数据为默认值
- 技术指标缺失

**解决方案:**
```python
# 检查数据完整性
data = provider.get_stock_data("600519")
print(f"数据行数: {len(data)}")
print(f"列数: {len(data.columns)}")
print(f"列名: {data.columns.tolist()}")

# 确保至少有60天数据
if len(data) < 60:
    print("数据不足，需要更多历史数据")
```

### 问题4: 性能问题

**现象:**
- 扫描速度慢
- 内存占用高

**解决方案:**
```python
# 1. 减少扫描数量
stock_list = provider.get_hot_stocks(20)  # 从50减少到20

# 2. 使用缓存
provider.cache_timeout = 600  # 增加缓存时间

# 3. 批量处理
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(provider.get_stock_data, code) 
               for code, name in stock_list]
    results = [f.result() for f in futures]
```

## 📊 数据质量说明

### 数据来源
- **efinance**: 东方财富网数据接口
- **更新频率**: 实时（交易时间）
- **历史数据**: 支持获取完整历史

### 数据准确性
- ✅ 价格数据: 准确可靠
- ✅ 成交量: 准确可靠
- ⚠️ 基本面数据: 依赖公开披露，可能有延迟
- ⚠️ 技术指标: 基于历史数据计算，准确但有滞后性

### 使用建议
1. **交易时间**: 数据最准确
2. **盘后分析**: 建议收盘后30分钟再分析
3. **基本面**: 结合公司公告和财报
4. **技术指标**: 多指标综合判断

## 🔄 数据更新策略

### 推荐更新频率

```python
# 实时监控（交易时间）
update_interval = 60  # 1分钟

# 日常分析（盘后）
update_interval = 3600  # 1小时

# 长期投资
update_interval = 86400  # 1天
```

### 自动更新示例

```python
import schedule
from data_layer.efinance_provider import EFinanceProvider
from strategy_layer.smart_advisor import SmartAdvisor, MarketScanner

def daily_scan():
    """每日扫描任务"""
    provider = EFinanceProvider()
    advisor = SmartAdvisor(risk_tolerance="中等")
    scanner = MarketScanner(advisor)
    
    # 清除缓存
    provider.clear_cache()
    
    # 获取股票列表
    stock_list = provider.get_hot_stocks(50)
    
    # 扫描市场
    advice_list = scanner.scan_market(stock_list, provider)
    
    # 保存结果
    # ... 保存到数据库或文件
    
    print(f"扫描完成，找到 {len(advice_list)} 个机会")

# 每天15:30执行（收盘后）
schedule.every().day.at("15:30").do(daily_scan)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 📝 注意事项

1. **数据使用规范**
   - 仅供个人学习研究使用
   - 不得用于商业用途
   - 遵守相关法律法规

2. **投资风险提示**
   - 数据仅供参考
   - 不构成投资建议
   - 投资有风险，入市需谨慎

3. **技术限制**
   - 依赖网络连接
   - 可能受到API限制
   - 数据可能有延迟

4. **最佳实践**
   - 定期更新数据
   - 结合多种分析方法
   - 严格风险控制
   - 保持理性投资

## 🆘 获取帮助

如遇到问题：
1. 查看本文档的故障排除部分
2. 运行 `test_real_data.py` 诊断问题
3. 查看日志输出获取详细信息
4. 检查 efinance 官方文档

## 🔗 相关资源

- [efinance 官方文档](https://efinance.readthedocs.io)
- [efinance GitHub](https://github.com/Micro-sheep/efinance)
- [智能顾问使用指南](SMART_ADVISOR_GUIDE.md)
- [系统升级总结](UPGRADE_SUMMARY.md)
