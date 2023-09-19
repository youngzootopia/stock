from PyQt5.QtWidgets import *
import sys
import json
import pandas
from kiwoom import Kiwoom
from mongo import Mongo

if __name__ == '__main__': # 중복 방지를 위해 사용
    app = QApplication(sys.argv)
    Kiwoom = Kiwoom()
    Mongo = Mongo()

    # 종목 정보 가져오기
    kospi_list = Kiwoom.get_code_list_stok_market("0")
    # kodak_list = Kiwoom.get_code_list_stok_market("10")

    # 일별 적재
    stock_list = []
    date_list = pandas.date_range(start = '20230901', end = '20230919', freq = 'D')
    for kospi in kospi_list:
        print(kospi)
        for dateStr in date_list:
            stock_price = Kiwoom.get_day_price(kospi, dateStr.replace('-', ''))
            if len(stock_price) > 0:
                stock_list.append(stock_price)
                Mongo.insert_price_daily(stock_price)

    # with open("daily_stock_list.json", "w") as json_file:
    #     json.dump(stock_list, json_file, indent=4)


    # 2018~20230831 일괄 적재 완료.
    # 특정 종목부터 받아올 경우 isNext 사용
    # isNext = True
    # for kospi in kospi_list:
    # #     if kospi == "000020":
    # #         isNext = False

    # #     if isNext:
    # #         continue    
    #     print(kospi)
    #     stock_price_list = Kiwoom.get_price(kospi)

    # # 이상한 종목을 가져오는 경우가 있음. 이런 경우 size 필터링해서 DB에 안넣기
    #     if len(stock_price_list) > 0:
    #         Mongo.insert_price_many(stock_price_list)

    app.exec_()
