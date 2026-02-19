import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

class QuantAnalyzerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Quant Analyzer v1.0.0')
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        title_label = QLabel('Quant Analyzer - Professional Quantitative Analysis Platform')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('font-size: 24px; font-weight: bold; margin: 20px;')
        layout.addWidget(title_label)
        
        status_label = QLabel('Status:\n Data Layer - Completed\n Analysis Layer - Completed\n Strategy Layer - Completed\n Risk Layer - Completed\n UI Layer - In Development')
        status_label.setAlignment(Qt.AlignLeft)
        status_label.setStyleSheet('font-size: 14px; margin: 20px;')
        layout.addWidget(status_label)
        
        info_label = QLabel('Progress: Phase 1 Complete (100%), Overall 60%')
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet('font-size: 16px; color: #27ae60; margin: 20px;')
        layout.addWidget(info_label)
        
    def show(self):
        super().show()
        print('Quant Analyzer main window displayed')

def main():
    print('Starting Quant Analyzer v1.0.0')
    app = QApplication(sys.argv)
    app.setApplicationName('Quant Analyzer')
    app.setApplicationVersion('1.0.0')
    
    try:
        main_window = QuantAnalyzerMainWindow()
        main_window.show()
        print('Main window launched successfully')
        exit_code = app.exec_()
        print('Application exited')
        return exit_code
    except Exception as e:
        print(f'Launch failed: {str(e)}')
        return 1

if __name__ == '__main__':
    sys.exit(main())
