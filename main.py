from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import time
import pandas as pd

from win32 import Login
import multiprocessing

class Kiwoom(QAxWidget):
    def __init__(self): # QAxWidget 상속 받은 경우 오버라이딩 필요
        super().__init__()
        # 키움 증권 로그인 창이 뜨면, 비밀번호 입력 및 로그인할 프로세스
        login_process = multiprocessing.Process(target = Login, name = "login process", args = "")
        login_process.start()

        # 키움 증권 로그인 창 띄우기
        self._make_kiwoom_instance()
        self._set_signal_slots() # 로그인용 슬롯 등록
        self._comm_connect()
        self.get_account_number() # 계좌번호 가져오기


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

    def get_account_number(self): # 계좌 정보 가져오기
        account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCLIST")
        account_number = account_list.split(';')[0]
        print("나의 계좌 번호:", account_number)
        return account_number
    
    # 종목 코드 가져오기: market_type: 0: 코스피, 10: 코스닥
    def get_code_list_stok_market(self, market_type):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_type)
        code_list = code_list.split(';')[:-1]
        return code_list

if __name__ == '__main__': # 중복 방지를 위해 사용
    app = QApplication(sys.argv)
    Kiwoom = Kiwoom()

    kospi_list = Kiwoom.get_code_list_stok_market("0")

    print("코스피", kospi_list)

    app.exec()

    

>>>>>>> main
