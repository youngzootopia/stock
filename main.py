from PyQt5.QtWidgets import *
import sys
from kiwoom import Kiwoom
from mongo import Mongo

if __name__ == '__main__': # 중복 방지를 위해 사용
    app = QApplication(sys.argv)
    Kiwoom = Kiwoom()
    Mongo = Mongo()

    orders = Kiwoom.get_deposit()
    print(orders)

    app.exec_()
