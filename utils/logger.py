"""
日志工具模块
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from config.settings import LOG_LEVEL, LOG_FILE

def setup_logger(level=None, log_file=None):
    """设置日志配置"""
    
    if level is None:
        level = LOG_LEVEL
    if log_file is None:
        log_file = LOG_FILE
    
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 配置根日志记录器
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除现有的处理器
    logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        try:
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            # 创建文件处理器
            file_handler = RotatingFileHandler(
                log_file, 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"无法创建日志文件 {log_file}: {e}")

def get_logger(name):
    """获取指定名称的日志记录器"""
    return logging.getLogger(name)