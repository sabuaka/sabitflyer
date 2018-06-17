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

    @staticmethod
    def str2side(str_side):
        '''Convert string to OrderSide type'''
        if str_side == BrokerAPI.OrderSide.BUY.value:
            return BrokerAPI.OrderSide.BUY
        elif str_side == BrokerAPI.OrderSide.SELL.value:
            return BrokerAPI.OrderSide.SELL
        return None

    class OrderType(Enum):
        '''enumeration of order type'''
        # normal order
        LIMIT = 'LIMIT'
        MARKET = 'MARKET'
        # special order
        SIMPLE = 'SIMPLE'
        IFD = 'IFD'
        OCO = 'OCO'
        IFDOCO = 'IFDOCO'

    @staticmethod
    def str2type(str_type):
        '''Convert string to OrderType type'''
        for ot in BrokerAPI.OrderType:
            if ot.value == str_type:
                return ot
        return None

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
        ORDER_ALL_CANCEL = 'ORDER_ALL_CANCEL'
        OCO_BUY_LIMIT_STOP = 'OCO_BUY_LIMIT_STOP'
        OCO_SELL_LIMIT_STOP = 'OCO_SELL_LIMIT_STOP'
        SPECIAL_ORDER_CANCEL = 'SPECIAL_ORDER_CANCEL'

    @staticmethod
    def str2dt(str_dt):
        '''Convert string to datetime type'''
        try:
            TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S'
            return datetime.strptime(str_dt[0:18], TIMESTAMP_FORMAT)
        except:
            return None

    def __init__(self, pair, key, secret, log=True, *, get_timeout=None, post_timeout=None):
        """イニシャライザ"""
        self.broker_name = 'bitflyer'
        self.__trade_pair = pair

        self.__api_key = key
        self.__api_secret = secret
        self.__get_timeout = get_timeout
        self.__post_timeout = post_timeout
        self.__prv_api = PrivateAPI(self.__api_key, self.__api_secret,
                                    get_timeout=self.__get_timeout,
                                    post_timeout=self.__post_timeout)

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
                header_str = ('date time'
                              ',event'
                              ',order id'
                              ',price'
                              ',amount'
                              ',success'
                              ',facility'
                              '\n')
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
                rtn_order = OrderInfo(res_infos[0])
                result = True
            else:
                result = True
                rtn_order = OrderInfo()
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
            res_dct = PublicAPI(timeout=self.__get_timeout).get_markets()
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
            res_dct = PublicAPI(timeout=self.__get_timeout).get_depth(self.trade_pair)
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
            res_dct = PublicAPI(timeout=self.__get_timeout).get_ticker(self.trade_pair)
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
            res_dct = PublicAPI(timeout=self.__get_timeout).get_executions(self.trade_pair)
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
            res_dct = PublicAPI(timeout=self.__get_timeout).get_boardstate(self.trade_pair)
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
            res_dct = PublicAPI(timeout=self.__get_timeout).get_health(self.trade_pair)
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
            res_dct = PublicAPI(timeout=self.__get_timeout).get_chats()
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            res_dct = None
        return result, res_dct

    # -------------------------------------------------------------------------
    # Private API
    # -------------------------------------------------------------------------
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

    def order_all_cancel(self):
        '''全ての注文をキャンセルする'''
        result = False
        try:
            self.prv_api.send_cancelallchildorders(self.trade_pair)
            result = True
        except:     # pylint: disable-msg=W0702
            result = False

        self.__logging_event(self.EventLog.ORDER_ALL_CANCEL, None, None, None, result, '')

    class ConditionType(Enum):
        '''特殊注文の執行条件'''
        LIMIT = 'LIMIT'             # Limit order.
        MARKET = 'MARKET'           # Market order.
        STOP = 'STOP'               # Stop order.
        STOP_LIMIT = 'STOP_LIMIT'   # Stop-limit order.
        TRAIL = 'TRAIL'             # Trailing stop order.

    def parent_aid_to_oid(self, acceptance_id):
        '''Get parent_order_id from parent_order_acceptance_id'''
        result = False
        rtn_id = None
        try:
            res_info = self.__prv_api.get_parentorder(parent_order_acceptance_id=acceptance_id)
            rtn_id = res_info['parent_order_id']
            result = True
        except:
            result = False
            rtn_id = None

        return result, rtn_id

    def so_check_details(self, parent_order_id):
        '''check special order information'''
        result = False
        rtn_orders = None
        try:
            res_infos = self.prv_api.get_childorders(self.trade_pair,
                                                     parent_order_id=parent_order_id)
            rtn_orders = []
            if len(res_infos) > 0:  # pylint: disable-msg=C1801
                for info in res_infos:
                    rtn_orders.append(OrderInfo(info))
                result = True
            else:
                result = True
                rtn_orders.append(OrderInfo())
                rtn_orders[0].order_state = self.OrderState.UNKNOWN
        except:     # pylint: disable-msg=W0702
            result = False
            rtn_orders = None
        return result, rtn_orders

    def so_mk_prms_limit(self, product_code, side, price, size) -> dict:
        '''return parameters of dicttype parent order'''
        res_dict = {
            'product_code': product_code,
            'condition_type': self.ConditionType.LIMIT.value,
            'side': side,
            'price': price,
            'size': size
        }
        return res_dict

    def so_mk_prms_stop(self, product_code, side, price, size) -> dict:
        '''return parameters of dicttype parent order'''
        res_dict = {
            'product_code': product_code,
            'condition_type': self.ConditionType.STOP.value,
            'side': side,
            'trigger_price': price,
            'size': size
        }
        return res_dict

    def so_oco_buy_limit_stop(self, o_price, s_price, amount):
        '''oco type buying order of limit and trail'''
        result = False
        order_id = None
        try:
            # make order list
            prms_order = self.so_mk_prms_limit(self.trade_pair,
                                               self.OrderSide.BUY.value,
                                               float(o_price),
                                               float(amount))
            prms_stop = self.so_mk_prms_stop(self.trade_pair,
                                             self.OrderSide.BUY.value,
                                             float(s_price),
                                             float(amount))
            parameters = [prms_order, prms_stop]

            # send order
            res_order = self.prv_api.send_parentorder(self.OrderType.OCO.value,
                                                      parameters)
            order_id = res_order['parent_order_acceptance_id']
            result = True
        except:
            result = False
            order_id = None

        self.__logging_event(self.EventLog.OCO_BUY_LIMIT_STOP,
                             order_id,
                             o_price, amount,
                             result, 'OCO1:LIMIT')
        self.__logging_event(self.EventLog.OCO_BUY_LIMIT_STOP,
                             order_id,
                             s_price, amount,
                             result, 'OCO2:STOP')

        return result, order_id

    def so_oco_sell_limit_stop(self, o_price, s_price, amount):
        '''oco type selling order of limit and trail'''
        result = False
        order_id = None
        try:
            # make order list
            prms_order = self.so_mk_prms_limit(self.trade_pair,
                                               self.OrderSide.SELL.value,
                                               float(o_price),
                                               float(amount))
            prms_stop = self.so_mk_prms_stop(self.trade_pair,
                                             self.OrderSide.SELL.value,
                                             float(s_price),
                                             float(amount))
            parameters = [prms_order, prms_stop]

            # send order
            res_order = self.prv_api.send_parentorder(self.OrderType.OCO.value,
                                                      parameters)
            order_id = res_order['parent_order_acceptance_id']
            result = True
        except:
            result = False
            order_id = None

        self.__logging_event(self.EventLog.OCO_SELL_LIMIT_STOP,
                             order_id,
                             o_price, amount,
                             result, 'OCO1:LIMIT')
        self.__logging_event(self.EventLog.OCO_SELL_LIMIT_STOP,
                             order_id,
                             s_price, amount,
                             result, 'OCO2:STOP')

        return result, order_id

    def so_cancel(self, *, parent_order_acceptance_id=None, parent_order_id=None):
        '''cancel special order'''
        result = False
        memo = None
        c_id = None
        try:
            if parent_order_acceptance_id is not None:
                c_id = parent_order_acceptance_id
                memo = 'parent_order_acceptance_id'
                self.prv_api.send_cancelparentorder(
                    self.trade_pair, parent_order_acceptance_id=parent_order_acceptance_id)
                result = True

            elif parent_order_id is not None:
                c_id = parent_order_id
                memo = 'parent_order_id'
                self.prv_api.send_cancelparentorder(
                    self.trade_pair, parent_order_id=parent_order_id)
                result = True

            else:
                result = False

        except:     # pylint: disable-msg=W0702
            result = False

        self.__logging_event(self.EventLog.SPECIAL_ORDER_CANCEL,
                             c_id,
                             None, None,
                             result, memo)

        return result


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
    outstanding_amount = None
    canceled_amount = None
    expire_date = None
    order_date = None

    @property
    def executed_actual_amount(self):
        '''[property] actual amount'''
        if self.executed_amount is None or self.executed_commission is None:
            return None
        return self.executed_amount - self.executed_commission

    def __init__(self, info=None):
        if info is not None:
            self.order_id = info['child_order_acceptance_id']
            self.order_pair = info['product_code']
            self.order_side = BrokerAPI.str2side(info['side'])
            self.order_type = BrokerAPI.str2type(info['child_order_type'])
            self.order_price = n2d(info['price'])
            self.order_amount = n2d(info['size'])
            self.executed_ave_price = n2d(info['average_price'])
            self.executed_amount = n2d(info['executed_size'])
            self.executed_commission = n2d(info['total_commission'])
            self.outstanding_amount = n2d(info['outstanding_size'])
            self.canceled_amount = n2d(info['cancel_size'])
            self.expire_date = BrokerAPI.str2dt(info['expire_date'])
            self.order_date = BrokerAPI.str2dt(info['child_order_date'])
            self.order_state = self.__analize_state(info['child_order_state'], self.executed_amount)

    @staticmethod
    def __analize_state(str_state, executed_amount):
        if str_state == 'ACTIVE':
            if executed_amount > 0:
                return BrokerAPI.OrderState.PARTIALLY_FILLED
            else:
                return BrokerAPI.OrderState.UNFILLED
        elif str_state == 'COMPLETED':
            return BrokerAPI.OrderState.FULLY_FILLED
        elif str_state == 'CANCELED':
            if executed_amount > 0:
                return BrokerAPI.OrderState.CANCELED_PARTIALLY_FILLED
            else:
                return BrokerAPI.OrderState.CANCELED_UNFILLED
        else:   # EXPIRED, REJECTED
            return BrokerAPI.OrderState.CANCELED_UNFILLED

    def out_shell(self):
        '''Display information to shell'''
        print('order_id', self.order_id, type(self.order_id))
        print('order_pair', self.order_pair, type(self.order_pair))
        print('order_side', self.order_side, type(self.order_side))
        print('order_type', self.order_type, type(self.order_type))
        print('order_state', self.order_state, type(self.order_state))
        print('order_price', self.order_price, type(self.order_price))
        print('order_amount', self.order_amount, type(self.order_amount))
        print('executed_ave_price', self.executed_ave_price, type(self.executed_ave_price))
        print('executed_amount', self.executed_amount, type(self.executed_amount))
        print('executed_commission', self.executed_commission, type(self.executed_commission))
        print('executed_actual_amount', self.executed_actual_amount,
              type(self.executed_actual_amount))
        print('outstanding_amount', self.outstanding_amount, type(self.outstanding_amount))
        print('canceled_amount', self.canceled_amount, type(self.canceled_amount))
        print('expire_date', self.expire_date, type(self.expire_date))
        print('order_date', self.order_date, type(self.order_date))
