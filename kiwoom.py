from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from datetime import datetime, timedelta

import time
import math
import sys
import pandas as pd
import logging

import fid_codes
import trade_algorithm
from teleBot import TeleBot

class Kiwoom(QAxWidget):
    def __init__(self, logger): # QAxWidget 상속 받은 경우 오버라이딩 필요
        super().__init__()

        self.logger = logger
        
        # 로그인 프로세스를 따로 띄웠으나, 계좌 비밀번호가 저장이 안돼 사용 X
        # 키움 증권 로그인 창이 뜨면, 비밀번호 입력 및 로그인할 프로세스
        # login_process = multiprocessing.Process(target = Login, name = "login process", args = "")
        # login_process.start()

        # 키움 증권 로그인 창 띄우기
        self._make_kiwoom_instance()
        self._set_signal_slots() # 로그인용 슬롯 등록
        self._comm_connect()
        self.account_number = self.get_account_number() # 계좌번호 가져오기
        self.universe_realtime_transaction_info = [] # 실시간 체결정보 가져올 종목코드 리스트 -> 사용법에 대해서 고민 해봐야 함
        self.stock_dict = {}
        self.pl = 0
        self.tr_event_loop = QEventLoop()
        self.deposit = 0
        self.get_deposit() # 예수금 가져오기
        self.order_list = self.get_order() # 체결리스트 가져오기 
        # 텔레그램 봇
        self.teleBot = TeleBot()

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
                # print(date)

                if date < '19000101' or date == datetime.now().strftime("%Y%m%d"):
                    self.isNext = False
                    
                    continue
                
                open = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "시가").strip())
                high = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "고가").strip())
                low = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "저가").strip())
                close = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "현재가").strip())
                volume = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "거래량").strip()
                if volume.isdigit():
                    volume = int(volume)
                else:
                    volume = 0


                stock = {'open': open, 'high': high, 'low': low, 'close': close, 'volume': volume }
                stock["_id"] = {"code": code, "date": date}
                total.append(stock)
            self.tr_data = total
        
        elif rqname == "opw00001_req": # 예수금 가져오기
            deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, 0, "주문가능금액")
            self.deposit = int(deposit)

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

        elif rqname == "opt20006_req": # 시장(코스피, 코스닥) 일봉 정보 일괄로 가져오기
            total = []
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, 0, "업종코드").strip()
            if code == "001": # KOSPI
                code = 'KOSPI'
            elif code == "101": # KOSDAQ
                code = 'KOSDAQ'

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

        elif rqname == "opw00018_req": # 잔고 가져오기
            total = []
            for i in range(cnt):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "종목번호").strip()[1:] 
                buy_close = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "매입가").strip())
                available_quantity = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "매매가능수량").strip())
                ror = float(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "수익률(%)").strip())
                close = int(self.dynamicCall("GetCommData(QString, QString, int, QString)", trcode, rqname, i, "현재가").strip())


                stock = {}
                stock['code'] = code
                stock['buy_close'] = buy_close
                stock['available_quantity'] = available_quantity
                stock['ror'] =  ror
                stock['close'] = close
                total.append(stock)
            self.tr_data = total

        self.tr_event_loop.exit() # 슬롯 응답 대기 종료
        time.sleep(1)

    # 주문 TR 조회 응답 및 주문에 대한 메세지
    def _on_receive_msg(self, screen_no, rqname, trcode, msg):
        print(screen_no, rqname, trcode, msg)
        if trcode == "RC4007":
            pass

    # 주문 접수 및 체결에 대한 응답
    # gubun: 주문 접수 및 체결까지 GetChejanData 3번 수신(접수: 0, 체결: 0, 잔고 이동: 1)
    # cnt: 주문 접수 및 체결 시 얻는 항목의 개수
    # fid_list FID의 경우 키움API에서 미리 정의된 코드 값
    def _on_receive_chejan(self, gubun, cnt, fid_list):
        try:
            if gubun == "1": # 잔고
                # 주문가능수량 갱신
                code = self.dynamicCall("GetChejanData(int)", "9001")[1:] 
                available_quantity = int(self.dynamicCall("GetChejanData(int)", fid_codes.get_fid("주문가능수량")))
                buy_close = int(self.dynamicCall("GetChejanData(int)", "931").lstrip("+").lstrip("-")) # 매입단가
                self.stock_dict[code]['available_quantity'] = available_quantity
                self.stock_dict[code]['buy_close'] = buy_close

                # 당일 손익 리포트
                pl = int(self.dynamicCall("GetChejanData(int)", fid_codes.get_fid("당일 총 매도 손익")))
                pl_rate = round(float(self.dynamicCall("GetChejanData(int)", fid_codes.get_fid("손익율"))), 2)

                # 접수/체결 시 잔고 조회하므로 손익이 변경 되었을 시(체결 시)만 리포팅
                if self.pl != pl:
                    self.pl = pl
                    self.teleBot.report_message("당일 총 매도 손익: {}, 손익율: {}".format(pl, pl_rate))

            elif gubun == "0": # 주문/체결
                code = self.dynamicCall("GetChejanData(int)", "9001")[1:] 
                name = self.dynamicCall("GetChejanData(int)", "302").strip() # 종목명
                division = self.dynamicCall("GetChejanData(int)", "907") # 매도수 구분, 1:매도, 2:매수
                che = self.dynamicCall("GetChejanData(int)", "911").lstrip("+").lstrip("-") # 체결량
                price = self.dynamicCall("GetChejanData(int)", "910").lstrip("+").lstrip("-") # 체결가
                buy_close = self.dynamicCall("GetChejanData(int)", "910").lstrip("+").lstrip("-") # 매입단가
                order = self.dynamicCall("GetChejanData(int)", fid_codes.get_fid("주문수량"))
                un_che = self.dynamicCall("GetChejanData(int)", fid_codes.get_fid("미체결수량"))


                if che.isdigit() and price.isdigit() and buy_close.isdigit() and order.isdigit():
                    che = int(che)
                    price = int(price)
                    buy_close = int(buy_close)
                    order = int(order)
                    un_che = int(un_che)
                else:
                    che = 0
                    price = 0
                    buy_close = 0.0
                    order = 0
                    un_che = 0

                if che > 0 and division == '2': # 매수 체결 시
                    self.stock_dict[code]['ror'] = 0.0 # 주문 체결 시 0으로 초기화 하여야 당일 매수/매도 가능함
                    self.teleBot.report_message("{} 매수 - {}(체결수량)/{}(주문수량), 미체결수량: {}, 매수가: {}".format(name, che, order, un_che, buy_close))

                if che > 0 and division == '1': # 매도 체결 시
                    self.deposit = self.deposit + (che * price)

                    self.teleBot.report_message("{} 매도 - {}(체결수량)/{}(주문수량), 미체결수량: {}".format(name, che, order, un_che))
        except Exception as e:
            print(e)

        '''
        for fid in fid_list.split(";"):
            # FID 9001 = 종목 코드, 결과의 경우 문자+종목코드 이므로 문자 제외하고 슬라이싱
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
        '''

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
            vp = float(self.dynamicCall("GetCommRealData(QString, int)", s_code, fid_codes.get_fid("체결강도")))

            try:
                self.logger.debug("{} {} {} {} {}".format(signed_at, s_code, self.stock_dict[s_code]['name'], fluctuation_rate, vp))
            except KeyError as e:
                self.logger.error(e)

            self.universe_realtime_transaction_info.append([s_code, signed_at, fluctuation_rate, close, high, open, low, accum_volume])
            try:
                self.stock_dict[s_code]['fluctuation_rate'] = fluctuation_rate
                self.stock_dict[s_code]['close'] = close
            except Exception as e:
                self.logger.error(e)

            # 매수
            try:
                # 당일 상승중이며, 주문한 적 없고, 매도가능수량 없는 경우에만 매수
                if fluctuation_rate > 0 and self.stock_dict[s_code]['buy_quantity'] == 0 and self.stock_dict[s_code]['available_quantity'] == 0: 
                    buy_quantity = 0

                    # (미)체결 리스트 체크, 프로그램 재시작 시 이미 매수 주문 넣었던 건이면 매수 안함
                    for order in self.order_list:
                        if s_code == order[0] and order[7] == '매수' and int(order[9]) > 0: # 매수 체결량 0 보다 큰 경우 매수 안함
                            # self.logger.debug("(당일 매수 체결 종목){} {}".format(s_code, self.stock_dict[s_code]['name']))
                            # print("(당일 매수 체결 종목){} {}".format(s_code, self.stock_dict[s_code]['name']))
                            buy_quantity = -2 
                            break

                     # 매수 체결 건이 아닌 경우 매수 알고리즘
                    if buy_quantity != -2:
                        buy_quantity = trade_algorithm.get_buy_quantity(self.deposit, 100000, close, self.stock_dict[s_code], vp, self.logger) # 10만원어치 구매
                        
                        if buy_quantity != -1: # -1의 경우 예수금 부족 혹은 매수 가치 없음
                            self.stock_dict[s_code]['buy_quantity'] = buy_quantity # buy_quantity가 있는 경우 프로그램 실행 후 매수 주문 건
                            self.deposit = self.deposit - (close * buy_quantity)

                            self.buy_stock(s_code, close, buy_quantity) 
            except KeyError:
                pass
                # print("{} 매수 종목 아님".format(s_code))

            # 잔고 매도
            try:
                sell_quantity_rate, ror = trade_algorithm.get_sell_quantity_and_ror(close, self.stock_dict[s_code], self.logger)

                if sell_quantity_rate == 0.0 and ror == 0.0:
                    pass # 매입가 없으므로 매도 안함
                elif self.stock_dict[s_code]['available_quantity'] > 0: # 주문가능수량 있어야 함
                    sell_quantity = math.trunc(self.stock_dict[s_code]['available_quantity'] * sell_quantity_rate)
                    if sell_quantity > 0:
                        self.sell_stock(s_code, '', sell_quantity)
                        
                    elif sell_quantity_rate == 1.0: # 전량 매도 타이밍인 경우 매도 주문
                        self.sell_stock(s_code, '', self.stock_dict[s_code]['available_quantity'])
                    else:
                        self.logger.info("(매도 가능 수량 없음)코드: {}, ROR, 매도가능수량: {}, 현 수량: {}".format(s_code, self.stock_dict[s_code]['condition'], sell_quantity, self.stock_dict[s_code]['available_quantity']))
                        print("(매도 가능 수량 없음)코드: {}, ROR, 매도가능수량: {}, 현 수량: {}".format(s_code, self.stock_dict[s_code]['condition'], sell_quantity, self.stock_dict[s_code]['available_quantity']))
                    
            except KeyError as e:
                pass
                # print(e)


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
        time.sleep(3)
        return code_list
    
    # 종목코드로 종목명 가져오기 
    def get_code_name(self, code):
        name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return name
    
    # 가격 정보 가져오기
    def get_price(self, code):
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "기준일자", "20010101")
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10081_req", "opt10081", 0, "0020")
        self.tr_event_loop.exec_()
        time.sleep(4)

        total = self.tr_data

        while self.isNext:
            self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", "20010101")
            self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
            self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10081_req", "opt10081", 2, "0020")
            self.tr_event_loop.exec_()
            total += self.tr_data
            time.sleep(4)

        return total
    
    # 일별 주가 요청
    def get_day_price(self, code, req_date, ml_time):
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "조회일자", req_date)
        self.dynamicCall("SetInputValue(QString, QString)", "표시구분", "0")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10086_req", "opt10086", 0, "0006")
        self.tr_event_loop.exec_()
        # 어차피 내일 종가 예측할 것이기 때문에, 1초만 딜레이

        sleep_time = 0
        if ml_time is None:
            sleep_time = 4
        else:
            sleep_time = 4 - ml_time
        if sleep_time > 0:
            time.sleep(sleep_time)

        total = self.tr_data

        total["_id"] = {"code": code, "date": req_date}

        return total
    
    # 업종(코스피 가져오려고) 가격 정보 가져오기
    def get_market_price(self, code, dateStr):
        # 업종코드 = 001:종합(KOSPI), 002:대형주, 003:중형주, 004:소형주 101:종합(KOSDAQ), 201:KOSPI200, 302:KOSTAR, 701: KRX100 나머지 ※ 업종코드 참고
        self.dynamicCall("SetInputValue(QString, QString)", "업종코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "기준일자", dateStr)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt20006_req", "opt20006", 0, "0030")
        self.tr_event_loop.exec_()
        time.sleep(4)

        total = self.tr_data

        for stock in total:
            if stock['_id']['date'] == dateStr:
                self.isNext = False

        while self.isNext:
            self.dynamicCall("SetInputValue(QString, QString)", "업종코드", code)
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", dateStr)
            self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt20006_req", "opt20006", 2, "0030")
            self.tr_event_loop.exec_()
            total += self.tr_data

            for stock in total:
                if stock['_id']['date'] == dateStr:
                    self.isNext = False
            time.sleep(4)

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

        try:
            self.logger.info("(매수 주문)코드: {}, 등락률(예측 상승률): {}({}), 구매수량: {}".format(code, self.stock_dict[code]['fluctuation_rate'], self.stock_dict[code]['pred_fluctuation_rate'], quantity))
            print("(매수 주문)코드: {}, 등락률(예측 상승률): {}({}), 구매수량: {}".format(code, self.stock_dict[code]['fluctuation_rate'], self.stock_dict[code]['pred_fluctuation_rate'], quantity))
        except KeyError as e:
            self.logger.error("(매수 주문) 오류 {}".format(e))
            print(e)

        time.sleep(1) # 초당 5번 주문 가능

    def sell_stock(self, code, price, quantity):
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
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["매도", "0153", stock_account, 2, code, quantity, price, division, ""])

        try:
            self.logger.info("(매도 주문)코드: {}, ROR, 판매수량: {}".format(code, self.stock_dict[code]['condition'], math.trunc(quantity)))
            print("(매도 주문)코드: {}, ROR, 판매수량: {}".format(code, self.stock_dict[code]['condition'], math.trunc(quantity)))
        except KeyError as e:
            self.logger.error("(매도 주문) 오류 {}".format(e.args))
            print(e)

        # print("{} 매도".format(code))
        time.sleep(1) # 초당 5번 주문 가능

    # 예수금 가져오기
    def get_deposit(self):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00001_req", "opw00001", 0, "0502")

        self.tr_event_loop.exec()

    # 미체결 요청(실제로 당일 접수 전부 가져옴)
    def get_order(self):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)", "전체종목구분", "0")
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "0") # 0: 전체, 1: 미체결, 2: 체결
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0") # 0: 전체, 1: 매도, 2: 매수
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10075_req", "opt10075", 0, "0902")

        self.tr_event_loop.exec()
        return self.tr_data
    
    # 잔고 요청
    def get_balance(self):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00018_req", "opw00018", 0, "0903")

        self.tr_event_loop.exec_()
        time.sleep(5)

        total = self.tr_data

        while self.isNext:
            self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
            self.dynamicCall("SetInputValue(QString, QString)", "비밀번호매체구분", "00")
            self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
            self.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00018_req", "opw00018", 2, "0903")
            self.tr_event_loop.exec_()
            total += self.tr_data
            time.sleep(5)

        return total

    # 실시간 체결 정보 등록, 주식 시세는 체결과 관계 없이 시세가 변할 때이므로 체결 정보로 현재가 가져와야 함
    # list의 경우 ; 구분자
    # opt_type의 경우 같은 화면에서 최초 등록의 경우 0, 그 이후 1 -> 처음부터 1로 해도 동작 함
    def set_real_reg(self, str_screen_no, str_code_list, str_fid_list, str_opt_type, stock_dict):        
        # print(str_code_list)

        # 주식 딕셔너리 초기화
        if len(self.stock_dict) == 0:
            self.stock_dict = stock_dict
        else:
            for key in stock_dict.keys():
                self.stock_dict[key] = stock_dict[key]

        self.dynamicCall("SetRealReg(QString, QString, QString, QString)", str_screen_no, str_code_list, str_fid_list, str_opt_type)
        
        time.sleep(1)

