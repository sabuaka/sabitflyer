# -*- coding: utf-8 -*-
'''取引所アクセスモジュール'''
import os
from datetime import datetime
from enum import Enum, IntEnum, auto
from .common import get_dt_short, get_dt_long, n2d
from .private import PrivateAPI
from .public import PublicAPI


class BrokerAPI(object):
    '''取引所アクセス仮想APIクラス'''

    class Asset(Enum):
        '''enumeration of asset'''
        LTC = 'LTC'
        BCH = 'BCH'
        BTC = 'BCH'
        MONA = 'MONA'
        LSK = 'LSK'
        ETC = 'ETC'
        JPY = 'JPY'
        ETH = 'ETH'

    class TradePair(Enum):
        '''enumeration of trade pair'''
        BTC_JPY = 'BTC_JPY'

    class OrderSide(Enum):
        '''enumeration of trade side'''
        BUY = 'BUY'
        SELL = 'SELL'

    class OrderType(Enum):
        '''enumeration of order type'''
        LIMIT = 'LIMIT'
        MARKET = 'MARKET'

    class OrderState(IntEnum):
        '''enumeration of order state'''
        UNFILLED = auto()                   # 注文中
        PARTIALLY_FILLED = auto()           # 注文中(一部約定)
        FULLY_FILLED = auto()               # 約定済み
        CANCELED_UNFILLED = auto()          # 取消済(EXPIRED,REJECTED含む)
        CANCELED_PARTIALLY_FILLED = auto()  # 取消済(一部約定)
        UNKNOWN = auto()                    # 不明

    class HealthStatus(Enum):
        '''enumeration of health status'''
        NORMAL = 'NORMAL'           # 取引所は稼動しています。
        BUSY = 'BUSY'               # 取引所に負荷がかかっている状態です。
        VERY_BUSY = 'VERY BUSY'     # 取引所の負荷が大きい状態です。
        SUPER_BUSY = 'SUPER BUSY'   # 負荷が非常に大きい状態です。発注は失敗するか、遅れて処理される可能性があります。
        NO_ORDER = 'NO ORDER'       # 発注が受付できない状態です。
        STOP = 'STOP'               # 取引所は停止しています。発注は受付されません。

    class StateStatus(Enum):
        '''enumeration of status'''
        RUNNING = 'RUNNING'                 # 通常稼働中
        CLOSED = 'CLOSED'                   # 取引停止中
        STARTING = 'STARTING'               # 再起動中
        PREOPEN = 'PREOPEN'                 # 板寄せ中
        CIRCUIT_BREAK = 'CIRCUIT BREAK'     # サーキットブレイク発動中
        AWAITING_SQ = 'AWAITING SQ'         # LightningFuturesの取引終了後SQ（清算値）の確定前
        MATURED = 'MATURED'                 # LightningFuturesの満期に到達

    class EventLog(Enum):
        '''enumeration of status'''
        ORDER_BUY_MARKET = 'ORDER_BUY_MARKET'
        ORDER_BUY_LIMIT = 'ORDER_BUY_LIMIT'
        ORDER_SELL_MARKET = 'ORDER_SELL_MARKET'
        ORDER_SELL_LIMIT = 'ORDER_SELL_LIMIT'
        ORDER_CANCEL = 'ORDER_CANCEL'

    class OrderInfo(object):
        '''order information class'''
        order_id = None
        order_pair = None
        order_side = None
        order_type = None
        order_state = None
        order_price = None
        order_amount = None
        executed_ave_price = None
        executed_amount = None
        executed_commission = None
        canceled_amount = None
        expire_date = None
        order_date = None

        @property
        def remaining_amount(self):
            '''[property] remaining amount'''
            if self.order_amount is None or self.executed_amount is None:
                return None
            return self.order_amount - self.executed_amount

        @property
        def executed_actual_amount(self):
            '''[property] actual amount'''
            if self.executed_amount is None or self.executed_commission is None:
                return None
            return self.executed_amount - self.executed_commission

    def __init__(self, pair, key, secret, log=True):
        """イニシャライザ"""
        self.broker_name = 'bitflyer'
        self.__trade_pair = pair

        self.__api_key = key
        self.__api_secret = secret
        self.__prv_api = PrivateAPI(self.__api_key, self.__api_secret)
        self.__log = log

        if self.__log:
            log_dir = './log/' + self.broker_name + '/'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            self.__log_path = log_dir + get_dt_short() \
                                      + '_order' \
                                      + '_' + self.broker_name \
                                      + '_' + self.__trade_pair + '.csv'
            with open(self.__log_path, 'w') as flog:
                header_list = {
                    'date time',
                    'event',
                    'order id',
                    'price',
                    'amount',
                    'success',
                    'facility'
                }
                header_str = ','.join(header_list) + '\n'
                flog.writelines(header_str)

    def __logging_event(self, event,
                        order_id,
                        price, anount,
                        success,
                        facility):
        '''イベント保存'''
        if self.__log:
            wstr = (get_dt_long() + ','
                    + str(event.value) + ','
                    + str(order_id) + ','
                    + str(price) + ','
                    + str(anount) + ','
                    + str(success) + ','
                    + str(facility) + '\n')

            with open(self.__log_path, 'a') as flog:
                flog.writelines(wstr)

    def __str2side(self, str_side):
        if str_side == self.OrderSide.BUY.value:
            return self.OrderSide.BUY
        elif str_side == self.OrderSide.SELL.value:
            return self.OrderSide.SELL
        return None

    def __str2type(self, str_type):
        if str_type == self.OrderType.LIMIT.value:
            return self.OrderType.LIMIT
        elif str_type == self.OrderType.MARKET.value:
            return self.OrderType.MARKET
        return None

    def __str2dt(self, str_dt):
        try:
            TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S'
            return datetime.strptime(str_dt[0:18], TIMESTAMP_FORMAT)
        except:
            return None

    def __analize_state(self, str_state, executed_amount):
        if str_state == 'ACTIVE':
            if executed_amount > 0:
                return self.OrderState.PARTIALLY_FILLED
            else:
                return self.OrderState.UNFILLED
        elif str_state == 'COMPLETED':
            return self.OrderState.FULLY_FILLED
        elif str_state == 'CANCELED':
            if executed_amount > 0:
                return self.OrderState.CANCELED_PARTIALLY_FILLED
            else:
                return self.OrderState.CANCELED_UNFILLED
        else:   # EXPIRED, REJECTED
            return self.OrderState.CANCELED_UNFILLED

    # -------------------------------------------------------------------------
    # Private API
    # -------------------------------------------------------------------------
    @property
    def prv_api(self):
        '''[property] private api'''
        return self.__prv_api

    @property
    def trade_pair(self):
        '''[property] trade pair'''
        return self.__trade_pair

    class AssetInfo:
        '''資産情報'''
        name = None
        onhand_amount = None
        free_amount = None

        @property
        def locked_amount(self):
            '''[property] locked amount'''
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
                asset_info = self.AssetInfo()
                asset_info.name = blance['currency_code']
                asset_info.onhand_amount = n2d(blance['amount'])
                asset_info.free_amount = n2d(blance['available'])
                rtn_assets[asset_info.name] = asset_info
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            rtn_assets = None
        return result, rtn_assets

    def order_check_detail(self, order_id):
        """注文状況の詳細を取得"""
        result = False
        rtn_order = None
        try:
            res_infos = self.prv_api.get_childorders(
                self.trade_pair, child_order_acceptance_id=order_id)
            if len(res_infos) > 0:  # pylint: disable-msg=C1801
                info = res_infos[0]
                rtn_order = self.OrderInfo()
                rtn_order.order_id = info['child_order_acceptance_id']
                rtn_order.order_pair = info['product_code']
                rtn_order.order_side = self.__str2side(info['side'])
                rtn_order.order_type = self.__str2type(info['child_order_type'])
                rtn_order.order_price = n2d(info['price'])
                rtn_order.order_amount = n2d(info['size'])
                rtn_order.executed_ave_price = n2d(info['average_price'])
                rtn_order.executed_amount = n2d(info['executed_size'])
                rtn_order.executed_commission = n2d(info['total_commission'])
                rtn_order.canceled_amount = n2d(info['cancel_size'])
                rtn_order.expire_date = self.__str2dt(info['expire_date'])
                rtn_order.order_date = self.__str2dt(info['child_order_date'])
                rtn_order.order_state = self.__analize_state(info['child_order_state'],
                                                             rtn_order.executed_amount)
                result = True
            else:
                result = True
                rtn_order = self.OrderInfo()
                rtn_order.order_state = self.OrderState.UNKNOWN
        except:     # pylint: disable-msg=W0702
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
            res_dct = PublicAPI().get_markets()
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            res_dct = None
        return result, res_dct

    def get_depth_data(self):
        ''' 板情報の取得 '''
        result = False
        res_dct = None
        try:
            res_dct = PublicAPI().get_depth(self.trade_pair)
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            res_dct = None
        return result, res_dct

    def get_ticker(self):
        '''Tickerの取得'''
        result = False
        res_dct = None
        try:
            res_dct = PublicAPI().get_ticker(self.trade_pair)
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            res_dct = None
        return result, res_dct

    def get_executions(self):
        ''' 約定履歴の取得 '''
        result = False
        res_dct = None
        try:
            res_dct = PublicAPI().get_executions(self.trade_pair)
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            res_dct = None
        return result, res_dct

    def __cvt_status_health(self, api_text):
        rtn_health = self.HealthStatus.STOP
        for obj in self.HealthStatus:
            if obj.value == api_text:
                rtn_health = obj
                break
        return rtn_health

    def __cvt_status_state(self, api_result):
        rtn_state = self.StateStatus.CLOSED
        for obj in self.StateStatus:
            if obj.value == api_result:
                rtn_state = obj
                break
        return rtn_state

    def get_depth_status(self):
        ''' 板の状態の取得 '''
        result = False
        health = self.HealthStatus.STOP
        state = self.StateStatus.CLOSED
        try:
            res_dct = PublicAPI().get_boardstate(self.trade_pair)
            health = self.__cvt_status_health(res_dct['health'])
            state = self.__cvt_status_state(res_dct['state'])
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            health = self.HealthStatus.STOP
            state = self.StateStatus.CLOSED
        return result, health, state

    def get_broker_status(self):
        ''' 取引所の状態の取得 '''
        result = False
        health = self.HealthStatus.STOP
        try:
            res_dct = PublicAPI().get_health(self.trade_pair)
            health = self.__cvt_status_health(res_dct['status'])
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            health = self.HealthStatus.STOP
        return result, health

    def get_chats(self):
        ''' チャットの取得 '''
        result = False
        res_dct = None
        try:
            res_dct = PublicAPI().get_chats()
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            res_dct = None
        return result, res_dct

    def order_buy_limit(self, price, amount):
        '''指値買い注文を出す'''
        result = False
        order_id = None
        try:
            res_order = self.prv_api.send_childorder_limit_buy(self.trade_pair,
                                                               float(price),
                                                               float(amount))
            order_id = res_order['child_order_acceptance_id']
            result = True
        except:     # pylint: disable-msg=W0702
            order_id = None
            result = False

        self.__logging_event(self.EventLog.ORDER_BUY_LIMIT,
                             order_id,
                             price, amount,
                             result, '')

        return result, order_id

    def order_buy_market(self, amount):
        '''成行買い注文を出す'''
        result = False
        order_id = None
        try:
            res_order = \
                self.prv_api.send_childorder_market_buy(self.trade_pair,
                                                        float(amount))
            order_id = res_order['child_order_acceptance_id']
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            order_id = None

        self.__logging_event(self.EventLog.ORDER_BUY_MARKET,
                             order_id,
                             None, amount,
                             result, '')

        return result, order_id

    def order_sell_limit(self, price, amount):
        '''指値買い注文を出す'''
        result = False
        order_id = None
        try:
            res_order = self.prv_api.send_childorder_limit_sell(
                self.trade_pair, float(price), float(amount))
            order_id = res_order['child_order_acceptance_id']
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            order_id = None

        self.__logging_event(self.EventLog.ORDER_SELL_LIMIT,
                             order_id,
                             price, amount,
                             result, '')

        return result, order_id

    def order_sell_market(self, amount):
        '''成行売り注文を出す'''
        result = False
        order_id = None
        try:
            res_order = \
                self.prv_api.send_childorder_market_sell(self.trade_pair,
                                                         float(amount))
            order_id = res_order['child_order_acceptance_id']
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            order_id = None

        self.__logging_event(self.EventLog.ORDER_SELL_MARKET,
                             order_id,
                             None, amount,
                             result, '')

        return result, order_id

    def order_cancel(self, order_id):
        '''注文をキャンセルする'''
        result = False
        try:
            self.prv_api.send_cancelchildorder(
                self.trade_pair, child_order_acceptance_id=order_id)
            result = True
        except:     # pylint: disable-msg=W0702
            result = False

        self.__logging_event(self.EventLog.ORDER_CANCEL,
                             order_id,
                             None, None,
                             result, '')

        return result
