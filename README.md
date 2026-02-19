# Quant Analyzer 量化分析软件

## 项目概述

Quant Analyzer 是一个专业的量化分析软件，基于Python开发，提供完整的金融数据分析、策略回测和风险管理功能。该软件将传统的金融数据查询工具升级为专业的量化分析平台。

## 核心功能

### 📊 数据层 (Data Layer)
- **数据获取**: 支持股票、基金、指数等多品种数据获取
- **数据处理**: 数据清洗、标准化、特征工程
- **数据存储**: 本地数据库缓存，提高查询效率
- **数据管理**: 收藏管理、查询历史记录

### 📈 分析层 (Analysis Layer)
- **技术指标**: SMA、EMA、MACD、RSI、KDJ、布林带等20+技术指标
- **统计分析**: 收益率分析、波动率计算、风险指标评估
- **信号生成**: 基于技术指标的交易信号生成
- **绩效评估**: 夏普比率、最大回撤、胜率等关键指标

### 🎯 策略层 (Strategy Layer)
- **策略引擎**: 支持多种量化策略类型
- **回测系统**: 完整的历史回测功能
- **参数优化**: 网格搜索、遗传算法参数优化
- **策略管理**: 策略注册、激活、组合管理

### ⚠️ 风险层 (Risk Layer)
- **风险管理**: 仓位控制、风险限额设置
- **风险监控**: 实时风险监控和预警
- **仓位管理**: 凯利公式、固定比例等多种仓位管理方法
- **异常检测**: 市场异常波动检测

## 技术架构

```
quant_analyzer/
├── data_layer/          # 数据层
│   ├── data_provider.py    # 数据提供者
│   ├── data_processor.py   # 数据处理器
│   └── data_storage.py     # 数据存储
├── analysis_layer/      # 分析层
│   ├── technical_indicators.py  # 技术指标
│   └── statistical_analysis.py  # 统计分析
├── strategy_layer/      # 策略层
│   ├── strategy_engine.py       # 策略引擎
│   └── backtesting.py           # 回测系统
├── risk_layer/          # 风险层
│   └── risk_manager.py          # 风险管理
├── ui_layer/            # 界面层（待开发）
├── config/              # 配置文件
├── utils/               # 工具模块
├── logs/                # 日志文件
├── exports/             # 导出数据
└── main.py             # 主程序入口
```

## 安装和使用

### 环境要求
- Python 3.8+
- Windows 10/11 (推荐)
- 8GB+ 内存

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行测试
```bash
python test_quant.py
```

### 启动程序
```bash
python main.py
```

## 功能特色

### 🔧 专业量化功能
- **多因子分析**: 价值、成长、质量、动量因子分析
- **组合优化**: 马科维茨均值方差优化
- **机器学习**: 集成scikit-learn进行预测分析
- **时间序列**: ARIMA、GARCH模型支持

### 📊 数据可视化
- **K线图**: 专业级K线图表显示
- **指标图**: 技术指标可视化
- **热力图**: 相关性矩阵热力图
- **回测图表**: 策略绩效可视化展示

### 🛡️ 风险控制
- **实时监控**: 持仓风险实时监控
- **智能止损**: 多种止损策略
- **仓位管理**: 动态仓位调整
- **压力测试**: 极端行情风险评估

## 开发计划

### 第一阶段：基础框架 ✓
- [x] 项目目录结构重构
- [x] 数据层模块开发
- [x] 分析层模块开发
- [x] 策略层模块开发
- [x] 风险层模块开发

### 第二阶段：核心功能
- [ ] 界面层开发
- [ ] 策略编辑器
- [ ] 可视化组件
- [ ] 报告生成系统

### 第三阶段：高级功能
- [ ] 机器学习集成
- [ ] 实时数据接口
- [ ] 多市场支持
- [ ] 云服务部署

## 使用示例

```python
# 导入模块
from data_layer import get_stock_data
from analysis_layer import calculate_all_technical_indicators
from strategy_layer import TechnicalStrategy, run_backtest
from risk_layer import calculate_optimal_position_size

# 获取数据
data = get_stock_data('000001', period='daily', add_indicators=True)

# 技术分析
indicators_data = calculate_all_technical_indicators(data)

# 策略回测
strategy = TechnicalStrategy('均线策略', ['SMA', 'RSI'])
results = run_backtest(strategy, data, initial_capital=1000000)

# 风险管理
position_size = calculate_optimal_position_size(
    capital=1000000, 
    entry_price=10.5, 
    stop_loss_price=9.5,
    method='fixed_fractional'
)

print(f"建议仓位: {position_size} 股")
```

## 许可证

MIT License

## 免责声明

本软件仅供学习和研究使用，不构成任何投资建议。投资有风险，入市需谨慎。

---
**Quant Analyzer - 让量化分析更简单！**