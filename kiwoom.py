from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from datetime import datetime, timedelta

import time
import pandas as pd

class Kiwoom(QAxWidget):
    def __init__(self): # QAxWidget 상속 받은 경우 오버라이딩 필요
        super().__init__()
        # 로그인 프로세스를 따로 띄웠으나, 계좌 비밀번호가 저장이 안돼 사용 X
        # 키움 증권 로그인 창이 뜨면, 비밀번호 입력 및 로그인할 프로세스
        # login_process = multiprocessing.Process(target = Login, name = "login process", args = "")
        # login_process.start()

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

        if rqname == "opt10081_req": # 일괄 주식 가격 정보 가져오기
            total = []
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, 0, "종목코드").strip()
            
            for i in range(cnt):
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "일자").strip()

                if date < '20180101' or date == datetime.now().strftime("%Y%m%d"):
                    continue
                
                open = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "시가").strip())
                high = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "고가").strip())
                low = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "저가").strip())
                close = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "현재가").strip())
                volume = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "거래량").strip())

                stock = {'open': open, 'high': high, 'low': low, 'close': close, 'volume': volume }
                stock["_id"] = {"code": code, "date": date}
                total.append(stock)
            self.tr_data = total
        
        elif rqname == "opw00001_req": # 예수금 가져오기
            deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, 0, "주문가능금액")
            self.tr_data = int(deposit)

        elif rqname == "opt10086_req": # 일별 주식 가격 정보 가져오기
            try: # 주식 가격이 없는 경우 ''
                open = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, 0, "시가"))
                open = open if open >= 0 else open * -1
                high = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, 0, "고가"))
                high = high if high >= 0 else high * -1
                low = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, 0, "저가"))
                low = low if low >= 0 else low * -1
                close = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, 0, "종가"))
                close = close if close >= 0 else close * -1
                volume = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, 0, "거래량"))
                total = {'open': open, 'high': high, 'low': low, 'close': close, 'volume': volume }
            except ValueError:
                total = {'open': 0, 'high': 0, 'low': 0, 'close': 0, 'volume': 0 }
                print("no price infomation")
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
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        # self.dynamicCall("SetInputValue(QString, QString)", "기준일자", "20230823")
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10081_req", "opt10081", 0, "0020")
        self.tr_event_loop.exec_()
        time.sleep(5)

        total = self.tr_data

        while self.isNext:
            self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            # self.dynamicCall("SetInputValue(QString, QString)", "기준일자", "20230823")
            self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
            self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10081_req", "opt10081", 2, "0020")
            self.tr_event_loop.exec_()
            total += self.tr_data
            time.sleep(5)

        return total
    
    # 예수금 가져오기
    def get_deposit(self):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00001_req", "opw00001", 0, "0004")
        self.tr_event_loop.exec()
        return self.tr_data
    
    # 일별 주가 요청
    def get_day_price(self, code, req_date):
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "조회일자", req_date)
        self.dynamicCall("SetInputValue(QString, QString)", "표시구분", "0")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10086_req", "opt10086", 0, "0006")
        self.tr_event_loop.exec_()
        # 어차피 내일 종가 예측할 것이기 때문에, 5초 딜레이 삭제
        time.sleep(2)

        total = self.tr_data

        total["_id"] = {"code": code, "date": req_date}

        return total