"""
量化分析软件配置文件
"""

import os

# 应用程序基本信息
APP_NAME = "Quant Analyzer"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Quant Team"

# 数据库配置
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'quant.db')
DATABASE_INIT = True

# 界面配置
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"

# 数据获取配置
DEFAULT_TIMEOUT = 30  # 请求超时时间（秒）
MAX_RETRY = 3         # 最大重试次数

# 缓存配置
CACHE_ENABLED = True
CACHE_EXPIRE_TIME = 300  # 缓存过期时间（秒）

# 图表配置
DEFAULT_CHART_STYLE = 'seaborn'
CHART_DPI = 100
CHART_FIGSIZE = (12, 8)

# 回测配置
DEFAULT_INITIAL_CAPITAL = 1000000  # 默认初始资金
DEFAULT_COMMISSION = 0.001         # 默认手续费率
DEFAULT_SLIPPAGE = 0.0005          # 默认滑点

# 导出配置
EXPORT_DIR = os.path.join(os.path.dirname(__file__), '..', 'exports')
EXPORT_FORMATS = ['xlsx', 'csv', 'json']

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'quant.log')

# 量化分析配置
TECHNICAL_INDICATORS = [
    'SMA', 'EMA', 'MACD', 'RSI', 'KDJ', 'BOLL', 
    'CCI', 'ROC', 'WILLR', 'OBV', 'ATR', 'ADX'
]

STRATEGY_TYPES = [
    'technical', 'fundamental', 'machine_learning', 'arbitrage'
]

RISK_METRICS = [
    'sharpe_ratio', 'max_drawdown', 'volatility', 'var', 'cvar'
]