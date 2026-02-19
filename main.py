"""
量化分析软件主程序
整合所有模块功能的入口点
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import APP_NAME, APP_VERSION, WINDOW_TITLE
from ui_layer.main_window import QuantAnalyzerMainWindow
from utils.logger import setup_logger

def main():
    """主函数"""
    # 设置日志
    setup_logger()
    logger = logging.getLogger(__name__)
    
    logger.info(f"启动 {APP_NAME} v{APP_VERSION}")
    
    # 设置高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    app.setApplicationName(WINDOW_TITLE)
    app.setApplicationVersion(APP_VERSION)
    
    # 创建主窗口
    try:
        main_window = QuantAnalyzerMainWindow()
        main_window.show()
        logger.info("主窗口已显示")
        
        # 运行应用程序
        exit_code = app.exec_()
        logger.info("应用程序已退出")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"启动应用程序时出错: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()