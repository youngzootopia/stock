from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo.errors
import certifi
import json

class Mongo():
    def __init__(self):
        super().__init__()
        with open('./config/pass.json') as f:
            self.config = json.load(f)

        self.connect()

    def connect(self):
        uri = "mongodb+srv://" + self.config['DEFAULT']['ATLAS_USERNAME'] + ":" + self.config['DEFAULT']['ATLAS_PASS'] + "@stockdb.wbsygbk.mongodb.net/?retryWrites=true&w=majority"

        # Create a new client and connect to the server
        self.client = MongoClient(uri, tlsCAFile=certifi.where())

        print(self.client.list_database_names())

        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            self.db = self.client["stock"]
        except Exception as e:
            print(e)

    def insert_price_many(self, arr):
        coll = self.db["price"]
        # print(df.to_json())
        try:
            result = coll.insert_many(arr, ordered = False) # ordered=False 이미 있는 값은 merge
        except Exception as e:
            # print("Error occurred:", e)
            print("Error occurred")
        # result = coll.insert_many(json.loads(df.T.to_json()).values())

        # print(result.inserted_ids)

    def insert_price_daily(self, dict):
        coll = self.db["price"]
        # print(df.to_json())
        try:
            result = coll.insert_one(dict)
        except pymongo.errors.DuplicateKeyError:
            print("DuplicateKeyError")
        # result = coll.insert_many(json.loads(df.T.to_json()).values())

        # print(result.inserted_ids)

    def delete_Many(self, query):
        coll = self.db["price"]

        d = coll.delete_many(query)

        print(d.deleted_count, " documents deleted !!")

    def get_min_date(self):
        coll = self.db["price"]

        agg_result = coll.aggregate(
            [{
            "$group" : 
                {"_id" : None, 
                "minDate" : {"$min" : "$_id.date"}
                }
            }])
        
        # 쿼리결과가 1개 뿐임
        return agg_result.next()['minDate']

    def get_price_data(self, code):
        coll = self.db["price"]

        find_result = coll.aggregate(
            [{
                "$match" :
                    {"_id.code": code}}, 
            {
                "$project" : {
                    "_id" : 0, 
                    "date" : "$_id.date", 
                    "open" : 1, 
                    "high" : 1, 
                    "low" : 1, 
                    "close" : 1, 
                    "volume" : 1}

            }])

        return find_result
    
    def get_stock_list(self):
        coll = self.db["price"]

        stock_list = coll.distinct("_id.code")

        return stock_list
    
    def insert_code_name_many(self, arr):
        coll = self.db["code"]
        result = coll.insert_many(arr)

    def insert_code_name(self, code):
        coll = self.db["code"]
        result = coll.insert_one(code)        

    def insert_predict_price(self, predict_price):
        coll = self.db["predict"]
        try:
            result = coll.insert_one(predict_price)
        except pymongo.errors.DuplicateKeyError:
            print("predict DuplicateKeyError")
        

    def get_stock_name(self, code):
        coll = self.db["code"]

        code_and_name = coll.find_one({'_id.code': code})

        try:
            name = code_and_name["name"]
        except TypeError:
            name = ""
            print("{}: no name".format(code))

        return name
    
    def update_predict_price(self, actually_price):
        coll = self.db["predict"]
        try:
            close = self.get_recent_close(actually_price['_id']['code'])['close']
        except TypeError:
            print("전날 예측 종가 없음")
            return

        try:
            result = coll.update_one({"_id.code": actually_price['_id']['code']
                                  , "_id.date": actually_price['_id']['date']}
                                 , {"$set":{"close": actually_price['close']
                                            , "fluctuation_rate": round(((actually_price['close'] - close) / close * 100), 2)
                                            }})
        except pymongo.errors.DuplicateKeyError:
            print("DuplicateKeyError")
        # result = coll.insert_many(json.loads(df.T.to_json()).values())

        # print(result.inserted_ids)

    def get_recent_close(self, code):
        coll = self.db["price"]

        filter = {
            '_id.code': code
            }
        project = {
            'close': 1, 
            '_id': 0
            }
        sort = list({
            '_id.date': -1
            }.items())
        limit = 1

        result = coll.find_one(
            filter = filter,
            projection = project,
            sort = sort,
            limit = limit
        )

        return result
    
    def get_pred_close(self, dateStr, limit):
        coll = self.db["predict"]

        filter = {
                '_id.date': dateStr, 
                'pred_fluctuation_rate': { # 5% 이상
                    '$gt': 3,
                    '$lt': 30 # 정리 매매의 경우 기존 종가가 너무 높을 수 있기 때문에 예측값이 크게 나옴
                },
                'pred_close': {
                    '$gt': 1500 # 모의 투자에서는 현재가 1000원 이하 주문 불가
                }
            }
        project = {
            'pred_close': 1,
            'pred_fluctuation_rate': 1, 
            '_id.code': 1
            }
        sort = list({
            'pred_fluctuation_rate': -1,
            'pred_close': 1
            }.items())

        result = coll.find(
            filter = filter,
            projection = project,
            sort = sort,
            limit = limit
        )

        return result
    
    def get_kospi_pred_close(self, dateStr):
        coll = self.db["predict"]

        filter = {
            '_id.date': dateStr,
            '_id.code': "KOSPI"
            }
        project = {
            'pred_close': 1,
            'pred_fluctuation_rate': 1, 
            '_id.code': 1
            }
        result = coll.find_one(
            filter = filter,
            projection = project
        )

        return result