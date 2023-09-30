from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import numpy as np
from mongo import Mongo

Mongo = Mongo()

stock_list = Mongo.get_stock_list()


for stock_code in stock_list:
    df = pd.DataFrame(Mongo.get_price_data(stock_code))
    df.set_index(keys = 'date', inplace = True)
    df.sort_index()

    data = []
    target = []

    for i in range(len(df) - 2):
        a = list(df.iloc[i]) # 학습 데이터는 주가정보 전부
        b = df.iloc[i + 1, 3] # open, high, low, close, volume, 정답 데이터는 종가

        data.append(a)
        target.append(b)

    data = np.array(data)
    target = np.array(target)

    rf = RandomForestRegressor(oob_score = True)
    rf.fit(data, target)
    score = rf.oob_score_

    # print("평가 점수: {}".format(score))

    # 금일 종가
    new = df.iloc[-2]

    pred = rf.predict([new])
    print("예측 종가: {}, 실제 종가: {}".format(pred[0], df.iloc[-1, 3]))



