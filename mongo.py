
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
        uri = "mongodb+srv://" + self.config['DEFAULT']['ATLAS_USERNAME'] + ":" + self.config['DEFAULT']['ATLAS_PASS'] + "@stockdb.fil8hwx.mongodb.net/?retryWrites=true&w=majority"

        # Create a new client and connect to the server
        self.client = MongoClient(uri, tlsCAFile=certifi.where())

        print(self.client.list_database_names())

        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)