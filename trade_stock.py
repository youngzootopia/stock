from PyQt5.QtWidgets import *
from datetime import datetime
import exchange_calendars as xcals
import sys
from kiwoom import Kiwoom
from mongo import Mongo
from ml_stock import Ml_stock
from teleBot import TeleBot

def buy_predict_stock(dateStr, limit):
    for pred in Mongo.get_pred_close(dateStr, limit):

        Kiwoom.buy_stock(pred['_id']['code'], 0, 1) # 시장가, 1개 주문

if __name__ == '__main__': # 중복 방지를 위해 사용
    # 키움 API 실행
    app = QApplication(sys.argv)
    Kiwoom = Kiwoom()
    Mongo = Mongo()
    TeleBot = TeleBot()

    dateStr = datetime.today().strftime("%Y%m%d")
    XKRX = xcals.get_calendar("XKRX")
    openDate = XKRX.session_open(dateStr).strftime("%Y%m%d")

    buy_predict_stock(openDate, 30)


    app.exec_()
    
