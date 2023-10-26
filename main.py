from datetime import datetime
import exchange_calendars as xcals
from trade_stock import Trade_stock


if __name__ == '__main__': # 중복 방지를 위해 사용
    Trade_stock = Trade_stock()

    dateStr = datetime.today().strftime("%Y%m%d")
    XKRX = xcals.get_calendar("XKRX")
    openDate = XKRX.session_open(dateStr).strftime("%Y%m%d")

    Trade_stock.register_real_stock_price(openDate, 30)
