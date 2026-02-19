import sys
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class QuantAnalyzerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Quant Analyzer')
        self.setGeometry(100, 100, 1200, 800)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        label = QLabel('Quant Analyzer Main Window - Under Development')
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
    
    def show(self):
        super().show()
        print('Main window displayed')