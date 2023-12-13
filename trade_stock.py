import math
from mongo import Mongo
import fid_codes
import trade_algorithm

class Trade_stock():
    def __init__(self, kiwoom): # QAxWidget 상속 받은 경우 오버라이딩 필요        
        self.Kiwoom = kiwoom
        self.Mongo = Mongo()        

    def register_real_stock_price(self, dateStr, limit):
        code_list_str = ""

        stock_dict = {}

        # 예상 종목
        for pred in self.Mongo.get_pred_close(dateStr, limit):
            stock = {}
            code_list_str = code_list_str + pred['_id']['code'] + ";"
        
            stock['pred_fluctuation_rate'] = pred['pred_fluctuation_rate']
            stock['pred_close'] = pred['pred_close']
            stock['buy_quantity'] = 0
            stock['buy_close'] = 0
            stock['available_quantity'] = 0
            stock['ror'] = 0.0
            stock['condition'] = 0.0
            stock['name'] = self.Mongo.get_stock_name(pred['_id']['code'])
            stock_dict[pred['_id']['code']] = stock

        # 잔고 
        for balance_stock in self.Kiwoom.get_balance():
            if balance_stock['code'] in stock_dict: # 상승 종목에 잔고가 포함 되어 있을 수 있음
                stock_dict[balance_stock['code']]['buy_close'] = balance_stock['buy_close']
                stock_dict[balance_stock['code']]['buy_quantity'] = balance_stock['available_quantity'] # 매수 완료 건 표시 그렇지 않은 경우 잔고에 있었으나, 전량 매도한 건 매수 주문하게 됨
                stock_dict[balance_stock['code']]['available_quantity'] = balance_stock['available_quantity']    
                stock_dict[balance_stock['code']]['ror'] = balance_stock['ror']
            else: # 잔고에만 있는 종목의 경우
                stock = {}
                code_list_str = code_list_str + balance_stock['code'] + ";"

                stock['buy_close'] = balance_stock['buy_close']
                stock['available_quantity'] = balance_stock['available_quantity']
                stock['buy_quantity'] = 0
                stock['condition'] = 0.0
                stock['ror'] = balance_stock['ror']
                stock['pred_fluctuation_rate'] = 100 # 잔고의 경우 예상등락률 없으므로 100%로 설정
                stock['name'] = self.Mongo.get_stock_name(balance_stock['code'])
                stock_dict[balance_stock['code']] = stock

            # 잔고 수익률에 따라 바로 매도
            sell_quantity_rate, ror = trade_algorithm.get_sell_quantity_and_ror(balance_stock['close'], stock_dict[balance_stock['code']], self.Kiwoom.logger)            
            sell_quantity = math.trunc(stock['available_quantity'] * sell_quantity_rate)
            
            if sell_quantity > 0:
                self.Kiwoom.logger.info("코드: {} ROR: {} 매도주문수량: {}".format(balance_stock['code'], ror, sell_quantity))
                print("코드: {} ROR: {} 매도주문수량: {}".format(balance_stock['code'], ror, sell_quantity))
                self.Kiwoom.sell_stock(balance_stock['code'], '', sell_quantity)
                

        fids = fid_codes.get_fid("체결시간") # 현제 체결시간만 등록해도 모든 데이터 가져옴. 키움 API 업데이트에 따라 리스트로 만들어야 할 수 있음

        # print(stock_dict)

        self.Kiwoom.set_real_reg("9001", code_list_str, fids, "0", stock_dict)