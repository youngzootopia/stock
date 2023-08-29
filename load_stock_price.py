from PyQt5.QtWidgets import *
import sys
from win32 import Login
from kiwoom import Kiwoom
from mongo import Mongo
import multiprocessing

if __name__ == '__main__': # 중복 방지를 위해 사용
    app = QApplication(sys.argv)
    Kiwoom = Kiwoom()
    Mongo = Mongo()

    # 종목 정보 가져오기
    kospi_list = Kiwoom.get_code_list_stok_market("0")
    # kodak_list = Kiwoom.get_code_list_stok_market("10")

    for kospi in kospi_list:
        print(kospi)
        stock_price = Kiwoom.get_price(kospi)
        stock_price.insert(0, "code", kospi)
        Mongo.insert_price_many(stock_price)

    app.exec_()
