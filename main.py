import sys
import functions
import requests
import json
from PyQt5.QtWidgets import QApplication, QComboBox, QPushButton, QTableWidgetItem, QSpinBox, QMainWindow, QLineEdit, QWidget, QVBoxLayout, QLabel
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, Qt
from main_gui import Ui_MainWindow
import threading


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.result = []
        
        self.crossplay = True
        self.platform = "pc"

        self.ui.marketTable.viewport().installEventFilter(self)
        self.ui.buy_btn_2.clicked.connect(self.search)

    def eventFilter(self, obj, event):
        if obj == self.ui.marketTable.viewport():
            if event.type() == QtCore.QEvent.MouseButtonPress:
                index = self.ui.marketTable.indexAt(event.pos())
                if not index.isValid():
                    self.ui.marketTable.clearSelection()
        return super().eventFilter(obj, event)

    def search(self):
        self.search_window = SearchWindow()
        self.search_window.destroyed.connect(self.search_closed)
        self.search_window.show()

    def search_closed(self):
        if self.result != []:
            for i in self.result:
                row = self.ui.marketTable.rowCount()
                self.ui.marketTable.insertRow(row)
                self.ui.marketTable.setItem(
                    row, 1, QTableWidgetItem(i["ingameName"]))
                self.ui.marketTable.setItem(
                    row, 2, QTableWidgetItem(self.current_name))
                self.ui.marketTable.setItem(
                    row, 3, QTableWidgetItem(i["type"]))
                self.ui.marketTable.setItem(
                    row, 4, QTableWidgetItem(str(i["quantity"])))
                self.ui.marketTable.setItem(
                    row, 5, QTableWidgetItem(str(i["price"])))
                self.ui.marketTable.setItem(
                    row, 6, QTableWidgetItem(str(self.current_wished_price)))
            self.ui.marketTable.setSortingEnabled(True)
            self.ui.marketTable.sortItems(5, Qt.AscendingOrder)
            self.ui.marketTable.sortItems(2, Qt.AscendingOrder)


class SearchWindow(QWidget):
    def __init__(self, platform: str = "pc", crossplatform: bool = True):
        super().__init__()
        layout = QVBoxLayout()

        self.platform = platform
        self.crossplatform = crossplatform
        
        
        self.result = []

        label1 = QLabel("Название предмета(на английском)")
        label2 = QLabel("Желаемая цена")
        label3 = QLabel("Количество")

        layout.addWidget(label1)

        self.name = QLineEdit()
        layout.addWidget(self.name)

        layout.addWidget(label2)

        self.max_price = QSpinBox()
        self.max_price.setRange(1, 99999)
        self.max_price.setSingleStep(1)
        layout.addWidget(self.max_price)

        layout.addWidget(label3)

        self.quantity = QSpinBox()
        self.quantity.setMinimum(1)
        self.quantity.setMaximum(99999)
        self.quantity.setSingleStep(1)
        layout.addWidget(self.quantity)

        self.combo = QComboBox()
        self.combo.addItems(["Купить", "Продать"])
        self.combo.setItemData(0, "sell")
        self.combo.setItemData(1, "buy")
        self.combo.setCurrentIndex(0)
        layout.addWidget(self.combo)

        self.submit = QPushButton()
        self.submit.setText("Подтвердить")
        self.submit.clicked.connect(self.sub)
        layout.addWidget(self.submit)

        self.setLayout(layout)

    def sub(self):
        try:            
            window.result.append({
            "name": self.name.text(),
            "wished_price": int(self.max_price.text()),
            "type": self.combo.currentData(),
            "quantity": int(self.quantity.text())
            })
            self.close()
        except Exception as e:
            self.w = PopupWindow(str(e))
            self.w.show()


class PopupWindow(QWidget):
    def __init__(self, error_text: str):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel(error_text)
        layout.addWidget(label)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
