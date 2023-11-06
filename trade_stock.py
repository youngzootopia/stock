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
        self.Kiwoom = Kiwoom()
        self.Mongo = Mongo()
        self.TeleBot = TeleBot()

    def register_real_stock_price(self, dateStr, limit):
        code_list_str = ""

        stock_dict = {}

        # 예상 종목
        for pred in self.Mongo.get_pred_close(dateStr, limit):
            stock = {}
            code_list_str = code_list_str + pred['_id']['code'] + ";"
        
            stock['pred_fluctuation_rate'] = pred['pred_fluctuation_rate']
            stock['pred_close'] = pred['pred_close']
            stock['quantity'] = 0
            stock['order_quantity'] = 0
            stock['buy_close'] = 0
            stock['available_quantity'] = 0
            stock_dict[pred['_id']['code']] = stock

        # 잔고 
        for balance_stock in self.Kiwoom.get_balance():
            if balance_stock['code'] in stock_dict: # 상승 종목에 잔고가 포함 되어 있을 수 있음
                stock['buy_close'] = balance_stock['buy_close']
                stock['available_quantity'] = balance_stock['available_quantity']    
            else: # 잔고에만 있는 종목의 경우
                stock = {}
                code_list_str = code_list_str + balance_stock['code'] + ";"

                stock['buy_close'] = balance_stock['buy_close']
                stock['available_quantity'] = balance_stock['available_quantity']
                stock_dict[balance_stock['code']] = stock

        fids = fid_codes.get_fid("체결시간") # 현제 체결시간만 등록해도 모든 데이터 가져옴. 키움 API 업데이트에 따라 리스트로 만들어야 할 수 있음

        print(stock_dict)

        self.Kiwoom.set_real_reg("9001", code_list_str, fids, "0", stock_dict)