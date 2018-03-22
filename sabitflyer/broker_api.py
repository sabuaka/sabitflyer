from enum import Enum
from .public_api import public_api

class broker_api(object):

    class enum_health(Enum):
        normal = 'NORMAL'           # 取引所は稼動しています。
        busy = 'BUSY'               # 取引所に負荷がかかっている状態です。
        very_busy = 'VERY BUSY'     # 取引所の負荷が大きい状態です。
        super_busy = 'SUPER BUSY'   # 負荷が非常に大きい状態です。発注は失敗するか、遅れて処理される可能性があります。
        no_order = 'NO ORDER'       # 発注が受付できない状態です。
        stop = 'STOP'               # 取引所は停止しています。発注は受付されません。

    class enum_state(Enum):
        running = 'RUNNING'             # 通常稼働中
        closed = 'CLOSED'               # 取引停止中
        starting = 'STARTING'           # 再起動中
        preopen = 'PREOPEN'             # 板寄せ中
        circuit_break = 'CIRCUIT BREAK' # サーキットブレイク発動中
        awaiting_sq ='AWAITING SQ'      # Lightning Futures の取引終了後 SQ（清算値）の確定前
        matured = 'MATURED'             # Lightning Futures の満期に到達

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

    def get_depth(self, pair):
        ''' 板情報の取得 '''
        result = False
        res_dct = None
        try:
            res_dct = public_api().get_depth(pair)
            result = True             
        except:
            result = False
            res_dct = None
        return result, res_dct

    def get_ticker(self, pair):
        '''Tickerの取得'''
        result = False
        res_dct = None
        try:
            res_dct = public_api().get_ticker(pair)
            result = True             
        except:
            result = False
            res_dct = None
        return result, res_dct

    def get_executions(self, pair):
        ''' 約定履歴の取得 '''
        result = False
        res_dct = None
        try:
            res_dct = public_api().get_executions(pair)
            result = True             
        except:
            result = False
            res_dct = None
        return result, res_dct

    def get_boardstate(self, pair):
        ''' 板の状態の取得 '''
        result = False
        res_dct = None
        health = broker_api.enum_health.stop
        state = broker_api.enum_state.closed
        try:
            res_dct = public_api().get_boardstate(pair)
            health = res_dct['health']
            state = res_dct['state']
            result = True             
        except:
            result = False
            res_dct = None
        return result, health, state

    def get_health(self, pair):
        ''' 取引所の状態の取得 '''
        result = False
        res_dct = None
        health = broker_api.enum_health.stop
        try:
            res_dct = public_api().get_health(pair)
            health = res_dct['status']
            result = True             
        except:
            result = False
            res_dct = None
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