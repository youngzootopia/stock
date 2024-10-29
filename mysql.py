import pymysql
import json
import pandas as pd

class MySql():
    def __init__(self):
        super().__init__()
        with open('./config/pass.json') as f:
            self.config = json.load(f)

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
        self.connect()
        cursor = self.client.cursor()
        cols = ",".join([str(i) for i in daily_price_list.columns.tolist()])
        update_cols = ",".join([f"{col} = VALUES({col})" for col in daily_price_list.columns.tolist()])

        for i, row in daily_price_list.iterrows():
            sql = f"INSERT INTO PRICE ({cols}) VALUES (" + "%s," * (len(row) - 1) + "%s) " \
                  f"ON DUPLICATE KEY UPDATE {update_cols}"
            cursor.execute(sql, tuple(row))

        self.client.commit()

        self.close()

    def select_volatility(self, query_date, query_limit):
        """
        주어진 날짜에 대한 변동성을 계산하고 결과를 데이터프레임으로 반환하는 함수

        Args:
        query_date (str): 조회할 날짜 (YYYYMMDD 형식)
        query_limit (int): 조회할 건수

        Returns:
        pd.DataFrame: 변동성 결과를 포함한 데이터프레임
        """
        # MySQL 쿼리
        query = """
        SELECT A.TICKER, (A.HIGH - A.LOW) / A.CLOSE * 100 AS VOLATILITY
        FROM PRICE A
        WHERE A.DATE = %s
        AND (A.HIGH - A.LOW) / A.CLOSE * 100 BETWEEN 10.0 AND 99.9
        ORDER BY VOLATILITY DESC
        LIMIT %s
        """

        # 데이터베이스 연결 및 쿼리 실행
        try:
            self.connect()
            with self.client.cursor() as cursor:
                cursor.execute(query, (query_date, query_limit))
                result = cursor.fetchall()
                df = pd.DataFrame(result, columns=['TICKER', 'VOLATILITY'])
                return df
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            return None
        finally:
            self.close()