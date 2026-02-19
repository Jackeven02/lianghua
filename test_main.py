import sys
import os
from PyQt5.QtWidgets import QApplication

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config.settings import APP_NAME, APP_VERSION
from ui_layer.main_window import QuantAnalyzerMainWindow

def main():
    print(f'Starting {APP_NAME} v{APP_VERSION}')
    
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    try:
        main_window = QuantAnalyzerMainWindow()
        main_window.show()
        print('Main window displayed successfully')
        exit_code = app.exec_()
        print('Application exited')
        sys.exit(exit_code)
    except Exception as e:
        print(f'Error starting application: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main()
