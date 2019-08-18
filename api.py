import win32com.client


class CreonAPI:

    obj_code_mgr = None
    obj_cp_cybos = None
    obj_cp_trade = None
    obj_future_mgr = None
    obj_stock_week = None
    obj_stock_mst = None
    obj_stock_cur = None
    obj_stock_order = None

    @classmethod
    def set_api(cls):
        cls.obj_code_mgr = win32com.client.Dispatch('CpUtil.CpCodeMgr')
        cls.obj_cp_cybos = win32com.client.Dispatch('CpUtil.CpCybos')
        cls.obj_cp_trade = win32com.client.Dispatch('CpTrade.CpTdUtil')
        cls.obj_future_mgr = win32com.client.Dispatch("CpUtil.CpFutureCode")
        cls.obj_stock_week = win32com.client.Dispatch("DsCbo1.StockWeek")
        cls.obj_stock_mst = win32com.client.Dispatch("DsCbo1.StockMst")
        cls.obj_stock_cur = win32com.client.Dispatch("DsCbo1.StockCur")
        cls.obj_stock_order = win32com.client.Dispatch("CpTrade.CpTd0311")



