# -*- coding: utf-8 -*-
"""
测试真实数据获取
快速验证efinance数据提供者是否正常工作
"""

import sys
import os
import logging

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from data_layer.efinance_provider import EFinanceProvider
from strategy_layer.smart_advisor import SmartAdvisor


def test_data_provider():
    """测试数据提供者"""
    print("\n" + "=" * 80)
    print("测试 efinance 数据提供者")
    print("=" * 80 + "\n")
    
    try:
        provider = EFinanceProvider()
        
        # 测试1: 获取股票数据
        print("1. 测试获取股票历史数据...")
        stock_code = "600519"
        data = provider.get_stock_data(stock_code)
        
        if not data.empty:
            print(f"   成功获取 {stock_code} 数据")
            print(f"   - 数据行数: {len(data)}")
            print(f"   - 最新价格: {data['close'].iloc[-1]:.2f}")
        else:
            print(f"   获取数据失败")
            return False
        
        # 测试2: 获取基本面数据
        print("\n2. 测试获取基本面数据...")
        fundamental = provider.get_fundamental_data(stock_code)
        
        if fundamental:
            print(f"   成功获取基本面数据")
            print(f"   - ROE: {fundamental.get('roe', 0):.2f}%")
        else:
            print(f"   获取基本面数据失败")
        
        print("\n" + "=" * 80)
        print("数据提供者测试通过！")
        print("=" * 80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n真实数据测试程序\n")
    
    if not test_data_provider():
        print("\n警告: 数据提供者测试失败")
        print("请检查:")
        print("1. 是否已安装 efinance: pip install efinance")
        print("2. 网络连接是否正常")
        return
    
    print("\n所有测试通过！系统可以正常使用真实数据。\n")


if __name__ == "__main__":
    main()
