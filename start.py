# -*- coding: utf-8 -*-
"""
智能投资顾问系统 - 启动程序
"""
import sys
import os

print("\n")
print("╔" + "═" * 78 + "╗")
print("║" + " " * 25 + "智能投资顾问系统" + " " * 33 + "║")
print("╚" + "═" * 78 + "╝")
print()

print("请选择功能:")
print()
print("1. GUI界面 - 图形化界面（推荐）")
print("2. 快速测试 - 验证数据连接")
print("3. 单股分析 - 分析单只股票")
print("4. 市场扫描 - 扫描多只股票寻找机会")
print("5. 退出")
print()

choice = input("请输入选择 (1-5): ").strip()

if choice == "1":
    print("\n正在启动GUI界面...")
    print("提示: GUI窗口已打开，请在窗口中操作")
    os.system("python start_gui.py")
    
elif choice == "2":
    print("\n正在运行快速测试...")
    os.system("python quick_start.py")
    
elif choice == "3":
    print("\n正在运行单股分析...")
    os.system("python demo_advisor.py")
    
elif choice == "4":
    print("\n正在运行市场扫描...")
    os.system("python demo_scanner.py")
    
elif choice == "5":
    print("\n再见！")
    
else:
    print("\n无效的选择")

print()
