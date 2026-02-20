"""
量化分析软件配置文件
"""

import os

# 项目基本信息
PROJECT_NAME = "QuantFinance Pro"
PROJECT_VERSION = "1.0.0"
PROJECT_AUTHOR = "QuantFinance Team"

# 数据配置
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
CACHE_DIR = os.path.join(DATA_DIR, 'cache')
EXPORT_DIR = os.path.join(DATA_DIR, 'exports')

# 数据库配置
DATABASE_PATH = os.path.join(DATA_DIR, 'quant_finance.db')
DATABASE_INIT = True

# 界面配置
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
WINDOW_TITLE = f"{PROJECT_NAME} v{PROJECT_VERSION}"

# 计算配置
DEFAULT_CAPITAL = 1000000  # 默认初始资金
COMMISSION_RATE = 0.0003   # 佣金费率
SLIPPAGE = 0.001          # 滑点

# 技术指标配置
DEFAULT_INDICATORS = [
    'SMA', 'EMA', 'MACD', 'RSI', 'KDJ', 'BOLL', 'CCI', 'ROC'
]

# 回测配置
BACKTEST_DEFAULT_PERIOD = 252  # 默认回测周期（交易日）
RISK_FREE_RATE = 0.03         # 无风险利率

# 选股配置
DEFAULT_SCREEN_COUNT = 20     # 默认筛选股票数量
FACTOR_WEIGHTS = {
    'value': 0.25,
    'growth': 0.25, 
    'quality': 0.25,
    'momentum': 0.25
}

# 风险管理配置
MAX_POSITION_SIZE = 0.1       # 单个股票最大仓位
STOP_LOSS_RATE = 0.05         # 止损比例
TAKE_PROFIT_RATE = 0.15       # 止盈比例

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'