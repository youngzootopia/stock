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

    Kiwoom.buy_stock('005930','','')

    app.exec_()
