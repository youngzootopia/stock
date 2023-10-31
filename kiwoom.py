from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from datetime import datetime, timedelta

import time
import pandas as pd

import fid_codes

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
        self.universe_realtime_transaction_info = [] # 실시간 체결정보 가져올 종목코드 리스트
        self.tr_event_loop = QEventLoop()

    # 키움 증권 로그인 API
    def _make_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1") 

    # slot 등록 함수, API 종류마다 slot 함수도 다르게 만들어줘야함
    def _set_signal_slots(self): 
        self.OnEventConnect.connect(self._login_slot) # connect시 _login_slot 슬롯 함수 호출
        self.OnReceiveTrData.connect(self._on_receive_tr_data) # TR 조회 슬롯 함수 호출
        self.OnReceiveMsg.connect(self._on_receive_msg) # TR 조회 응답 및 주문에 대한 메세지 수신
        self.OnReceiveChejanData.connect(self._on_receive_chejan) # 주문 접수 및 체결에 대한 응답
        self.OnReceiveRealData.connect(self._on_receive_real_data) # 실시간 응답

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

        elif rqname == "opt20006_req": # 코스피 일봉 정보 일괄로 가져오기
            total = []
            code = "KOSPI"
            for i in range(cnt):
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "일자").strip()

                # if date < '20180101' or date == datetime.now().strftime("%Y%m%d"):
                #     continue
                
                open = float(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "시가").strip()) / 100
                high = float(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "고가").strip()) / 100
                low = float(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "저가").strip()) / 100
                close = float(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "현재가").strip()) / 100
                volume = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "거래량").strip()) * 1000

                stock = {'open': open, 'high': high, 'low': low, 'close': close, 'volume': volume }
                stock["_id"] = {"code": code, "date": date}
                total.append(stock)
            self.tr_data = total

        elif rqname == "opt10075_req": # 미체결 요청
            box = []

            for i in range(cnt):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "종목코드").strip()
                code_name = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "종목명").strip()
                order_number = str(int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "주문번호").strip()))
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "주문상태").strip()
                order_quantity = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "주문수량").strip())
                order_price = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "주문가격").strip())
                current_price = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "현재가").strip().lstrip("+").lstrip("-"))
                order_type = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "주문구분").strip().lstrip("+").lstrip("-")
                left_quantity = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "미체결수량").strip())
                executed_quantity = (self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "체결량").strip())
                orderd_at = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "시간").strip()
                fee = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "당일매매수수료"))
                tax = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "당일매매세금"))

                box.append([code, code_name, order_number, order_status, order_quantity, order_price, current_price, order_type, left_quantity, executed_quantity, orderd_at, fee, tax])
            self.tr_data = box

        self.tr_event_loop.exit() # 슬롯 응답 대기 종료
        time.sleep(1)

    # 주문 TR 조회 응답 및 주문에 대한 메세지
    def _on_receive_msg(self, screen_no, rqname, trcode, msg):
        print(screen_no, rqname, trcode, msg)

    # 주문 접수 및 체결에 대한 응답
    # gubun: 주문 접수 및 체결까지 GetChejanData 3번 수신(접수: 0, 체결: 0, 잔고 이동: 1)
    # cnt: 주문 접수 및 체결 시 얻는 항목의 개수
    # fid_list FID의 경우 키움API에서 미리 정의된 코드 값
    def _on_receive_chejan(self, gubun, cnt, fid_list):
        print(gubun, cnt, fid_list)

        for fid in fid_list.split(";"):
            # FID 9001 = 종목 코드, 결과의 경우 문자+종목코드 이므로 문자 제외하고 슬라이싱
            code = self.dynamicCall("GetChejanData(int)", "9001")[1:] 
            data = self.dynamicCall("GetChejanData(int)", fid).lstrip("+").lstrip("-")
            # 모든 데이터는 문자열이기 때문에 가격 같이 정수형인 경우 정수 변환
            if data.isdigit():
                data = int(data)
            
            # 관리자사번, 주문업무분류(JJ:주식주문, FJ:선물옵션, JG:주식잔고, FG:선물옵션잔고), (최우선)매도호가, (최우선)매수호가, 단위체결가, 단위체결량 거부사유 화면번호
            if fid in "9205 912 27 28 914 915 919 920" :
                continue
            # FID 모름
            if fid in "921 922 923 949 10010 969 819 306 305  970 10012 10025 10011 924":
                continue 
            try:
                name = fid_codes.FID_CODES[fid]
                print("{} : {}".format(name, data))
            except KeyError:
                print("FID {} 는 정의되지 않았습니다.".format(fid))

    # 실시간 체결 정보 응답 슬롯
    def _on_receive_real_data(self, s_code, real_type, real_data):
        if real_type == "장시작시간":
            pass
        elif real_type == "주식체결":
            signed_at = self.dynamicCall("GetCommRealData(QString, int)", s_code, fid_codes.get_fid("체결시간"))
            fluctuation_rate = self.dynamicCall("GetCommRealData(QString, int)", s_code, fid_codes.get_fid("등락율"))
            fluctuation_rate = float(fluctuation_rate)
            close = self.dynamicCall("GetCommRealData(QString, int)", s_code, fid_codes.get_fid("현재가"))
            close = abs(int(close))
            high = self.dynamicCall("GetCommRealData(QString, int)", s_code, fid_codes.get_fid("고가"))
            high = abs(int(high))
            open = self.dynamicCall("GetCommRealData(QString, int)", s_code, fid_codes.get_fid("시가"))
            open = abs(int(open))
            low = self.dynamicCall("GetCommRealData(QString, int)", s_code, fid_codes.get_fid("저가"))
            low = abs(int(low))
            accum_volume = self.dynamicCall("GetCommRealData(QString, int)", s_code, fid_codes.get_fid("누적거래량"))
            accum_volume = abs(int(accum_volume))

            self.universe_realtime_transaction_info.append([s_code, signed_at, fluctuation_rate, close, high, open, low, accum_volume])
            if fluctuation_rate > 0:
                print(s_code, fluctuation_rate, signed_at, close, high, open, low, accum_volume)
                self.buy_stock(s_code, close, 1) 


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
    
    # 일별 주가 요청
    def get_day_price(self, code, req_date):
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "조회일자", req_date)
        self.dynamicCall("SetInputValue(QString, QString)", "표시구분", "0")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10086_req", "opt10086", 0, "0006")
        self.tr_event_loop.exec_()
        # 어차피 내일 종가 예측할 것이기 때문에, 5초 딜레이 삭제
        time.sleep(3)

        total = self.tr_data

        total["_id"] = {"code": code, "date": req_date}

        return total
    
    # 업종(코스피 가져오려고) 가격 정보 가져오기
    def get_kospi_price(self, code):
        self.dynamicCall("SetInputValue(QString, QString)", "업종코드", "001" if code == "" else code)
        # self.dynamicCall("SetInputValue(QString, QString)", "기준일자", "20231003")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt20006_req", "opt20006", 0, "0030")
        self.tr_event_loop.exec_()
        time.sleep(5)

        total = self.tr_data

        while self.isNext:
            self.dynamicCall("SetInputValue(QString, QString)", "업종코드", "001" if code != "" else code)
            # self.dynamicCall("SetInputValue(QString, QString)", "기준일자", "20231003")
            self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt20006_req", "opt20006", 0, "0030")
            self.tr_event_loop.exec_()
            total += self.tr_data
            time.sleep(5)

        return total
    
    def buy_stock(self, code, price, quantity):
        stock_account = self.account_number

        price = 0 if price == "" else price
        division = "03" if price == "" or price == 0 else "00" # 가격 입력 되지 않았거나, 0원 일 때
        quantity = 1 if quantity == "" else quantity

        ''' sRQName	사용자가 임의로 지정할 수 있는 이름입니다. (예: "삼성전자주문")
            sScreenNO	화면번호로 "0"을 제외한 4자리의 문자열을 사용합니다. (예: "1000")
            sAccNo	계좌번호입니다. (예: "8140977311")
            nOrderType	주문유형입니다. (1: 매수, 2: 매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도 정정)
            sCode	매매할 주식의 종목코드입니다.
            nQty	주문수량입니다.
            nPrice	주문단가입니다.
            sHogaGb	'00': 지정가, '03': 시장가
            sOrgOrderNo	원주문번호로 주문 정정시 사용합니다.
        '''
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["매수", "0150", stock_account, 1, code, quantity, price, division, ""])

        time.sleep(1) # 초당 5번 주문 가능

    # 예수금 가져오기
    def get_deposit(self):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00001_req", "opw00001", 0, "0502")

        self.tr_event_loop.exec()
        return self.tr_data

    # 미체결 요청(실제로 당일 접수 전부 가져옴)
    def get_order(self):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)", "전체종목구분", "0")
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "0") # 0: 전체, 1: 미체결, 2: 체결
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0") # 0: 전체, 1: 매도, 2: 매수
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10075_req", "opt10075", 0, "0902")

        self.tr_event_loop.exec()
        return self.tr_data

    # 실시간 체결 정보 등록, 주식 시세는 체결과 관계 없이 시세가 변할 때이므로 체결 정보로 현재가 가져와야 함
    # list의 경우 ; 구분자
    # opt_type의 경우 같은 화면에서 최초 등록의 경우 0, 그 이후 1 -> 처음부터 1로 해도 동작 함
    def set_real_reg(self, str_screen_no, str_code_list, str_fid_list, str_opt_type):
        print(str_code_list)
        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", str_screen_no, str_code_list, str_fid_list, str_opt_type)

        time.sleep(1)

