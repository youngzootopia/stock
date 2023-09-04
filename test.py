from pandas import DataFrame
import json

daeshin = {'code':  ['000020', '000020', '000020', '000020', '000020'],
           'date':  ['20010101', '20020101', '20030101', '20040101', '20050101',],
           'open':  [11650, 11100, 11200, 11100, 11000],
           'high':  [12100, 11800, 11200, 11100, 11150],
           'low' :  [11600, 11050, 10900, 10950, 10900],
           'close': [11900, 11600, 11000, 11100, 11050]}

daeshin_day = DataFrame(daeshin)

daeshin_day.set_index(['code', 'date'], inplace = True)
daeshin_day = daeshin_day.drop_duplicates()
daeshin_day = daeshin_day.sort_index()

daeshin_day = daeshin_day.loc[('000020', '20020101') : ('000020', '20040101')]

print(json.loads(daeshin_day.T.to_json()))


daeshin = {'_id': {
            'code':  ['000020', '000020', '000020', '000020', '000020'],
            'date':  ['20010101', '20020101', '20030101', '20040101', '20050101',] },
           'open':  [11650, 11100, 11200, 11100, 11000],
           'high':  [12100, 11800, 11200, 11100, 11150],
           'low' :  [11600, 11050, 10900, 10950, 10900],
           'close': [11900, 11600, 11000, 11100, 11050]}

print(daeshin_day = DataFrame(daeshin))

