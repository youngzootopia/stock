import pymysql
import json
import pandas as pd

class MySql():
    def __init__(self):
        super().__init__()
        with open('./config/pass.json') as f:
            self.config = json.load(f)

        self.connect()

    def connect(self):
        self.client = pymysql.connect(
            host = self.config['DEFAULT']['MYSQL_HOST'],
            user = self.config['DEFAULT']['MYSQL_USERNAME'],
            password = self.config['DEFAULT']['MYSQL_PASS'],
            database = self.config['DEFAULT']['MYSQL_DATABASE']
            )
        
    def close(self):
        self.client.close()
        
    def insert_daily(self, daily_price_list):
        cursor = self.client.cursor()
        cols = ",".join([str(i) for i in daily_price_list.columns.tolist()])
        update_cols = ",".join([f"{col} = VALUES({col})" for col in daily_price_list.columns.tolist()])

        for i, row in daily_price_list.iterrows():
            sql = f"INSERT INTO PRICE ({cols}) VALUES (" + "%s," * (len(row) - 1) + "%s) " \
                  f"ON DUPLICATE KEY UPDATE {update_cols}"
            cursor.execute(sql, tuple(row))

        self.client.commit()