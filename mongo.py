
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
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
        result = coll.insert_one(dict)
        # result = coll.insert_many(json.loads(df.T.to_json()).values())

        # print(result.inserted_ids)
