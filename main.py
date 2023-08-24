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
        self.account_number = self.get_account_number() # 계좌번호 가져오기
        self.tr_event_loop = QEventLoop()


    # 키움 증권 로그인 API
    def _make_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1") 

    # slot 등록 함수, API 종류마다 slot 함수도 다르게 만들어줘야함
    def _set_signal_slots(self): 
        self.OnEventConnect.connect(self._login_slot) # connect시 _login_slot 슬롯 함수 호출
        self.OnReceiveTrData.connect(self._on_receive_tr_data) # TR 조회 슬롯 함수 호출

    # 로그인 응답 slot 함수
    def _login_slot(self, err_code): 
        if err_code == 0:
            print("Connected!")
        else:
            print("Not Connectedd...")
        self.login_event_loop.exit()

    # 모든 TR 거래에 대해 응답을 수신하는 slot 함수
    # 화면번호, TR 구분명, TR 이름, 레코드 이름(빈칸 가능), 
    # OnreceiveTrData 함수 결과: 2: 데이터 더 있음, 0: 없음
    # 연속 조회할 값의 유무,
    # 종목 코드, 기준 일자: 입력 안하면 최근일자, 수정 주가 구분: 1로 사용할 예정, TR 묶음 지정 네자리 숫자
    def _on_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, v1, v2, v3, v4):
        print(screen_no, rqname, trcode, record_name, next)
        cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)

        if next == "2":
            self.isNext = True
        else:
            self.isNext = False

        if rqname == "opt10081": # 주식 가격 정보 가져오기
            print()
            total = []
            for i in range(cnt):
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "일자").strip()
                open = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "시가").strip())
                high = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "고가").strip())
                low = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "저가").strip())
                close = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "현재가").strip())
                volume = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "거래량").strip())
                total.append([date, open, high, low, close, volume])
            self.tr_data = total

        self.tr_event_loop.exit() # 슬롯 응답 대기 종료
        time.sleep(1)



    def _comm_connect(self):
        self.dynamicCall("CommConnect()") # QAxWidget 클래스 내 함수
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec() # 로그인 요청시까지 기다린다

    # 계좌 정보 가져오기
    def get_account_number(self): 
        account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCLIST")
        account_number = account_list.split(';')[0]
        print("나의 계좌 번호:", account_number)
        return account_number
    
    # 종목 코드 가져오기: market_type: 0: 코스피, 10: 코스닥
    def get_code_list_stok_market(self, market_type):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_type)
        code_list = code_list.split(';')[:-1]
        return code_list
    
    # 종목코드로 종목명 가져오기 
    def get_code_name(self, code):
        name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return name
    
    # 가격 정보 가져오기
    def get_price(self, code):
        self.dynamicCall("SetInputValue(QString, QString)", "종목 코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "기준 일자", "20230823")
        self.dynamicCall("SetInputValue(QString, QString)", "수정 주가 구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10081", "opt10081", 0, "0020")
        self.tr_event_loop.exec_()
        time.sleep(1)

        total = self.tr_data

        while self.isNext:
            self.dynamicCall("SetInputValue(QString, QString)", "종목 코드", code)
            self.dynamicCall("SetInputValue(QString, QString)", "기준 일자", "20230823")
            self.dynamicCall("SetInputValue(QString, QString)", "수정 주가 구분", "1")
            self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10081", "opt10081", 2, "0020")
            self.tr_event_loop.exec_()
            total += self.tr_data
            time.sleep(1)       

        df = pd.DataFrame(total, columns = ['date', 'open', 'high', 'low', 'close', 'volume']).set_index("date")
        df = df.drop_duplicates()
        df = df.sort_index()
        return df

if __name__ == '__main__': # 중복 방지를 위해 사용
    app = QApplication(sys.argv)
    Kiwoom = Kiwoom()

    # 종목 정보 가져오기 예제
    kospi_list = Kiwoom.get_code_list_stok_market("0")
    # kodak_list = Kiwoom.get_code_list_stok_market("10")
    # print("코스피", kospi_list)
    # print("코스닥", kospi_list)

    # 종목명 가져오기 예제
    for kospi in kospi_list:
        name = Kiwoom.get_code_name(kospi)
        if name == "삼성전자":
            print(kospi)

    # 삼성전자 주식 가격 가져오기
    samsung = Kiwoom.get_price("005930")
    print(samsung)

    app.exec()
