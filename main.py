from PyQt5.QtWidgets import *
import sys
from datetime import datetime
import logging
import exchange_calendars as xcals
from trade_stock import Trade_stock
from kiwoom import Kiwoom


if __name__ == '__main__': # 중복 방지를 위해 사용
    app = QApplication(sys.argv)
    # 로깅
    log_path = './log/' + datetime.today().strftime("%Y%m%d") + '.log'
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(message)s]")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    kiwoom = Kiwoom(logger)
    trade_stock = Trade_stock(kiwoom)

    dateStr = datetime.today().strftime("%Y%m%d")
    XKRX = xcals.get_calendar("XKRX")
    openDate = XKRX.session_open(dateStr).strftime("%Y%m%d")

    trade_stock.register_real_stock_price(openDate, 30)

    app.exec_()

