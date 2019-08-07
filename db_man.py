
import mysql.connector
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5 import uic


class SetDB(QDialog):

    def __init__(self):
        super(SetDB, self).__init__()
        self.ui = uic.loadUi('set_db.ui', self)
        self.ui.show()
        self.pushSet.clicked.connect(self.set)
        self.pushClose.clicked.connect(self.closed)

    def set(self):
        pass

    def closed(self):
        self.close()


class DB:

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.db_config = {
            'host': '192.168.1.2',
            'database': 'market',
            'user': 'root',
            'passwd': 'goose'
        }
        print("database connector class")

    def get_master(self, where=''):
        self.conn = mysql.connector.connect(**self.db_config)
        query = 'select * from market.master ' + where
        df = pd.read_sql(query, self.conn)
        self.conn.close()
        return df
