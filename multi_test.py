from PyQt5.QtWidgets import *
import sys
import threading

from kiwoom import Kiwoom

class MyThread(threading.Thread):
    def __init__(self, kiwoom):
        threading.Thread.__init__(self)
        self.kiwoom = kiwoom

    def get_balance(self):
        return self.kiwoom.get_balance()

    def get_order(self):
        return self.kiwoom.get_order()

if __name__ == '__main__': # 중복 방지를 위해 사용
    app = QApplication(sys.argv)

    kiwoom = Kiwoom()

    balance_thread = MyThread(kiwoom)
    order_thread = MyThread(kiwoom)

    balance_thread.start()
    order_thread.start()

    balance = balance_thread.get_balance()
    print(f"예수금: {balance}")
    order_list = order_thread.get_order()
    print(f"주문내역: {order_list}")

    app.exec_()

