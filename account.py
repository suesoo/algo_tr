from PyQt5.QtWidgets import *
from PyQt5 import uic
import db_man as db
import api
# import Enum


# enum 주문 상태 세팅용
class OrderStatus:
    nothing = 1          # 별 일 없는 상태
    newOrder = 2          # 신규 주문 낸 상태
    orderConfirm = 3      # 신규 주문 처리 확인
    modifyOrder = 4     # 정정 주문 낸 상태
    cancelOrder = 5      # 취소 주문 낸 상태


# 주문 체결 pb 기록용(종료 시 받은 데이터 print)
class orderHistoryData:
    def __init__(self):
        self.flag = ""
        self.code = ""
        self.price = 0
        self.orderamount = 0
        self.contamount = 0
        self.etc = ""

    def sethistory(self, flag, code, price, amount, contamount, ordernum, etc):
        self.flag = flag
        self.code = code
        self.price = price
        self.orderamount = amount
        self.contamount = contamount
        self.ordernum = ordernum
        self.etc = etc

    def printhistory(self):
        print(self.flag, self.code, "가격:", self.price, "수량:", self.orderamount, "체결수량:", self.contamount, "주문번호:",
              self.ordernum, self.etc)


class Order:

    def __init__(self, CreonAPI):
        self.api_stock_order = CreonAPI.obj_stock_order
        self.api_cp_cybos = CreonAPI.obj_cp_cybos
        self.api_cp_trade = CreonAPI.obj_cp_trade
        self.history = []

    def send_order(self, acc, code, buy_sell, i_qty, i_price):
        # 연결 여부 체크
        bConnect = self.api_cp_cybos.IsConnect
        if bConnect == 0:
            print("PLUS가 정상적으로 연결되지 않음. ")
            exit()

        # # 주문 초기화
        initCheck = self.api_cp_trade.TradeInit(0)
        if initCheck != 0:
            print("주문 초기화 실패, 체크섬",initCheck)
            exit()

        # # 주식 매수 주문
        # accFlag = self.api_cp_trade.GoodsList(acc, 1)  # 주식상품 구분
        # print(acc, accFlag[0])
        # print('acc flag list', accFlag)

        self.api_stock_order.SetInputValue(0, buy_sell)  # 2: 매수
        self.api_stock_order.SetInputValue(1, acc)  # 계좌번호
        self.api_stock_order.SetInputValue(2, '01')  # 상품구분 - 주식 상품 중 첫번째
        self.api_stock_order.SetInputValue(3, code)  # 종목코드 - A003540 - 대신증권 종목
        self.api_stock_order.SetInputValue(4, i_qty)  # 매수수량 10주
        self.api_stock_order.SetInputValue(5, i_price)  # 주문단가  - 14,100원
        self.api_stock_order.SetInputValue(7, "0")  # 주문 조건 구분 코드, 0: 기본 1: IOC 2:FOK
        self.api_stock_order.SetInputValue(8, "01")  # 주문호가 구분코드 - 01: 보통

        print('order buy_sell={}, acc={}, code={}'.format(buy_sell, acc, code))
        # 매수 주문 요청
        self.api_stock_order.BlockRequest()
        print('order requested')
        rqStatus = self.api_stock_order.GetDibStatus()
        rqRet = self.api_stock_order.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            exit()
        rt_code = self.api_stock_order.GetHeaderValue('3')
        rt_order_no = self.api_stock_order.GetHeaderValue('8')

    def send_cancel_order(self, acc, code, i_prev_order_no, i_qty):
        # 연결 여부 체크
        bConnect = self.api_cp_cybos.IsConnect
        if bConnect == 0:
            print("PLUS가 정상적으로 연결되지 않음. ")
            exit()
        self.api_stock_order.SetInputValue(1, i_prev_order_no)  # 원주문번호
        self.api_stock_order.SetInputValue(2, acc)  # 계좌번호
        self.api_stock_order.SetInputValue(3, '01')  # 상품구분 - 주식 상품 중 첫번째
        self.api_stock_order.SetInputValue(4, code)  # 종목코드
        self.api_stock_order.SetInputValue(5, i_qty)  # 취소수량
        self.api_stock_order.BlockRequest()
        print('order requested')
        rqStatus = self.api_stock_order.GetDibStatus()
        rqRet = self.api_stock_order.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            exit()
        rt_prev_order_no = self.api_stock_order.GetHeaderValue('1')
        rt_cancel_qty = self.api_stock_order.GetHeaderValue('5')

    def send_modi_order(self, acc, code, i_prev_order_no, i_qty, i_price):
        # 연결 여부 체크
        bConnect = self.api_cp_cybos.IsConnect
        if bConnect == 0:
            print("PLUS가 정상적으로 연결되지 않음. ")
            exit()
        self.api_stock_order.SetInputValue(1, i_prev_order_no)  # 원주문번호
        self.api_stock_order.SetInputValue(2, acc)  # 계좌번호
        self.api_stock_order.SetInputValue(3, '01')  # 상품구분 - 주식 상품 중 첫번째
        self.api_stock_order.SetInputValue(4, code)  # 종목코드
        self.api_stock_order.SetInputValue(5, i_qty)  # 정정수량
        self.api_stock_order.SetInputValue(6, i_price)  # 정정 가격
        self.api_stock_order.BlockRequest()
        print('order requested')
        rqStatus = self.api_stock_order.GetDibStatus()
        rqRet = self.api_stock_order.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            exit()
        rt_prev_order_no = self.api_stock_order.GetHeaderValue('1')
        rt_cancel_qty = self.api_stock_order.GetHeaderValue('5')

    def initOrder(self):
        # 주문 정보 초기화
        self.orderStatus = OrderStatus.nothing
        self.ordernum = 0        # 주문번호
        self.remainAmount = 0 # 주문 후 미체결 수량
        self.orderNonce = 9     # 매수 주문 호가 조정 변수 ( 9 > 8 > 7 .. 순으로 호가 조정)

    # 실시간 주문 체결 업데이트
    def monitorOrderStatus(self, code, ordernum, conflags, price, amount, balance):
        print("주문체결: ", code, ordernum, conflags, price, amount, balance)
        if self.orderStatus == OrderStatus.nothing:
            return
        # 체결: 체결 시 체결 수량/미체결 수량 계산
        if conflags == "체결":
            self.remainAmount -= amount  # 미체결 수량 계산
            if self.orderStatus == OrderStatus.orderConfirm:
                print("주문 체결 됨 ", "수량", amount, "잔고수량:", balance, "미체결수량:", self.remainAmount)

            if self.remainAmount <= 0:  # 전량 체결 됨
                self.initOrder()

            # for debug
            history = orderHistoryData()
            history.sethistory(conflags, code, price, self.remainAmount, amount, ordernum, "")
            self.history.append(history)

        #  접수: 신규 주문 > 접수 ;--> 주문번호, 주문 정상 처리
        elif conflags == "접수":
            if self.orderStatus == OrderStatus.newOrder:
                self.ordernum = ordernum  # 주문번호 업데이트
                self.remainAmount = amount  # 주문 후 미체결 수량
                self.orderStatus = OrderStatus.orderConfirm

                # for debug
                history = orderHistoryData()
                history.sethistory(conflags, code, price, amount, 0, ordernum, "신규 매수")
                self.history.append(history)
                history.printhistory()

        #  확인: 정정/취소 주문 > 확인 ;--> 정정/취소 주문 정상 처리 확인
        elif conflags == "확인":
            etc = ""
            if self.orderStatus == OrderStatus.modifyOrder:  # 정정 확인
                self.ordernum = ordernum  # 주문번호 업데이트
                self.orderStatus = OrderStatus.orderConfirm
                etc = "정정확인"
            elif self.orderStatus == OrderStatus.cancelOrder:  # 취소 확인
                self.initOrder()
                etc = "취소확인"

            # for debug
            history = orderHistoryData()
            print(code, price)
            print(self.remainAmount, ordernum)
            history.sethistory(conflags, code, price, self.remainAmount, 0, ordernum, etc)
            self.history.append(history)
            history.printhistory()

        # 거부: 정정/취소 주문 > 거부 ;--> 정정/취소 주문 거부, 정정/취소 불가
        elif conflags == "거부":
            if self.orderStatus == OrderStatus.modifyOrder or self.orderStatus == OrderStatus.cancelOrder:
                print("주문거부 발생, 반드시 확인 필요")
                self.orderStatus = OrderStatus.newOrder  # 주문 상태를 이전으로 돌림

            # for debug
            history = orderHistoryData()
            history.sethistory(conflags, code, price, amount, 0, ordernum, "")
            self.history.append(history)
            history.printhistory()


class OrderDlg(QDialog):

    def __init__(self, obj_order):

        super(OrderDlg, self).__init__()
        self.ui = uic.loadUi('order.ui', self)
        self.ui.show()
        self.pushOrder.clicked.connect(self.ordered)
        self.pushClose.clicked.connect(self.closed)
        self.db = db.DB()
        self.master_df = self.db.get_master(where="where section='10'")
        names = self.master_df.name.tolist()
        self.comboProduct.addItems(names)
        self.obj_order = obj_order
        print(self.master_df)

    def ordered(self):
        idx_prod = self.comboProduct.currentIndex()
        prod_code = self.master_df.code[idx_prod]
        price = self.linePrice.text()
        qty = self.lineQty.text()
        try:
            i_price = int(price)
        except:
            print('price must be integer number')
            return False
        try:
            i_qty = int(qty)
        except:
            print('qty must be integer number')
            return False

        if self.radioBuy.isChecked():
            buy_sell = '2'
        elif self.radioSell.isChecked():
            buy_sell = '1'
        else:
            print('not selected')
        self.obj_order.send_order('78229074801', prod_code, buy_sell, i_qty, i_price)

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