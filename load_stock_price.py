from PyQt5.QtWidgets import *
import sys
import json
import pandas
from kiwoom import Kiwoom
from mongo import Mongo

def daily_load(self, start_date):
    daily_load(start_date, start_date)

def daily_load(self, start_date, end_date):
    # 종목 정보 가져오기
    kospi_list = Kiwoom.get_code_list_stok_market("0")
    # kodak_list = Kiwoom.get_code_list_stok_market("10")

    # 특정 종목부터 받아올 경우 isNext 사용
    # 일별 적재
    stock_list = []
    date_list = pandas.date_range(start = start_date, end = end_date, freq = 'D')
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
def full_load(self):
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
def save_json(self, stock_list, file_name):
    if file_name == "":
        file_name = "daily_stock_list.json"

    with open(file_name, "w") as json_file:
        json.dump(stock_list, json_file, indent=4)

if __name__ == '__main__': # 중복 방지를 위해 사용
    app = QApplication(sys.argv)
    Kiwoom = Kiwoom()
    Mongo = Mongo()

    app.exec_()

