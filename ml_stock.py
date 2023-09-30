from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import numpy as np
from mongo import Mongo

class Ml_stock():
    def __init__(self):
        super().__init__()
        self.Mongo = Mongo()

    def predict_stock_close_price(self, code):
        stock_code = code

        df = pd.DataFrame(self.Mongo.get_price_data(stock_code))
        df.set_index(keys = 'date', inplace = True)
        df.sort_index()

        data = []
        target = []

        for i in range(len(df) - 1):
            a = list(df.iloc[i]) # 학습 데이터는 주가정보 전부
            b = df.iloc[i + 1, 3] # open, high, low, close, volume, 정답 데이터는 종가

            data.append(a)
            target.append(b)

        data = np.array(data)
        target = np.array(target)

        rf = RandomForestRegressor(oob_score = True)
        rf.fit(data, target)
        score = rf.oob_score_

        # 금일 종가
        new = df.iloc[-1]

        pred = rf.predict([new])
        print("예측 종가: {}".format(pred[0], df.iloc[-1, 3]))



