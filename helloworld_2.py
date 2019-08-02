import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import win32com.client
import ctypes
import mysql.connector
import pandas as pd

g_objCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
g_objCpCybos= win32com.client.Dispatch('CpUtil.CpCybos')
g_objCpTrade = win32com.client.Dispatch('CpTrade.CpTdUtil')
g_objFutureMgr = win32com.client.Dispatch("CpUtil.CpFutureCode")
g_objStockWeek = win32com.client.Dispatch("DsCbo1.StockWeek")

code_dict = {'A000660': 0,
             'A010950': 1,
             'A105560': 2,
             'A000270': 3,
             'A066570': 4
             }


class CpEvent:

    instance = None
    main_win = None

    def OnReceived(self):

        code = CpEvent.instance.GetHeaderValue(0)  # 종목코드
        name = CpEvent.instance.GetHeaderValue(1)  # 종목명
        time = CpEvent.instance.GetHeaderValue(3)  # 시간
        cprice = CpEvent.instance.GetHeaderValue(13)  # 종가
        diff = CpEvent.instance.GetHeaderValue(2)  # 대비
        open = CpEvent.instance.GetHeaderValue(4)  # 시가
        high = CpEvent.instance.GetHeaderValue(5)  # 고가
        low = CpEvent.instance.GetHeaderValue(6)  # 저가
        offer = CpEvent.instance.GetHeaderValue(7)  # 매도호가
        bid = CpEvent.instance.GetHeaderValue(8)  # 매수호가
        vol = CpEvent.instance.GetHeaderValue(9)  # 거래량
        vol_value = CpEvent.instance.GetHeaderValue(10)  # 거래대금
        exFlag = CpEvent.instance.GetHeaderValue(19)  # 예상체결 플래그

        line_no = code_dict[code]
        CpEvent.main_win.price_table.setItem(line_no, 0, QTableWidgetItem(code))
        CpEvent.main_win.price_table.setItem(line_no, 1, QTableWidgetItem(name))
        CpEvent.main_win.price_table.setItem(line_no, 2, QTableWidgetItem(str(cprice)))
        CpEvent.main_win.price_table.setItem(line_no, 3, QTableWidgetItem(str(diff)))
        CpEvent.main_win.price_table.setItem(line_no, 4, QTableWidgetItem(str(offer)))
        CpEvent.main_win.price_table.setItem(line_no, 5, QTableWidgetItem(str(bid)))
        CpEvent.main_win.price_table.setItem(line_no, 6, QTableWidgetItem(str(vol)))
        CpEvent.main_win.price_table.setItem(line_no, 7, QTableWidgetItem(str(vol_value)))
        CpEvent.main_win.price_table.setItem(line_no, 8, QTableWidgetItem(str(open)))
        CpEvent.main_win.price_table.setItem(line_no, 9, QTableWidgetItem(str(high)))
        CpEvent.main_win.price_table.setItem(line_no, 10, QTableWidgetItem(str(low)))
        CpEvent.main_win.price_table.resizeColumnsToContents()

        # if exFlag == '1':  # 동시호가 시간 (예상체결)
        #     print("실시간(예상체결)", timess, "*", cprice, "대비", diff, "체결량", cVol, "거래량", vol)
        # elif exFlag == ord('2'):  # 장중(체결)
        #     print("실시간(장중 체결)", timess, cprice, "대비", diff, "체결량", cVol, "거래량", vol)


class CpStockCur:

    def __init__(self, main_win):
        self.main = main_win

    def Subscribe(self, code):
        self.objStockCur = win32com.client.Dispatch("DsCbo1.StockCur")
        win32com.client.WithEvents(self.objStockCur, CpEvent)
        self.objStockCur.SetInputValue(0, code)
        CpEvent.instance = self.objStockCur
        CpEvent.main_win = self.main
        self.objStockCur.Subscribe()

    def Unsubscribe(self):
        self.objStockCur.Unsubscribe()


class CpStockMst:

    def __init__(self, main_win):
        self.main = main_win
        self.objStockMst = win32com.client.Dispatch("DsCbo1.StockMst")

    def Request(self, code):
        # 연결 여부 체크
        bConnect = g_objCpCybos.IsConnect
        if bConnect == 0:
            print("PLUS가 정상적으로 연결되지 않음. ")
            return False

        # 현재가 객체 구하기
        self.objStockMst.SetInputValue(0, code)
        self.objStockMst.BlockRequest()

        # 현재가 통신 및 통신 에러 처리
        rqStatus = self.objStockMst.GetDibStatus()
        rqRet = self.objStockMst.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        # 현재가 정보 조회
        code = self.objStockMst.GetHeaderValue(0)  # 종목코드
        name = self.objStockMst.GetHeaderValue(1)  # 종목명
        time = self.objStockMst.GetHeaderValue(4)  # 시간
        cprice = self.objStockMst.GetHeaderValue(11)  # 종가
        diff = self.objStockMst.GetHeaderValue(12)  # 대비
        open = self.objStockMst.GetHeaderValue(13)  # 시가
        high = self.objStockMst.GetHeaderValue(14)  # 고가
        low = self.objStockMst.GetHeaderValue(15)  # 저가
        offer = self.objStockMst.GetHeaderValue(16)  # 매도호가
        bid = self.objStockMst.GetHeaderValue(17)  # 매수호가
        vol = self.objStockMst.GetHeaderValue(18)  # 거래량
        vol_value = self.objStockMst.GetHeaderValue(19)  # 거래대금

        # print("코드 이름 시간 현재가 대비 시가 고가 저가 매도호가 매수호가 거래량 거래대금")
        #
        # print(code, name, time, cprice, diff, open, high, low, offer, bid, vol, vol_value)
        line_no = code_dict[code]
        self.main.price_table.setItem(line_no, 0, QTableWidgetItem(code))
        self.main.price_table.setItem(line_no, 1, QTableWidgetItem(name))
        self.main.price_table.setItem(line_no, 2, QTableWidgetItem(str(cprice)))
        self.main.price_table.setItem(line_no, 3, QTableWidgetItem(str(diff)))
        self.main.price_table.setItem(line_no, 4, QTableWidgetItem(str(offer)))
        self.main.price_table.setItem(line_no, 5, QTableWidgetItem(str(bid)))
        self.main.price_table.setItem(line_no, 6, QTableWidgetItem(str(vol)))
        self.main.price_table.setItem(line_no, 7, QTableWidgetItem(str(vol_value)))
        self.main.price_table.setItem(line_no, 8, QTableWidgetItem(str(open)))
        self.main.price_table.setItem(line_no, 9, QTableWidgetItem(str(high)))
        self.main.price_table.setItem(line_no, 10, QTableWidgetItem(str(low)))
        self.main.price_table.resizeColumnsToContents()
        return True


class PriceHistory:

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.db_config = {
            'host': '192.168.1.2',
            'database': 'market',
            'user': 'root',
            'passwd': 'goose'
        }
        print("init PriceHistory class")

    def request_history(self, code):
        bConnect = g_objCpCybos.IsConnect
        if bConnect == 0:
            print("PLUS가 정상적으로 연결되지 않음.")
            exit()

        # 일자별 object 구하기
        g_objStockWeek.SetInputValue(0, code)  # 종목 코드 - 삼성전자

        # 최초 데이터 요청
        ret = self.request_com(g_objStockWeek)
        if not ret:
            exit()

        # 연속 데이터 요청
        # 예제는 5번만 연속 통신 하도록 함.
        NextCount = 1
        while g_objStockWeek.Continue:  # 연속 조회처리
            NextCount += 1
            if NextCount > 20:
                break
            ret = self.request_com(g_objStockWeek)
            if not ret:
                exit()

    def request_com(self, obj):
        # 데이터 요청
        obj.BlockRequest()

        # 통신 결과 확인
        rqStatus = obj.GetDibStatus()
        rqRet = obj.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        dates, opens, highs, lows, closes, diffs, vols = [], [], [], [], [], [], []
        # 일자별 정보 데이터 처리
        count = obj.GetHeaderValue(1)  # 데이터 개수
        for i in range(count):
            date = obj.GetDataValue(0, i)  # 일자
            open = obj.GetDataValue(1, i)  # 시가
            high = obj.GetDataValue(2, i)  # 고가
            low = obj.GetDataValue(3, i)  # 저가
            close = obj.GetDataValue(4, i)  # 종가
            diff = obj.GetDataValue(5, i)  # 전일대비 증감
            vol = obj.GetDataValue(6, i)  # 거래량
            dates.append(date)
            opens.append(open)
            highs.append(high)
            lows.append(low)
            closes.append(close)
            diffs.append(diff)
            vols.append(vol)
            print(date, open, high, low, close, diff, vol)
            price_dic = {'date': dates, 'open': opens, 'high':highs,'lows': lows, 'close':closes, 'diff':diffs,'vols':vols }
            df_price = pd.DataFrame(data=price_dic)
            print(df_price)
        return True

    def request_master(self):

        # 연결 여부 체크
        bConnect = g_objCpCybos.IsConnect
        if bConnect == 0:
            print("PLUS가 정상적으로 연결되지 않음. ")
            return

        # 종목코드 리스트 구하기
        objCpCodeMgr = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        codes = objCpCodeMgr.GetStockListByMarket(1)  # 거래소
        codes_2 = objCpCodeMgr.GetStockListByMarket(2)  # 코스닥
        print("거래소 종목코드", len(codes))
        section_codes, names, std_prices = [], [], []

        for i, code in enumerate(codes):
            section_codes.append(objCpCodeMgr.GetStockSectionKind(code))
            names.append(objCpCodeMgr.CodeToName(code))
            std_prices.append(objCpCodeMgr.GetStockStdPrice(code))
        master_dic = {'code': codes,
                      'section_code': section_codes,
                      'prod_name': names,
                      'std_price': std_prices}
        df_kospi = pd.DataFrame(data=master_dic)
        print(df_kospi)

        print("코스닥 종목코드", len(codes_2))
        section_codes, names, std_prices = [], [], []
        for i, code in enumerate(codes_2):
            section_codes.append(objCpCodeMgr.GetStockSectionKind(code))
            names.append(objCpCodeMgr.CodeToName(code))
            std_prices.append(objCpCodeMgr.GetStockStdPrice(code))
        master_dic = {'code': codes_2,
                      'section_code': section_codes,
                      'prod_name': names,
                      'std_price': std_prices}
        df_kosdaq = pd.DataFrame(data=master_dic)
        print(df_kosdaq)
        self.db_master_update(df_kospi, truncate=True)
        self.db_master_update(df_kosdaq)

    def db_master_update(self, df_data, truncate=False):
        self.conn = mysql.connector.connect(**self.db_config)
        self.cursor = self.conn.cursor()
        if truncate:
            self.cursor.execute('truncate table market.master')
            self.conn.commit()
        query = "insert into market.master(code, name, section, std_price) values(%s, %s, %s, %s)"
        query_2 = "update market.master set name = %s, section = %s, std_price =%s where code = %s"
        print('db being updated.')

        for idx, row in df_data.iterrows():
            try:
                arg = (row.code, row.prod_name, row.section_code, row.std_price)
                self.cursor.execute(query, arg)
            except mysql.connector.Error as err:
                arg = (row.prod_name, row.section_code, row.std_price, row.code)
                self.cursor.execute(query_2, arg)

        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        print('db updated.')

    def db_price_update(self, df_data):
        self.conn = mysql.connector.connect(**self.db_config)
        self.cursor = self.conn.cursor()
        query = "insert into market.etp(date, code, name, open, high, low, close, volume) values(%s, %s, %s, %s,%s, %s, %s, %s)"
        query_2 = "update market.etp set open = %s, high = %s, low = %s, close = %s where code = %s and date = %s"
        print('price history being updated.')

        for idx, row in df_data.iterrows():
            try:
                arg = (row.code, row.prod_name, row.section_code, row.std_price)
                self.cursor.execute(query, arg)
            except mysql.connector.Error as err:
                arg = (row.prod_name, row.section_code, row.std_price, row.code)
                self.cursor.execute(query_2, arg)
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        print('db updated.')

    def db_price_update(self, df_data, code,table_name):
        self.conn = mysql.connector.connect(**self.db_config)
        self.cursor = self.conn.cursor()
        query = "insert into market.etp(date, code, open, high, low, close, volume) values(%s, %s, %s, %s,%s, %s, %s, %s)"
        query_2 = "update market.etp set open = %s, high = %s, low = %s, close = %s where code = %s and date = %s"
        print('price history being updated.')

        for idx, row in df_data.iterrows():
            try:
                arg = (row.code, row.prod_name, row.section_code, row.std_price)
                self.cursor.execute(query, arg)
            except mysql.connector.Error as err:
                arg = (row.prod_name, row.section_code, row.std_price, row.code)
                self.cursor.execute(query_2, arg)
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        print('db updated.')

    def db_etp_update(self, truncate=False):
        self.conn = mysql.connector.connect(**self.db_config)
        self.cursor = self.conn.cursor()
        if truncate:
            self.cursor.execute('truncate table market.master')
            self.conn.commit()
        query = "select * from market.master where section = '10' or section = '17'"
        query_2 = "update market.master set name = %s, section = %s, std_price =%s where code = %s"
        print('db being updated.')
        df = pd.read_sql(query, self.conn)
        self.cursor.close()
        self.conn.close()
        print(df)

        for idx, row in df.iterrows():
            self.request_history(row.code)
            if idx > 2:
                break
            # try:
            #     arg = (row.code, row.prod_name, row.section_code, row.std_price)
            #     self.cursor.execute(query, arg)
            # except mysql.connector.Error as err:
            #     arg = (row.prod_name, row.section_code, row.std_price, row.code)
            #     self.cursor.execute(query_2, arg)
        print('db updated.')


class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Algo Trader")
        g_main_win = self
        self.isRq = False
        self.objStockMst = CpStockMst(self)
        self.objStockCur = CpStockCur(self)
        self.objPriceHistory = PriceHistory()

        self.setUI()
        # slot 등록하는 과정
        self.actionQuit.triggered.connect(self.quit)
        self.actionConnect.triggered.connect(self.connect)
        self.actionSubscribe_Price.triggered.connect(self.subscribe)
        self.actionUnsubscribe_Price.triggered.connect(self.unsubscribe)
        self.actionGetHistoryData.triggered.connect(self.get_history_data)
        self.actionGetMasterData.triggered.connect(self.get_master_data)
        self.actionGetETPPrice.triggered.connect(self.get_etp_price)

    def get_etp_price(self):
        # print('etp price ....')
        self.objPriceHistory.db_etp_update()

    def get_master_data(self):
        self.objPriceHistory.request_master()
        # print('get master data')
        # self.objPriceHistory.db_update()
        # self.objPriceHistory.request_history('A000660')

    def get_history_data(self):
        # print('get history data')
        # self.objPriceHistory.db_update()
        self.objPriceHistory.request_history('A000660')

    def setUI(self):
        self.ui = uic.loadUi('win3.ui', self)
        self.ui.setWindowTitle("Algo Trader")
        # self.setGeometry(300, 300, 300, 150)
        self.column_headers = ['종목코드', '종목명', '현재가', '대비', '매수호가', '매도호가', '거래량', '거래대금', '시가', '고가', '저가']
        print(len(code_dict))
        self.price_table.setRowCount(len(code_dict))
        self.price_table.setColumnCount(11)
        self.price_table.setHorizontalHeaderLabels(self.column_headers)

    def quit(self):
        print('close window')
        self.close()

    def connect(self):

        if ctypes.windll.shell32.IsUserAnAdmin():
            print('정상: 관리자권한으로 실행된 프로세스입니다.')
        else:
            print('오류: 일반권한으로 실행됨. 관리자 권한으로 실행해 주세요')
            return False
        # 연결 여부 체크
        if g_objCpCybos.IsConnect == 0:
            print("PLUS가 정상적으로 연결되지 않음. ")
            return False
        print('connected sucessfully')

    def StopSubscribe(self):
        if self.isRq:
            self.objStockCur.Unsubscribe()
            print('unsubscribed successfully')
        self.isRq = False

    def subscribe(self):
        for code in code_dict:      # code_dic는 전역변수
            if not self.objStockMst.Request(code):
                exit()
        # 하이닉스 실시간 현재가 요청
        self.objStockCur.Subscribe(code)
        print("============================")
        print("실시간 현재가 요청 시작")
        print("============================")
        self.isRq = True

    def unsubscribe(self):
        self.StopSubscribe()

    def btn3_clicked(self):
        self.StopSubscribe()
        exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()

