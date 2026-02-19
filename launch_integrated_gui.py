"""
启动集成版GUI界面
"""
import sys
import os

def launch():
    """启动集成版GUI"""
    try:
        # 添加项目路径
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from integrated_simple_gui import main
        print("正在启动集成版智能投资顾问系统...")
        print("功能包括：")
        print("- 单股分析")
        print("- 市场扫描") 
        print("- 技术指标分析")
        print("- 投资建议生成")
        print("- 风险评估")
        print("\n请在GUI界面中输入股票代码和名称开始分析。")
        print("提示：可以尝试 600519 (贵州茅台) 或 000001 (平安银行)")
        main()
    except ImportError as e:
        print(f"导入GUI模块失败: {e}")
        print("请确保已安装所需依赖: pip install PyQt5 pandas numpy efinance")
    except Exception as e:
        print(f"启动GUI时发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    launch()