from PyQt5.QtWidgets import *
import sys
from kiwoom import Kiwoom
from mongo import Mongo
from ml_stock import Ml_stock

if __name__ == '__main__': # 중복 방지를 위해 사용
    # app = QApplication(sys.argv)
    # Kiwoom = Kiwoom()
    # Mongo = Mongo()
    Ml_stock = Ml_stock()

    Ml_stock.predict_stock_close_price("466810", '20231026')

    # orders = Kiwoom.get_deposit()
    # print(orders)

    # app.exec_()