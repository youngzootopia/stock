from PyQt5.QtWidgets import *
import sys
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
    # for kospi in kospi_list:
    #     print(kospi)
    #     stock_price = Kiwoom.get_day_price(kospi, '20230830')
    #     if stock_price.size > 0:
    #         stock_price.insert(0, "code", kospi)
    #         Mongo.insert_price_one(stock_price)

    # stock_price = Kiwoom.get_day_price('005930', '20230830')
    # print(stock_price)
    # Mongo.insert_price_many(stock_price)


    # 2010~20230901 일괄 적재
    # 특정 종목부터 받아올 경우 isNext 사용
    isNext = True
    for kospi in kospi_list:
        if kospi == "000020":
            isNext = False

        if isNext:
            continue    
        print(kospi)
        stock_price = Kiwoom.get_price(kospi)

        # 이상한 종목을 가져오는 경우가 있음. 이런 경우 size 필터링해서 DB에 안넣기
        if stock_price.size > 0:
            Mongo.insert_price_many(stock_price)

    app.exec_()
