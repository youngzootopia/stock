from PyQt5.QtWidgets import *
from datetime import datetime
import exchange_calendars as xcals
import sys
from kiwoom import Kiwoom
from mongo import Mongo
from ml_stock import Ml_stock
from teleBot import TeleBot
import fid_codes


class Trade_stock():
    def __init__(self): # QAxWidget 상속 받은 경우 오버라이딩 필요
        app = QApplication(sys.argv)
        self.Kiwoom = Kiwoom()
        self.Mongo = Mongo()
        self.TeleBot = TeleBot()

        app.exec_()        


    # 종목코드, 등락률, close(현재가)
    def buy_stock(self, code, fluctuation_rate, close):
        # 예수금 조회
        deposit = self.Kiwoom.get_deposit()
        print("예수금: ", deposit)

        # 미체결 요청 가져오기
        # orders = Kiwoom.get_order()
        # print(orders)
        
        # 매수 Strat
        # 만원어치 이상 구매
        quantity = 1
        while quantity * close < 10000:
            quantity = quantity + 1

        # 예수금이 남아 있어야 함
        if deposit - 100000 > quantity * close:    
            Kiwoom.buy_stock(code, close, quantity)    

    def sell_stock(self):
        # 잔고 얻어오기 opw00018
        print()

    def register_real_stock_price(self, dateStr, limit):
        code_list_str = ""

        for pred in self.Mongo.get_pred_close(dateStr, limit):
            code_list_str = code_list_str + pred['_id']['code'] + ";"

        fids = fid_codes.get_fid("체결시간") # 현제 체결시간만 등록해도 모든 데이터 가져옴. 키움 API 업데이트에 따라 리스트로 만들어야 할 수 있음
        self.Kiwoom.set_real_reg("9001", code_list_str, fids, "0")

Trade_stock = Trade_stock()