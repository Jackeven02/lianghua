
import sys
sys.path.insert(0, '.')

print('Testing import...')

try:
    from strategy_layer.smart_strategy_engine import SmartMarketAnalyzer
    print(' Import successful!')
    
    analyzer = SmartMarketAnalyzer()
    print(' Instance created!')
    
    print('All tests passed!')
except Exception as e:
    print(f' Error: {e}')
    import traceback
    traceback.print_exc()
