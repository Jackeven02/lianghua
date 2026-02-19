"""
简化测试文件
"""

import pandas as pd
import numpy as np

def test_basic_functionality():
    """测试基本功能"""
    print("开始测试基本功能...")
    
    # 测试pandas和numpy
    try:
        # 创建测试数据
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        prices = 100 + np.cumsum(np.random.randn(100) * 0.02)
        data = pd.DataFrame({'close': prices}, index=dates)
        
        print(f"✓ pandas数据创建成功，形状: {data.shape}")
        
        # 测试基本计算
        returns = data['close'].pct_change()
        volatility = returns.std() * np.sqrt(252)
        print(f"✓ 基本计算成功，年化波动率: {volatility:.4f}")
        
        # 测试技术指标简单计算
        sma_20 = data['close'].rolling(20).mean()
        print(f"✓ 简单移动平均计算成功，长度: {len(sma_20.dropna())}")
        
        return True
        
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False

def test_imports():
    """测试导入功能"""
    print("\n测试导入功能...")
    
    try:
        import sys
        import os
        print("✓ 基础模块导入成功")
        
        # 测试相对导入
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        if project_root not in sys.path:
            sys.path.append(project_root)
        
        print("✓ 路径设置成功")
        return True
        
    except Exception as e:
        print(f"✗ 导入测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("Quant Analyzer 简化测试")
    print("=" * 50)
    
    results = []
    results.append(test_imports())
    results.append(test_basic_functionality())
    
    print("\n" + "=" * 50)
    print("测试结果:")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("🎉 基础功能测试通过！")
        print("下一步可以继续开发UI层和高级功能。")
    else:
        print("❌ 部分测试失败，请检查环境配置。")

if __name__ == '__main__':
    main()