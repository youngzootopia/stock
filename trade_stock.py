from PyQt5.QtWidgets import *
import sys
from kiwoom import Kiwoom
from mongo import Mongo
from ml_stock import Ml_stock
from teleBot import TeleBot


if __name__ == '__main__': # 중복 방지를 위해 사용
    # 키움 API 실행
    app = QApplication(sys.argv)
    Kiwoom = Kiwoom()
    Mongo = Mongo()
    TeleBot = TeleBot()

    app.exec_()
    
