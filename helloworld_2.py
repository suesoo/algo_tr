import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
import win32com.client
import ctypes


g_objCodeMgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
g_objCpCybos= win32com.client.Dispatch('CpUtil.CpCybos')
g_objCpTrade = win32com.client.Dispatch('CpTrade.CpTdUtil')
g_objFutureMgr = win32com.client.Dispatch("CpUtil.CpFutureCode")

code_dict = {'A000660': 0,
             'A010950': 1,
             'A105560': 2,
             'A000270': 3,
             'A066570': 4
             }

g_main_win = None


class CpEvent:

    instance = None

    def OnReceived(self):
        # time = CpEvent.instance.GetHeaderValue(3)  # 시간
        # timess = CpEvent.instance.GetHeaderValue(18)  # 초
        # exFlag = CpEvent.instance.GetHeaderValue(19)  # 예상체결 플래그
        # cprice = CpEvent.instance.GetHeaderValue(13)  # 현재가
        # diff = CpEvent.instance.GetHeaderValue(2)  # 대비
        # cVol = CpEvent.instance.GetHeaderValue(17)  # 순간체결수량
        # vol = CpEvent.instance.GetHeaderValue(9)  # 거래량

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
        g_main_win.price_table.setItem(line_no, 0, QTableWidgetItem(code))
        g_main_win.price_table.setItem(line_no, 1, QTableWidgetItem(name))
        g_main_win.price_table.setItem(line_no, 2, QTableWidgetItem(str(cprice)))
        g_main_win.price_table.setItem(line_no, 3, QTableWidgetItem(str(diff)))
        g_main_win.price_table.setItem(line_no, 4, QTableWidgetItem(str(offer)))
        g_main_win.price_table.setItem(line_no, 5, QTableWidgetItem(str(bid)))
        g_main_win.price_table.setItem(line_no, 6, QTableWidgetItem(str(vol)))
        g_main_win.price_table.setItem(line_no, 7, QTableWidgetItem(str(vol_value)))
        g_main_win.price_table.setItem(line_no, 8, QTableWidgetItem(str(open)))
        g_main_win.price_table.setItem(line_no, 9, QTableWidgetItem(str(high)))
        g_main_win.price_table.setItem(line_no, 10, QTableWidgetItem(str(low)))
        g_main_win.price_table.resizeColumnsToContents()

        # if exFlag == '1':  # 동시호가 시간 (예상체결)
        #     print("실시간(예상체결)", timess, "*", cprice, "대비", diff, "체결량", cVol, "거래량", vol)
        # elif exFlag == ord('2'):  # 장중(체결)
        #     print("실시간(장중 체결)", timess, cprice, "대비", diff, "체결량", cVol, "거래량", vol)


class CpStockCur:
    def Subscribe(self, code):
        self.objStockCur = win32com.client.Dispatch("DsCbo1.StockCur")
        win32com.client.WithEvents(self.objStockCur, CpEvent)
        self.objStockCur.SetInputValue(0, code)
        CpEvent.instance = self.objStockCur
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


class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Algo Trader")
        g_main_win = self
        self.isRq = False
        self.objStockMst = CpStockMst(self)
        self.objStockCur = CpStockCur()

        self.setUI()
        # slot 등록하는 과정
        self.actionQuit.triggered.connect(self.quit)
        self.actionConnect.triggered.connect(self.connect)
        self.actionSubscribe_Price.triggered.connect(self.subscribe)
        self.actionUnsubscribe_Price.triggered.connect(self.unsubscribe)

    def setUI(self):
        self.ui = uic.loadUi('win3.ui', self)
        self.ui.setWindowTitle("Algo Trader")
        # self.setGeometry(300, 300, 300, 150)
        self.column_headers = ['종목코드', '종목명', '현재가', '대비', '매수호가', '매도호가', '거래량', '거래대금', '시가', '고가', '저가']
        print(len(code_dict))
        self.price_table.setRowCount(len(code_dict))
        self.price_table.setColumnCount(11)
        self.price_table.setHorizontalHeaderLabels(self.column_headers)

        # btn1 = QPushButton("요청 시작", self)
        # btn1.move(20, 20)
        # btn1.clicked.connect(self.btn1_clicked)
        #
        # btn2 = QPushButton("요청 종료", self)
        # btn2.move(20, 70)
        # btn2.clicked.connect(self.btn2_clicked)
        #
        # btn3 = QPushButton("종료", self)
        # btn3.move(20, 120)
        # btn3.clicked.connect(self.btn3_clicked)

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

