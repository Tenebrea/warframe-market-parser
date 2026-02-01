import sys

import requests
import json
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore
from main_gui import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.marketTable.viewport().installEventFilter(self)
        # self.ui.add_btn.clicked.connect(self.add_item)
        # self.ui.delete_btn.clicked.connect(self.delete_item)

        #
        # def add_item(self):
        #     print("Добавить запись")
        #
        # def delete_item(self):
        #     print("Удалить запись")

    def eventFilter(self, obj, event):
        if obj == self.ui.marketTable.viewport():
            if event.type() == QtCore.QEvent.MouseButtonPress:
                index = self.ui.marketTable.indexAt(event.pos())
                if not index.isValid():
                    self.ui.marketTable.clearSelection()
        return super().eventFilter(obj, event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())




# def collect_data(item):
#     url_name = warframe_to_url(item)
#     r = requests.get(f"https://api.warframe.market/v2/orders/item/{url_name}")
#     r_json = r.json()
#
#     #https://api.warframe.market/v2/item/atlas_prime_set/set
#     #https://api.warframe.market/v2/items/atlas_prime_set
#     #https://api.warframe.market/v2/riven/weapon/{}
#     #https://api.warframe.market/v2/orders/item/atlas_prime_set
#
#     with open('min.json', 'w') as file:
#         json.dump(r_json, file, indent=4, ensure_ascii=False)
#
# def warframe_to_url(item):
#
#     if item.lower() == "атлас прайм сет":
#         url_name = "atlas_prime_set"
#     elif item.lower() == "атлас прайм комплект":
#         url_name = "atlas_prime_set"
#     elif item.lower() == "атлас прайм каркас":
#         url_name = "atlas_prime_chassis"
#     elif item.lower() == "атлас прайм система":
#         url_name = "atlas_prime_systems"
#     elif item.lower() == "атлас прайм нейрооптика":
#         url_name = "atlas_prime_neuroptics"
#     elif item.lower() == "атлас прайм чертёж":
#         url_name = "atlas_prime_blueprint"
#     elif item.lower() == "атлас прайм чертеж":
#         url_name = "atlas_prime_blueprint"
#
#     return url_name
#
#
# collect_data("атлас прайм сет")