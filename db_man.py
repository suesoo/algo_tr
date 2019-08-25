
import mysql.connector
import pandas as pd
from PyQt5.QtWidgets import *
from PyQt5 import uic


class DB:

    conn = None
    cursor = None
    db_config = {
        'host': '192.168.1.2',
        'port': 3306,
        'database': 'market',
        'user': 'root',
        'passwd': 'test'
    }

    def __init__(self):
        print("database connector class")

    def get_master(self, where=''):
        DB.conn = mysql.connector.connect(**DB.db_config)
        query = 'select * from market.master ' + where
        df = pd.read_sql(query, DB.conn)
        DB.conn.close()
        return df


class SetDB(QDialog):

    def __init__(self):
        super(SetDB, self).__init__()
        self.ui = uic.loadUi('set_db.ui', self)
        self.pushSet.clicked.connect(self.set)
        self.pushClose.clicked.connect(self.closed)

    def show_dlg(self):
        self.ui.show()

    def set(self):
        host = self.lineHost.text()
        port = int(self.linePort.text())
        db = self.lineDatabase.text()
        user = self.lineUser.text()
        password = self.linePassword.text()
        DB.db_config['host'] = host
        DB.db_config['port'] = port
        DB.db_config['database'] = db
        DB.db_config['user'] = user
        DB.db_config['password'] = password
        print('database 접속 방법이 재설정 되었습니다.')
        # print(host,port,db,user,password)

    def closed(self):
        self.close()


