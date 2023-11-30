from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

import pandas as pd
import numpy as np
from mongo import Mongo

import time

class Ml_stock():
    def __init__(self):
        super().__init__()
        self.Mongo = Mongo()

    def predict_stock_close_price(self, stock_code, date):
        start_time = time.time()
        df = pd.DataFrame(self.Mongo.get_price_data(stock_code))

        if len(df) < 2: # 신규 상장한 경우
            return

        df.set_index(keys = 'date', inplace = True)
        df = df.sort_index(ascending = True)

        data = []
        target = []

        for i in range(len(df) - 1):
            a = list(df.iloc[i]) # 학습 데이터는 주가정보 전부
            b = df.iloc[i + 1, 3] # open, high, low, close, volume, 정답 데이터는 종가

            data.append(a)
            target.append(b)

        data = np.array(data)
        target = np.array(target)

        rf_score, lr_score = 0, 0
        rf = RandomForestRegressor(oob_score = True)
        lr = LinearRegression()
        for i in range(5):
            rf.fit(data, target)
            rf_score = rf.oob_score_

            lr.fit(data, target)
            lr_score = lr.score(data, target)

            if rf_score > 0.99 or lr_score > 0.99:
                break

        # 금일 종가
        new = df.iloc[-1]

        rf_pred = rf.predict([new])
        lr_pred = lr.predict([new])
        # print("예측 종가: {}".format(pred[0], df.iloc[-1, 3]))

        pred = (rf_pred[0] + lr_pred[0]) / 2

        predict_price = {'name': self.Mongo.get_stock_name(stock_code)
                         , 'pred_close': pred
                         , 'pred_fluctuation_rate': round(((pred - df.iloc[-1, 3]) / df.iloc[-1, 3] * 100), 2)}
        predict_price["_id"] = {"code": stock_code, "date": date}
        self.Mongo.insert_predict_price(predict_price)

        return time.time() - start_time