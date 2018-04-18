# -*- coding: utf-8 -*-
import os
from decimal import Decimal
from enum import Enum
from .common import get_dt_short, get_dt_long
from .public_api import public_api
from .private_api import private_api

class broker_api(object):
    '''取引所アクセスモジュール'''

    class enum_asset(Enum):
        LTC = 'LTC'
        BCH = 'BCH'
        BTC = 'BCH'
        MONA = 'MONA'
        LSK = 'LSK'
        ETC = 'ETC'
        JPY = 'JPY'
        ETH = 'ETH'
        
    class enum_pair(Enum):
        BTC_JPY = 'BTC_JPY'

    class enum_side(Enum):
        BUY = 'BUY'
        SELL = 'SELL'

    class enum_order_type(Enum):
        LIMIT = 'LIMIT'
        MARKET = 'MARKET'
    
    class enum_order_status(Enum):
        UNFILLED = 'ACTIVE'                     # 注文中
        PARTIALLY_FILLED = 'ACTIVE'             # 注文中(一部約定)
        FULLY_FILLED = 'COMPLETED'              # 約定済み
        CANCELED_UNFILLED = 'CANCELED'          # 取消済(EXPIRED,REJECTED含む)
        CANCELED_PARTIALLY_FILLED = 'CANCELED'  # 取消済(一部約定)

    class enum_health_status(Enum):
        normal = 'NORMAL'           # 取引所は稼動しています。
        busy = 'BUSY'               # 取引所に負荷がかかっている状態です。
        very_busy = 'VERY BUSY'     # 取引所の負荷が大きい状態です。
        super_busy = 'SUPER BUSY'   # 負荷が非常に大きい状態です。発注は失敗するか、遅れて処理される可能性があります。
        no_order = 'NO ORDER'       # 発注が受付できない状態です。
        stop = 'STOP'               # 取引所は停止しています。発注は受付されません。

    class enum_state_status(Enum):
        running = 'RUNNING'             # 通常稼働中
        closed = 'CLOSED'               # 取引停止中
        starting = 'STARTING'           # 再起動中
        preopen = 'PREOPEN'             # 板寄せ中
        circuit_break = 'CIRCUIT BREAK' # サーキットブレイク発動中
        awaiting_sq ='AWAITING SQ'      # Lightning Futures の取引終了後 SQ（清算値）の確定前
        matured = 'MATURED'             # Lightning Futures の満期に到達

    class enum_event_log(Enum):
        order_buy_market = 'ORDER_BUY_MARKET'
        order_buy_limit = 'ORDER_BUY_LIMIT'
        order_sell_market = 'ORDER_SELL_MARKET'
        order_sell_limit = 'ORDER_SELL_LIMIT'
        order_cancel = 'ORDER_CANCEL'

    def __init__(self, pair, key, secret, log=True):
        """イニシャライザ"""
        self.broker_name = 'bitflayer'
        self.__trade_pair = pair.value

        self.__api_key = key
        self.__api_secret = secret
        self.__prv_api = private_api(self.__api_key, self.__api_secret)
        self.__log = log

        if self.__log:
            log_dir = './log/' + self.broker_name + '/'
            if os.path.exists(log_dir) != True:
                os.makedirs(log_dir)
            self.__log_path = log_dir + get_dt_short() + '_order_' + self.broker_name + '_' + self.__trade_pair +'.csv'
            with open(self.__log_path, 'w') as flog:
                header = 'date time, event, order id, price, amount, success, facility\n'
                flog.writelines(header)

    def __logging_event(self, event, order_id, price, anount, success, facility):
        '''イベント保存'''
        if self.__log:
            wstr = get_dt_long() + ',' \
                    + str(event.value) + ',' \
                    + str(order_id) + ',' \
                    + str(price) + ',' \
                    + str(anount) + ',' \
                    + str(success) + ',' \
                    + str(facility) + '\n'

            with open(self.__log_path, 'a') as flog:
                flog.writelines(wstr)

    # -------------------------------------------------------------------------
    # Private API
    # -------------------------------------------------------------------------
    @property
    def prv_api(self):
        return self.__prv_api
    @property
    def trade_pair(self):
        return self.__trade_pair

    class asset_info:
        '''資産情報'''
        name = None
        onhand_amount = None
        free_amount = None
        @property
        def locked_amount(self):
            if self.onhand_amount is None or self.free_amount is None:
                return None
            return self.onhand_amount - self.free_amount

    def get_assets(self):
        '''資産残高を取得'''
        result = False
        rtn_assets = {}
        try:
            res_balances = self.__prv_api.get_getbalance()
            for blance in res_balances:
                ia = self.asset_info()
                ia.name = blance['currency_code']
                ia.onhand_amount = Decimal(str(blance['amount']))
                ia.free_amount = Decimal(str(blance['available']))
                rtn_assets[ia.name] = ia
            result = True
        except:
            result = False
            rtn_assets = None
        return result, rtn_assets

    def order_buy_limit(self, price, amount):
        '''指値買い注文を出す'''
        result = False
        order_id = None
        try:
            res_order = self.prv_api.send_childorder_limit_buy(self.trade_pair, float(price), float(amount))
            order_id = res_order['child_order_acceptance_id']
            result = True
        except:
            order_id = None
            result = False

        self.__logging_event(self.enum_event_log.order_buy_limit, order_id, price, amount, result, '')

        return result, order_id
    
    def order_buy_market(self, amount):
        '''成行買い注文を出す'''
        result = False
        order_id = None
        try:
            res_order = self.prv_api.send_childorder_market_buy(self.trade_pair, float(amount))
            order_id = res_order['child_order_acceptance_id']
            result = True
        except:
            result = False
            order_id = None

        self.__logging_event(self.enum_event_log.order_buy_market, order_id, None, amount, result, '')

        return result, order_id

    def order_sell_limit(self, price, amount):
        '''指値買い注文を出す'''
        result = False
        order_id = None
        try:
            res_order = self.prv_api.send_childorder_limit_sell(self.trade_pair, float(price), float(amount))
            order_id = res_order['child_order_acceptance_id']
            result = True
        except:
            result = False
            order_id = None

        self.__logging_event(self.enum_event_log.order_sell_limit, order_id, price, amount, result, '')

        return result, order_id

    def order_sell_market(self, amount):
        '''成行売り注文を出す'''
        result = False
        order_id = None
        try:
            res_order = self.prv_api.send_childorder_market_sell(self.trade_pair, float(amount))
            order_id = res_order['child_order_acceptance_id']
            result = True
        except:
            result = False
            order_id = None

        self.__logging_event(self.enum_event_log.order_sell_market, order_id, None, amount, result, '')

        return result, order_id

    def order_cancel(self, order_id):
        '''注文をキャンセルする'''
        result = False
        try:
            self.prv_api.send_cancelchildorder(self.trade_pair, child_order_acceptance_id=order_id)
            result = True
        except:
            result = False

        self.__logging_event(self.enum_event_log.order_cancel, order_id, None, None, result, '')

        return result

    class order_info():
        order_id = None
        pair = None
        side = None
        order_type = None
        order_price = None
        order_size = None
        executed_average_price = None
        ordered_at = None
        executed_amount = None
        status = None

        @property
        def remaining_amount(self):
            if self.order_size is None or self.executed_amount is None:
                return None
            return self.order_size - self.executed_amount

    def order_check_detail(self, order_id):
        """注文状況の詳細を取得"""
        result = False
        rtn_order = None
        try:
            res_info = self.prv_api.get_childorders(self.trade_pair, child_order_acceptance_id=order_id)
            if len(res_info) > 0:
                oi = res_info[0]
                rtn_order = self.order_info()
                rtn_order.order_id = oi['child_order_acceptance_id']
                rtn_order.pair = oi['product_code']
                rtn_order.side = self.enum_side.BUY if oi['side'] == self.enum_side.BUY.value else self.enum_side.SELL
                rtn_order.order_type = self.enum_order_type.LIMIT if oi['child_order_type'] == self.enum_order_type.LIMIT.value else self.enum_order_type.MARKET
                rtn_order.order_price = Decimal(str(oi['price']))
                rtn_order.order_size = Decimal(str(oi['size']))
                rtn_order.executed_average_price = Decimal(str(oi['average_price']))
                rtn_order.ordered_at = oi['child_order_date']
                rtn_order.executed_amount = Decimal(str(oi['executed_size']))
                os = oi['child_order_state']
                if os == 'ACTIVE':
                    if rtn_order.executed_amount > 0:
                        rtn_order.status = self.enum_order_status.PARTIALLY_FILLED
                    else:
                        rtn_order.status = self.enum_order_status.UNFILLED
                elif os == 'COMPLETED':
                    rtn_order.status = self.enum_order_status.FULLY_FILLED
                elif os == 'CANCELED':
                    if rtn_order.executed_amount > 0:
                        rtn_order.status = self.enum_order_status.CANCELED_PARTIALLY_FILLED
                    else:
                        rtn_order.status = self.enum_order_status.CANCELED_UNFILLED
                else:   # EXPIRED, REJECTED
                    rtn_order.status = self.enum_order_status.CANCELED_UNFILLED
                result = True
            else:
                result = False
                rtn_order = None
        except:
            result = False
            rtn_order = None
        return result, rtn_order

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def get_markets(self):
        '''マーケットの一覧取得'''
        result = False
        res_dct = None
        try:
            res_dct = public_api().get_markets()
            result = True             
        except:
            result = False
            res_dct = None
        return result, res_dct

    def get_depth_data(self):
        ''' 板情報の取得 '''
        result = False
        res_dct = None
        try:
            res_dct = public_api().get_depth(self.trade_pair)
            result = True             
        except:
            result = False
            res_dct = None
        return result, res_dct

    def get_ticker(self):
        '''Tickerの取得'''
        result = False
        res_dct = None
        try:
            res_dct = public_api().get_ticker(self.trade_pair)
            result = True             
        except:
            result = False
            res_dct = None
        return result, res_dct

    def get_executions(self):
        ''' 約定履歴の取得 '''
        result = False
        res_dct = None
        try:
            res_dct = public_api().get_executions(self.trade_pair)
            result = True             
        except:
            result = False
            res_dct = None
        return result, res_dct

    def __cvt_status_health(self, api_text):
        rtn_health = self.enum_health_status.stop
        for obj in self.enum_health_status:
            if obj.value == api_text:
                rtn_health = obj
                break
        return rtn_health

    def __cvt_status_state(self, api_result):
        rtn_state = self.enum_state_status.closed
        for obj in self.enum_state_status:
            if obj.value == api_result:
                rtn_state = obj
                break
        return rtn_state

    def get_depth_status(self):
        ''' 板の状態の取得 '''
        result = False
        health = broker_api.enum_health_status.stop
        state = broker_api.enum_state_status.closed
        try:
            res_dct = public_api().get_boardstate(self.trade_pair)
            health = self.__cvt_status_health(res_dct['health'])
            state = self.__cvt_status_state(res_dct['state'])
            result = True             
        except:
            result = False
            health = broker_api.enum_health_status.stop
            state = broker_api.enum_state_status.closed
        return result, health, state

    def get_broker_status(self):
        ''' 取引所の状態の取得 '''
        result = False
        health = broker_api.enum_health_status.stop
        try:
            res_dct = public_api().get_health(self.trade_pair)
            health = self.__cvt_status_health(res_dct['status'])
            result = True
        except:
            result = False
            health = broker_api.enum_health_status.stop
        return result, health

    def get_chats(self):
        ''' チャットの取得 '''
        result = False
        res_dct = None
        try:
            res_dct = public_api().get_chats()
            result = True             
        except:
            result = False
            res_dct = None
        return result, res_dct