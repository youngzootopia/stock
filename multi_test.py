from PyQt5.QtWidgets import *
import sys
import threading
import time
from datetime import datetime
import exchange_calendars as xcals

from kiwoom import Kiwoom
from trade_stock import Trade_stock

class IntervalThread(threading.Thread):
    def __init__(self, kiwoom, trade_stock):
        threading.Thread.__init__(self)
        self.kiwoom = kiwoom
        self.trade_stock = trade_stock

    def get_order(self):
        self.kiwoom.order_list = self.kiwoom.get_order()
        print(self.kiwoom.order_list)

    def get_deposit(self):
        self.kiwoom.get_deposit()        
        print(self.kiwoom.deposit)
    
class TradeThread(threading.Thread):
    def __init__(self, kiwoom, trade_stock):
        threading.Thread.__init__(self)
        self.kiwoom = kiwoom
        self.trade_stock = trade_stock

    def register_real_stock_price(self):
        dateStr = datetime.today().strftime("%Y%m%d")
        XKRX = xcals.get_calendar("XKRX")
        openDate = XKRX.session_open(dateStr).strftime("%Y%m%d")

        self.trade_stock.register_real_stock_price(openDate, 30)
        

if __name__ == '__main__': # 중복 방지를 위해 사용
    app = QApplication(sys.argv)

    kiwoom = Kiwoom()
    trade_stock = Trade_stock(kiwoom)

    register_thread = TradeThread(kiwoom, trade_stock)
    register_thread.start()
    register_thread.register_real_stock_price()

    order_and_deposit_thread = IntervalThread(kiwoom, trade_stock)
    order_and_deposit_thread.start()

    while True: 
        order_and_deposit_thread.get_deposit()
        order_and_deposit_thread.get_order()

    app.exec_()

