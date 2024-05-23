import pandas
from pykrx import stock
# from datetime import datetime
from mysql import MySql
# from ml_stock import Ml_stock
# from teleBot import TeleBot

def daily_load(start_date):
    # 적재 Start
    df = stock.get_market_ohlcv(start_date, market="KOSPI")
    # pykrx의 경우 한글로 되어 있어 컬럼명, 인덱스명 변경
    df.columns = ['open', 'high', 'low', 'close', 'quantity', 'volume', 'per_change']
    df = df.reset_index()
    df = df.rename(columns = {'티커':'ticker'})
    # pykrx의 해당 메소드에는 날짜는 포함되어 있지 않아서 날짜 컬럼 추가
    df['date'] = start_date
    df['ticker'] = df['ticker'].astype('str')
    df['date'] = df['date'].astype('str')
    new_column_order = ['ticker', 'date', 'open', 'high', 'low', 'close', 'quantity', 'volume', 'per_change']
    df = df[new_column_order]

    mysql = MySql()
    mysql.insert_daily(df)
    mysql.close()



# def daily_load(start_date, end_date):
    # 종목 정보 가져오기
    # 기존 로직에서는 Kiwoom API로 종목 정보 가져왔으나, pykrx쓰므로 필요 없음
    # 코스피, 코스닥도 종가 예측했었으나, 예측률이 너무 낮아서 자동매매전략 수정에 따라 필요 없음 
    # 특정 종목부터 혹은 종목까지 적재 했었으나, pykrx의 경우 속도 빠르므로 전부 적재
    
    # 적재 Start
    # df = stock.get_market_ohlcv("20240522", market="KOSPI")
    # df.columns = ['open', 'high', 'low', 'close', 'quantity', 'volume', 'change']
    # print(df.head(3))



#                 # total = {'open': 0, 'high': 0, 'low': 0, 'close': 0, 'volume': 0 }

#                 # 신규 상장 주식의 경우 코드네임 저장
#                 if Mongo.get_stock_name(stock_code) == "":
#                     stock = {}
#                     stock['_id'] = {}
#                     stock['_id']['code'] = stock_code
#                     stock['name'] = Kiwoom.get_code_name(stock_code)

#                     Mongo.insert_code_name(stock)
            
#             # 데이터가 있어야 하고, 시가가 0원 이상만 적재
#             if len(stock_price) > 0 and stock_price['open'] > 0:
#                 stock_list.append(stock_price)
#                 # 전날 예측한 종가 검증을 위해 실제 종가 및 등락률 업데이트
#                 # 231127 이후 업데이트 안함. MONGODB의 경우 업데이트 시 로그가 쌓이는데 양이 너무 많아짐
#                 # Mongo.update_predict_price(stock_price)

#                 Mongo.insert_price_daily(stock_price)

#                 # 데이터 예측
#                 XKRX = xcals.get_calendar("XKRX")
#                 next_open = XKRX.next_open(dateStr)

#                 ml_time = Ml_stock.predict_stock_close_price(stock_code, next_open.strftime("%Y%m%d"))
                
# def full_load():
#     # 종목 정보 가져오기
#     code_list = Kiwoom.get_code_list_stok_market("0")
#     code_list = code_list + Kiwoom.get_code_list_stok_market("10")

#     isNext = True
#     i = 0
#     for code in code_list:
#         i = i + 1
#         if code == "000020": # 000020 첫 주식
#             isNext = False

#         if isNext:
#             continue    
#         print("{}: {} / {}".format(code, i, len(code_list)))
#         stock_price_list = Kiwoom.get_price(code)

#     # 이상한 종목을 가져오는 경우가 있음. 이런 경우 size 필터링해서 DB에 안넣기
#         if len(stock_price_list) > 0:
#             Mongo.insert_price_many(stock_price_list)

# # json 파일 생성, DB에 잘 넣고 있어 딱히 필요 없을 듯
# def save_json(stock_list, file_name):
#     if file_name == "":
#         file_name = "daily_stock_list.json"

#     with open(file_name, "w") as json_file:
#         json.dump(stock_list, json_file, indent=4)

# @dispatch()
# def delete_closed_data():
#     delete_closed_data(Mongo.get_min_date())

# # daily_load 기간으로 실행 시 주말도 적재하기 때문에, 휴장 데이터 삭제
# # delete_closed_data('20230923')
# @dispatch(str)
# def delete_closed_data(start_date):
#     end_date = datetime.now().strftime("%Y%m%d")

#     # 기간 동안의 전체 날짜
#     date_list = pandas.date_range(start = start_date, end = end_date, freq = 'D')
#     # 기간 동안의 개장일
#     open_date_list = xcals.get_calendar("XKRX", start = start_date, end = end_date).schedule.index

#     # 기간 동안의 휴장일
#     close_date_list = date_list.drop(labels = open_date_list)

#     for close_date in close_date_list:
#         print(close_date)
#         query = {"_id.date": close_date.strftime("%Y%m%d")}
#         Mongo.delete_Many(query)
    
# def load_stock_code_and_name():
#     # 종목 정보 가져오기
#     kospi_list = Kiwoom.get_code_list_stok_market("0")
#     kosdak_list = Kiwoom.get_code_list_stok_market("10")
    
#     total = []
#     for code in kospi_list:
#         name = Kiwoom.get_code_name(code)

#         print("{0}: {1}".format(code, name))
#         code_and_name = {'name': name}
#         code_and_name["_id"] = {"code": code}
#         total.append(code_and_name)

#     for code in kosdak_list:
#         name = Kiwoom.get_code_name(code)

#         print("{0}: {1}".format(code, name))
#         code_and_name = {'name': name}
#         code_and_name["_id"] = {"code": code}
#         total.append(code_and_name)

#     Mongo.insert_code_name_many(total)


# def stock_market_full_load(code, dateStr):

#     stock_price_list = Kiwoom.get_market_price(code, dateStr)

#     # 이상한 종목을 가져오는 경우가 있음. 이런 경우 size 필터링해서 DB에 안넣기
#     if len(stock_price_list) > 0:
#         Mongo.insert_price_many(stock_price_list)

#     return stock_price_list

# def report_close_pred(dateStr):
#     pred_kospi = Mongo.get_market_pred_close(dateStr, 'KOSPI')
#     pred_kosdak = Mongo.get_market_pred_close(dateStr, 'KOSDAQ')

#     TeleBot.report_message("{0} 증시 예측 보고서\nKOSPI : {1}\nKOSDAQ: {2}".format(dateStr, pred_kospi['pred_fluctuation_rate'], pred_kosdak['pred_fluctuation_rate']))

#     message = ""
#     for pred in Mongo.get_pred_close(dateStr, 30):
#         print(pred)
#         message = message + "{0}\n상승률: {1}, 종가: {2}\n\n".format(Mongo.get_stock_name(pred['_id']['code']), pred['pred_fluctuation_rate'], round(pred['pred_close']))
        
#     TeleBot.report_message(message)

# if __name__ == '__main__': # 중복 방지를 위해 사용
#     # 키움 API 실행
#     app = QApplication(sys.argv)
#     # 로깅
#     log_path = './log/' + datetime.today().strftime("%Y%m%d") + '.log'
#     logger = logging.getLogger('logger')
#     logger.setLevel(logging.DEBUG)
#     file_handler = logging.FileHandler(log_path, encoding='utf-8')
#     formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(message)s]")
#     file_handler.setFormatter(formatter)
#     logger.addHandler(file_handler)
#     Kiwoom = Kiwoom(logger)
#     Mongo = Mongo()
#     Ml_stock = Ml_stock()
#     TeleBot = TeleBot()

#     # 1. 종목 코드(코스피, 코스닥) 네임 저장하기
#     # load_stock_code_and_name()

#     # 2. 일괄 적재 완료(240107)
#     # full_load()

#     # 2. 일 적재
#     dateStr = datetime.today().strftime("%Y%m%d")
#     dateStr = '20240522' # 특정날짜 적재 시 수정

#     code = '003380' # 특정 코드부터 적재 할 시 수정

#     daily_load(dateStr, code)
#     # daily_load('20240509', '20240510', code)   
     

#     # 휴일인 경우 데이터 삭제
#     delete_closed_data(dateStr)    
    
#     XKRX = xcals.get_calendar("XKRX")
#     next_open = XKRX.next_open(dateStr).strftime("%Y%m%d")
#     report_close_pred(next_open)

#     app.exec_()




daily_load('20240523')