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
        result = coll.insert_many(arr)
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

