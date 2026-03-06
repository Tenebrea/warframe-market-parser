import os.path
import sys
from unittest import result

import settings_manager
from PyQt5.QtGui import QCursor, QPixmap

import functions
import functions
import requests
import json
from PyQt5.QtWidgets import QApplication, QComboBox, QPushButton, QTableWidgetItem, QSpinBox, QMainWindow, QLineEdit, \
    QWidget, QVBoxLayout, QLabel, QMessageBox, QDialog
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from main_gui import Ui_MainWindow
import threading

from second_gui import Ui_SettingsWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.settings_window = SettingsWindow()

        self.ui.setupUi(self)
        self.result = []
        
        self.crossplay = True
        self.platform = "pc"

        # self.platform = settings["platform"]
        # self.crossplay = settings["crossplatform"]

        self.ui.marketTable.viewport().installEventFilter(self)
        # self.ui.buy_btn.clicked.connect(self.message_text())
        self.ui.buy_btn_2.clicked.connect(self.search)
        self.ui.buy_btn_2.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.add_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.delete_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.ui.settings_btn.clicked.connect(self.open_settings)
        self.apply_settings()

    def eventFilter(self, obj, event):
        if obj == self.ui.marketTable.viewport():
            if event.type() == QtCore.QEvent.MouseButtonPress:
                index = self.ui.marketTable.indexAt(event.pos())
                if not index.isValid():
                    self.ui.marketTable.clearSelection()
        return super().eventFilter(obj, event)

    def open_settings(self):
        settings_window = SettingsWindow()
        if settings_window.exec_() == QDialog.Accepted:
            self.apply_settings()

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

            y_buy_btn = self.ui.buy_btn_2.y() + 55 * int(row) + 15

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

        copy_message = QMessageBox(window)
        copy_message.setWindowTitle("Сообщение")
        copy_message.setText(f"Сообщение для связи с игроком {ingameName} скопировано!")
        copy_message.exec_()

    # def show_settings(self):
    #     settings_window = SettingsWindow()
    #     if settings_window.exec_() == QDialog.Accepted:
    #         self.apply_settings()

    def apply_settings(self):
        if not os.path.exists("settings.json"):
            return

        with open("settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)
            print(settings)

        self.ui.lbl_current_name.setText(settings["username"])

        platform_map = {
            "pc": "ПК",
            "ps4": "PlayStation",
            "xbox": "Xbox",
            "switch": "Switch",
            "mobile": "Мобильные"
        }

        crossplay_map = {
            True: "Да",
            False: "Нет"
        }

        self.ui.lbl_current_platform.setText(
            platform_map.get(settings["platform"])
        )

        self.ui.lbl_current_crossplat.setText(
            crossplay_map.get(settings["crossplay"])
        )

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

        self.submit = QPushButton()
        self.submit.setText("Подтвердить")
        self.submit.clicked.connect(self.sub)
        layout.addWidget(self.submit)

        self.setLayout(layout)


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

class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.save_button_clicked)
        self.load_settings()

        self.ui.comboBox.setItemData(0, "pc")
        self.ui.comboBox.setItemData(1, "ps4")
        self.ui.comboBox.setItemData(2, "xbox")
        self.ui.comboBox.setItemData(3, "switch")
        self.ui.comboBox.setItemData(4, "mobile")

        self.ui.comboBox_2.setItemData(0, True)
        self.ui.comboBox_2.setItemData(1, False)


    def save_button_clicked(self):
        name = self.ui.lineEdit.text()
        platform = self.ui.comboBox.currentData()
        crossplay = self.ui.comboBox_2.currentData()

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение")
        msg_box.setText("Изменить настройки?")

        yes_button = msg_box.addButton("Да", QMessageBox.YesRole)
        no_button = msg_box.addButton("Нет", QMessageBox.NoRole)

        msg_box.exec_()

        if msg_box.clickedButton() == yes_button:
            data = {
                "username": name,
                "platform": platform,
                "crossplay": crossplay
            }

            with open("settings.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            self.accept()
        else:
            self.reject()

    def load_settings(self):
        try:
            with open("settings.json", "r", encoding="utf-8") as f:
                data = json.load(f)

                self.ui.lineEdit.setText(data["username"])

                index_platform = self.ui.comboBox.findData(data["platform"])
                self.ui.comboBox.setCurrentIndex(index_platform)

                index_crossplay = self.ui.comboBox_2.findData(data["crossplay"])
                self.ui.comboBox_2.setCurrentIndex(index_crossplay)

        except FileNotFoundError:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
