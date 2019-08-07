from PyQt5.QtWidgets import *
from PyQt5 import uic
import db_man as db


class Order(QDialog):

    def __init__(self):

        super(Order, self).__init__()
        self.ui = uic.loadUi('order.ui', self)
        self.ui.show()
        self.pushOrder.clicked.connect(self.ordered)
        self.pushClose.clicked.connect(self.closed)
        self.db = db.DB()
        self.master_df = self.db.get_master(where="where section='10'")
        names = self.master_df.name.tolist()
        self.comboProduct.addItems(names)
        print(self.master_df)

    def ordered(self):
        print(self.linePrice.text())
        print(self.lineQty.text())
        if self.radioBuy.isChecked():
            print('buy selected')
        elif self.radioSell.isChecked():
            print('sell selected')
        else:
            print('not selected')
        print('ordered')

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