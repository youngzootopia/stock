from PyQt5.QtWidgets import *
import sys
from win32 import Login
from kiwoom import Kiwoom
import multiprocessing

if __name__ == '__main__': # 중복 방지를 위해 사용
    app = QApplication(sys.argv)
    Kiwoom = Kiwoom()

    # 종목 정보 가져오기 예제
    kospi_list = Kiwoom.get_code_list_stok_market("0")
    # kodak_list = Kiwoom.get_code_list_stok_market("10")
    # print("코스피", kospi_list)
    # print("코스닥", kospi_list)

    # 종목명 가져오기 예제
    # for kospi in kospi_list:
    #     name = Kiwoom.get_code_name(kospi)
    #     if name == "삼성전자":
    #         print(kospi)

    # 삼성전자 주식 가격 가져오기
    # samsung = Kiwoom.get_price("005930")
    # print(samsung)

    print(Kiwoom.get_deposit())

    app.exec_()
