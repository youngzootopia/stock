from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import time
import pandas as pd

class Kiwoom(QAxWidget):
    def __init__(self): # QAxWidget 상속 받은 경우 오버라이딩 필요
        super().__init__()
        self._make_kiwoom_instance() # 키움 증권 로그인 창 띄우기
        self._set_signal_slots() # 로그인용 슬롯 등록
        self._comm_connect()

    def _make_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1") # 키움 증권 로그인 API

    def _set_signal_slots(self): # slot 등록 함수, API 종류마다 slot 함수도 다르게 만들어줘야함
        self.OnEventConnect.connect(self._login_slot) # connect시 _login_slot 슬롯 함수 호출

    def _login_slot(self, err_code): # 로그인 응답 slot 함수
        if err_code == 0:
            print("Connected!")
        else:
            print("Not Connectedd...")
        self.login_event_loop.exit()

    def _comm_connect(self):
        self.dynamicCall("CommConnect()") # QAxWidget 클래스 내 함수
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec() # 로그인 요청시까지 기다린다

app = QApplication(sys.argv)
Kiwoom = Kiwoom()
app.exec()