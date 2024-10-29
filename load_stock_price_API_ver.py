import pandas
import time
from pykrx import stock
from mysql import MySql
from datetime import datetime

def daily_load(start_date):
    # 적재 Start
    # KOSPI
    kospi = stock.get_market_ohlcv(start_date, market="KOSPI")
    # 거래대금 사용 X
    kospi = kospi.drop(columns=['거래대금'])
    # pykrx의 경우 한글로 되어 있어 컬럼명, 인덱스명 변경
    kospi.columns = ['open', 'high', 'low', 'close', 'quantity', 'per_change']
    kospi = kospi.reset_index()
    kospi = kospi.rename(columns = {'티커':'ticker'})
    # pykrx의 해당 메소드에는 날짜는 포함되어 있지 않아서 날짜 컬럼 추가
    kospi['date'] = start_date

    # API 부하를 막기 위해 1초 sleep
    time.sleep(1)

    # KOSDAQ
    kosdaq = stock.get_market_ohlcv(start_date, market="KOSDAQ")
    # 거래대금 사용 X
    kosdaq = kosdaq.drop(columns=['거래대금'])
    # pykrx의 경우 한글로 되어 있어 컬럼명, 인덱스명 변경
    kosdaq.columns = ['open', 'high', 'low', 'close', 'quantity', 'per_change']
    kosdaq = kosdaq.reset_index()
    kosdaq = kosdaq.rename(columns = {'티커':'ticker'})
    # pykrx의 해당 메소드에는 날짜는 포함되어 있지 않아서 날짜 컬럼 추가
    kosdaq['date'] = start_date

    df = pandas.concat([kospi, kosdaq], ignore_index = True)

    mysql = MySql()
    mysql.insert_daily(df)


def periodical_load(start_date, end_date, start_ticker):
    mysql = MySql()

    # KOSPI + KOSDAQ
    ticker_list = stock.get_market_ticker_list(date = end_date, market='KOSPI')
    ticker_list += stock.get_market_ticker_list(date = end_date, market='KOSDAQ')
    ticker_list_length = len(ticker_list)
    ticker_count = 0

    flag = False if start_ticker == '' else True

    for ticker in ticker_list:
        if flag:
            ticker_count += 1
            flag = False if start_ticker == ticker else True
            continue

        price = stock.get_market_ohlcv(start_date, end_date, ticker)

        # NaN 있을 수 있어서 이 경우 0
        price.fillna(0, inplace=True)
        
        # pykrx의 경우 한글로 되어 있어 컬럼명, 인덱스명 변경
        price.columns = ['open', 'high', 'low', 'close', 'quantity', 'per_change']
        price = price.reset_index()
        price = price.rename(columns = {'날짜':'date'})
        price['date'] = pandas.to_datetime(price['date'], format='%Y-%m-%d').dt.strftime('%Y%m%d')

        # pykrx의 해당 메소드에는 날짜는 포함되어 있지 않아서 날짜 컬럼 추가
        price['ticker'] = ticker

        # print(price)
        time.sleep(5)
        mysql.insert_daily(price)

        ticker_count += 1
        print("{}: {} / {} = {}".format(ticker, ticker_count, ticker_list_length, ticker_count / ticker_list_length * 100))


## 실행
# 당일 적재
daily_load(datetime.today().strftime('%Y%m%d'))

# 기간 적재
# periodical_load('20240705', '20240719', '')