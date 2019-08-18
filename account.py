from PyQt5.QtWidgets import *
from PyQt5 import uic
import db_man as db
import api


class Order:

    def __init__(self):
        self.obj_stock_order = api.CreonAPI.obj_stock_order

    def send_order(self, acc, pw, code, buy_sell, qty, price):
        # 연결 여부 체크
        bConnect = api.CreonAPI.obj_cp_cybos.IsConnect
        if bConnect == 0:
            print("PLUS가 정상적으로 연결되지 않음. ")
            exit()

        # 주문 초기화
        obj_trade = api.CreonAPI.obj_cp_trade
        initCheck = obj_trade.TradeInit(0)
        if initCheck != 0:
            print("주문 초기화 실패")
            exit()

        # 주식 매수 주문
        # acc = obj_trade.AccountNumber[0]  # 계좌번호
        accFlag = obj_trade.GoodsList(acc, 1)  # 주식상품 구분
        print(acc, accFlag[0])

        self.obj_stock_order.SetInputValue(0, buy_sell)  # 2: 매수
        self.obj_stock_order.SetInputValue(1, acc)  # 계좌번호
        self.obj_stock_order.SetInputValue(2, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
        self.obj_stock_order.SetInputValue(3, code)  # 종목코드 - A003540 - 대신증권 종목
        self.obj_stock_order.SetInputValue(4, qty)  # 매수수량 10주
        self.obj_stock_order.SetInputValue(5, price)  # 주문단가  - 14,100원
        self.obj_stock_order.SetInputValue(7, "0")  # 주문 조건 구분 코드, 0: 기본 1: IOC 2:FOK
        self.obj_stock_order.SetInputValue(8, "01")  # 주문호가 구분코드 - 01: 보통

        # 매수 주문 요청
        self.obj_stock_order.BlockRequest()

        rqStatus = self.obj_stock_order.GetDibStatus()
        rqRet = self.obj_stock_order.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            exit()


class OrderDlg(QDialog):

    def __init__(self):

        super(OrderDlg, self).__init__()
        self.ui = uic.loadUi('order.ui', self)
        self.ui.show()
        self.pushOrder.clicked.connect(self.ordered)
        self.pushClose.clicked.connect(self.closed)
        self.db = db.DB()
        self.master_df = self.db.get_master(where="where section='10'")
        names = self.master_df.name.tolist()
        self.comboProduct.addItems(names)
        self.obj_order = Order()
        print(self.master_df)

    def ordered(self):
        price = self.linePrice.text()
        qty = self.lineQty.text()
        if self.radioBuy.isChecked():
            buy_sell = '2'
        elif self.radioSell.isChecked():
            buy_sell = '1'
        else:
            print('not selected')
        self.obj_order.send_order()

    def closed(self):
        print('closed')
        self.close()


class OrderStauts(QWidget):

    def __init__(self):

        super(OrderStauts, self).__init__()
        self.ui = uic.loadUi('order_status.ui', self)
        self.ui.show()
        # self.pushOrder.clicked.connect(self.ordered)
        self.pushClose.clicked.connect(self.closed)
        self.column_headers = ['주문번호', '원주문번호', '체결/미체결', '매수/매도', '주문가격', '주문수량', '체결수량', '체결가격', '미체결잔량']
        self.tableStatus.setRowCount(5)
        self.tableStatus.setColumnCount(len(self.column_headers))
        self.tableStatus.setHorizontalHeaderLabels(self.column_headers)

        # self.db = db.DB()
        # self.master_df = self.db.get_master(where="where section='10'")
        # names = self.master_df.name.tolist()
        # self.comboProduct.addItems(names)
        # print(self.master_df)

    # def ordered(self):
    #     print(self.linePrice.text())
    #     print(self.lineQty.text())
    #     if self.radioBuy.isChecked():
    #         print('buy selected')
    #     elif self.radioSell.isChecked():
    #         print('sell selected')
    #     else:
    #         print('not selected')
    #     print('ordered')
    #
    def closed(self):
        print('closed')
        self.close()