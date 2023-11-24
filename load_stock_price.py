from PyQt5.QtWidgets import *
from datetime import datetime
from multipledispatch import dispatch
import pandas as pd
import sys
import json
import pandas
import exchange_calendars as xcals
from kiwoom import Kiwoom
from mongo import Mongo
from ml_stock import Ml_stock
from teleBot import TeleBot

@dispatch(str, str)
def daily_load(start_date, code):
    daily_load(start_date, start_date, code)

@dispatch(str, str, str)
def daily_load(start_date, end_date, code):
    # 종목 정보 가져오기
    code_list = Kiwoom.get_code_list_stok_market("0")
    code_list.append(Kiwoom.get_code_list_stok_market("10"))
    # kospi_list = []
    code_list.append("KOSPI")
    code_list.append("KOSDAQ")

    # 특정 종목부터 받아올 경우 isNext 사용
    # 일별 적재
    stock_list = []
    date_list = pandas.date_range(start = start_date, end = end_date, freq = 'D')
    isNext = True if code != "" else False
    for stock_code in code_list:
        # 특정 종목부터 적재할 때
        if stock_code == code:
            isNext = False

        if isNext:
            continue

        # 특정 종목까지만 적재할 때
        # if kospi == "466940":
        #     break

        print(stock_code)
        for dateStr in date_list:
            dateStr = dateStr.strftime("%Y%m%d")
            if stock_code == "KOSPI" or stock_code == 'KOSDAQ': 
                # 업종코드 = 001:종합(KOSPI), 002:대형주, 003:중형주, 004:소형주 101:종합(KOSDAQ), 201:KOSPI200, 302:KOSTAR, 701: KRX100 나머지 ※ 업종코드 참고
                market_code = '001'
                if stock_code == "KOSPI":
                    market_code = "001"
                elif stock_code == "KOSDAQ":
                    market_code = "101"

                market_price_list = stock_market_full_load(market_code)
                for market_price in market_price_list:
                    if market_price['_id']['date'] == dateStr:
                        stock_price = market_price
            else:
                stock_price = Kiwoom.get_day_price(stock_code, dateStr)

                # 신규 상장 주식의 경우 코드네임 저장
                if Mongo.get_stock_name(stock_code) == "":
                    stock = {}
                    stock['_id'] = {}
                    stock['_id']['code'] = stock_code
                    stock['name'] = Kiwoom.get_code_name(stock_code)

                    Mongo.insert_code_name(stock)
            
            # 데이터가 있어야 하고, 시가가 0원 이상만 적재
            if len(stock_price) > 0 and stock_price['open'] > 0:
                stock_list.append(stock_price)
                Mongo.update_predict_price(stock_price) # 전날 예측한 종가 검증을 위해 실제 종가 및 등락률 업데이트
                Mongo.insert_price_daily(stock_price)

                # 데이터 예측
                XKRX = xcals.get_calendar("XKRX")
                next_open = XKRX.next_open(dateStr)

                Ml_stock.predict_stock_close_price(stock_code, next_open.strftime("%Y%m%d"))
                

# 2018~ 일괄 적재 완료.    
def full_load():
    # 종목 정보 가져오기
    code_list = Kiwoom.get_code_list_stok_market("0")
    code_list.append(Kiwoom.get_code_list_stok_market("10"))

    isNext = True
    for code in code_list:
        if code == "000100":
            isNext = False

        if isNext:
            continue    
        print(code)
        stock_price_list = Kiwoom.get_price(code)

    # 이상한 종목을 가져오는 경우가 있음. 이런 경우 size 필터링해서 DB에 안넣기
        if len(stock_price_list) > 0:
            Mongo.insert_price_many(stock_price_list)

# json 파일 생성, DB에 잘 넣고 있어 딱히 필요 없을 듯
def save_json(stock_list, file_name):
    if file_name == "":
        file_name = "daily_stock_list.json"

    with open(file_name, "w") as json_file:
        json.dump(stock_list, json_file, indent=4)

@dispatch()
def delete_closed_data():
    delete_closed_data(Mongo.get_min_date())

# daily_load 기간으로 실행 시 주말도 적재하기 때문에, 휴장 데이터 삭제
# delete_closed_data('20230923')
@dispatch(str)
def delete_closed_data(start_date):
    end_date = datetime.now().strftime("%Y%m%d")

    # 기간 동안의 전체 날짜
    date_list = pandas.date_range(start = start_date, end = end_date, freq = 'D')
    # 기간 동안의 개장일
    open_date_list = xcals.get_calendar("XKRX", start = start_date, end = end_date).schedule.index

    # 기간 동안의 휴장일
    close_date_list = date_list.drop(labels = open_date_list)

    for close_date in close_date_list:
        print(close_date)
        query = {"_id.date": close_date.strftime("%Y%m%d")}
        Mongo.delete_Many(query)
    
def load_stock_code_and_name():
    # 종목 정보 가져오기
    kospi_list = Kiwoom.get_code_list_stok_market("0")
    kosdak_list = Kiwoom.get_code_list_stok_market("10")
    
    total = []
    for code in kospi_list:
        name = Kiwoom.get_code_name(code)

        print("{0}: {1}".format(code, name))
        code_and_name = {'name': name}
        code_and_name["_id"] = {"code": code}
        total.append(code_and_name)

    for code in kosdak_list:
        name = Kiwoom.get_code_name(code)

        print("{0}: {1}".format(code, name))
        code_and_name = {'name': name}
        code_and_name["_id"] = {"code": code}
        total.append(code_and_name)

    Mongo.insert_code_name_many(total)


def stock_market_full_load(code):

    stock_price_list = Kiwoom.get_kospi_price(code)

    # 이상한 종목을 가져오는 경우가 있음. 이런 경우 size 필터링해서 DB에 안넣기
    if len(stock_price_list) > 0:
        Mongo.insert_price_many(stock_price_list)

    return stock_price_list

def report_close_pred(dateStr):
    pred_kospi = Mongo.get_kospi_pred_close(dateStr)
    TeleBot.report_message("{0} KOSPI 예측 보고서: {1}".format(dateStr, pred_kospi['pred_fluctuation_rate']))

    for pred in Mongo.get_pred_close(dateStr, 30):
        TeleBot.report_message("종목명: {0}\n예측 상승률: {1}\n예측 종가: {2}".format(Mongo.get_stock_name(pred['_id']['code']), pred['pred_fluctuation_rate'], round(pred['pred_close'])))

if __name__ == '__main__': # 중복 방지를 위해 사용
    # 키움 API 실행
    app = QApplication(sys.argv)
    Kiwoom = Kiwoom()
    Mongo = Mongo()
    Ml_stock = Ml_stock()
    TeleBot = TeleBot()

    # 1. 종목 코드(코스피, 코스닥) 네임 저장하기
    # load_stock_code_and_name()

    # 2. 일괄 적재 kiwoom.py 에서 '20180101' 이후 데이터만 적재 하도록 작성
    full_load()

    # 2. 일 적재
    # dateStr = datetime.today().strftime("%Y%m%d")
    # dateStr = '20231123' # 특정날짜 적재 시 수정
    # code = '399580' # 특정 코드부터 적재 할 시 수정

    # daily_load(dateStr, code)       
    
    # XKRX = xcals.get_calendar("XKRX")
    # next_open = XKRX.next_open(dateStr).strftime("%Y%m%d")
    # report_close_pred(next_open)

    app.exec_()