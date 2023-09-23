from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import numpy as np
from mongo import Mongo

Mongo = Mongo()

samsung_df = pd.DataFrame(Mongo.get_price_data("005930"))
samsung_df.set_index(keys = 'date', inplace = True)
samsung_df.sort_index()

data = []
target = []

for i in range(len(samsung_df) - 1):
    a = list(samsung_df.iloc[i]) # 학습 데이터는 주가정보 전부
    b = samsung_df.iloc[i + 1, 3] # open, high, low, close, volume, 정답 데이터는 종가

    data.append(a)
    target.append(b)

data = np.array(data)
target = np.array(target)

rf = RandomForestRegressor(oob_score = True)
rf.fit(data, target)
score = rf.oob_score_

print("평가 점수: {}".format(score))

# 금일 종가
new = samsung_df.iloc[-2]

print(new)

pred = rf.predict([new])
print("내일 종가: {}".format(pred[0]))



