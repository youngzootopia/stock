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

    for kospi in kospi_list:
        print(kospi)
        stock_price = Kiwoom.get_price(kospi)

        # 이상한 종목을 가져오는 경우가 있음. 이런 경우 size 필터링해서 DB에 안넣기
        if stock_price.size > 0:
            # 2010년 이전 데이터 삭제
            stock_price = stock_price.drop(stock_price.index[stock_price['date'] < "20100101"].tolist(), axis = 0)
            stock_price.insert(0, "code", kospi)
            Mongo.insert_price_many(stock_price)

    app.exec_()
