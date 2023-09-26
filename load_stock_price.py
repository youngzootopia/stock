from PyQt5.QtWidgets import *
from datetime import datetime
from multipledispatch import dispatch
import sys
import json
import pandas
import exchange_calendars as xcals
from kiwoom import Kiwoom
from mongo import Mongo

@dispatch(str)
def daily_load(start_date):
    daily_load(start_date, start_date)

@dispatch(str, str)
def daily_load(start_date, end_date):
    # 종목 정보 가져오기
    kospi_list = Kiwoom.get_code_list_stok_market("0")
    # kodak_list = Kiwoom.get_code_list_stok_market("10")

    # 특정 종목부터 받아올 경우 isNext 사용
    # 일별 적재
    stock_list = []
    date_list = pandas.date_range(start = start_date, end = end_date, freq = 'D')
    date_list = pandas.date_range(start = '20230922', end = '20230922', freq = 'D')
    # isNext = True
    for kospi in kospi_list:
        # 특정 종목부터 적재할 때
        # if kospi == "465680":
        #     isNext = False

        # if isNext:
        #     continue

        # 특정 종목까지만 적재할 때
        # if kospi == "012800":
        #     break

        print(kospi)
        for dateStr in date_list:
            stock_price = Kiwoom.get_day_price(kospi, dateStr.strftime("%Y%m%d"))
            
            # 데이터가 있어야 하고, 시가가 0원 이상만 적재
            if len(stock_price) > 0 and stock_price['open'] > 0:
                stock_list.append(stock_price)
                Mongo.insert_price_daily(stock_price)

# 2018~ 일괄 적재 완료.    
def full_load():
    # 종목 정보 가져오기
    kospi_list = Kiwoom.get_code_list_stok_market("0")
    # kodak_list = Kiwoom.get_code_list_stok_market("10")

    # isNext = True
    for kospi in kospi_list:
    #     if kospi == "530023":
    #         isNext = False

    #     if isNext:
    #         continue    
        print(kospi)
        stock_price_list = Kiwoom.get_price(kospi)

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

if __name__ == '__main__': # 중복 방지를 위해 사용
    # 키움 API 실행
    app = QApplication(sys.argv)
    Kiwoom = Kiwoom()
    Mongo = Mongo()
    app.exec_()

    # daily_load 기간으로 실행 시 주말도 적재하기 때문에, 휴장 데이터 삭제
    # delete_closed_data('20230923')

    daily_load("20230925")    
    

    
