import sys
from unittest import result

from PyQt5.QtGui import QCursor, QPixmap

import functions
import functions
import requests
import json
from PyQt5.QtWidgets import QApplication, QComboBox, QPushButton, QTableWidgetItem, QSpinBox, QMainWindow, QLineEdit, \
    QWidget, QVBoxLayout, QLabel, QMessageBox
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
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
        # self.ui.buy_btn.clicked.connect(self.message_text())
        self.ui.buy_btn_2.clicked.connect(self.search)
        self.ui.buy_btn_2.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.add_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.delete_btn.setCursor(QCursor(Qt.PointingHandCursor))

    def eventFilter(self, obj, event):
        if obj == self.ui.marketTable.viewport():
            if event.type() == QtCore.QEvent.MouseButtonPress:
                index = self.ui.marketTable.indexAt(event.pos())
                if not index.isValid():
                    self.ui.marketTable.clearSelection()
        return super().eventFilter(obj, event)

    # @staticmethod
    # def create_scaled_pixmap(image_data: bytes, size=35):
    #     pixmap = QPixmap()
    #     pixmap.loadFromData(image_data)
    #
    #     return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def search(self):
        self.search_window = SearchWindow(self.platform, self.crossplay)
        self.search_window.submitted.connect(self.handle_search)
        self.search_window.show()

    def handle_search(self, data):
        result = functions.collect_data_parts(
            data["name"],
            data["type"],
            self.platform,
            data["quantity"],
            data["wishedPrice"],
            self.crossplay
        )

        if not result:
            info_message = QMessageBox(window)
            info_message.setWindowTitle("Ошибка")
            info_message.setText(f"Заказ ' {data['name']} ' стоимостью {data['wishedPrice']} ед. платины не найден.")
            info_message.exec_()
            return

        for i in result:
            icon_url = functions.get_api_icon(data["name"])
            image_bytes = functions.download_icon_bytes(icon_url)


            row = self.ui.marketTable.rowCount()
            self.ui.marketTable.insertRow(row)
            self.ui.marketTable.setRowHeight(row, 50)

            if image_bytes is not None:
                pixmap = functions.bytes_to_image(image_bytes)
                pixmap = pixmap.scaled(45, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label = QLabel()
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignCenter)
                self.ui.marketTable.setCellWidget(
                    row, 0, label)
            else:
                self.ui.marketTable.setItem(
                    row, 0, QTableWidgetItem("No Image"))
            self.ui.marketTable.setItem(
                row, 1, QTableWidgetItem(i["ingameName"]))
            self.ui.marketTable.setItem(
                row, 2, QTableWidgetItem(i["name"].replace("_", " ").title()))
            self.ui.marketTable.setItem(
                row, 3, QTableWidgetItem(i["type"]))
            self.ui.marketTable.setItem(
                row, 4, QTableWidgetItem(str(i["quantity"])))
            self.ui.marketTable.setItem(
                row, 5, QTableWidgetItem(str(i["price"])))
            self.ui.marketTable.setItem(
                row, 6, QTableWidgetItem(str(data["wishedPrice"])))

            self.buy_button_copy(row)

            y_buy_btn = 215 + 55 * int(row) + 15

            self.ui.buy_btn_2.setGeometry(QtCore.QRect(1130, y_buy_btn, 111, 38))

        self.ui.marketTable.setSortingEnabled(True)

    def buy_button_copy(self, row):
        x = self.ui.buy_btn.x()
        y = self.ui.buy_btn.y() + 50 * int(row)
        width = self.ui.buy_btn.width()
        height = self.ui.buy_btn.height() + 10

        button = QtWidgets.QPushButton(self.centralWidget())
        button.setGeometry(QtCore.QRect(x, y, width, height))
        button.setStyleSheet(self.ui.buy_btn.styleSheet())
        button.setIcon(self.ui.buy_btn.icon())
        button.setText(self.ui.buy_btn.text())
        button.setObjectName(f"buy_btn_{row}")
        button.setCursor(QCursor(Qt.PointingHandCursor))

        button.clicked.connect(lambda x, r=row: self.message_text(r))
        button.show()

    def message_text(self, row):
        ingameName = self.ui.marketTable.item(row, 1).text()
        name = self.ui.marketTable.item(row, 2).text()
        price = self.ui.marketTable.item(row, 5).text()

        message = f"/w {ingameName} Hi! I want to buy: '{name}' for {price} platinum. (warframe.market)"
        QApplication.clipboard().setText(message)
        print(f"Сообщение для {ingameName} скопировано")



class SearchWindow(QWidget):
    submitted = pyqtSignal(dict)
    def __init__(self, platform: str = "pc", crossplatform: bool = True):
        super().__init__()
        layout = QVBoxLayout()

        self.platform = platform
        self.crossplatform = crossplatform
        
        
        self.result = []

        label1 = QLabel("Название предмета")
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

# вызов через кнопку функции sub()
        self.submit = QPushButton()
        self.submit.setText("Подтвердить")
        self.submit.clicked.connect(self.sub)
        layout.addWidget(self.submit)

        self.setLayout(layout)

#
    def sub(self):
        try:            
            data = {
                "name": self.name.text(),
                "wishedPrice": int(self.max_price.text()),
                "type": self.combo.currentData(),
                "quantity": int(self.quantity.text())
            }
            self.submitted.emit(data)
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
