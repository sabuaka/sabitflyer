# -*- coding: utf-8 -*-
'''stream(realtime) API module'''

from enum import Enum
import json
import websocket


class RealtimeAPI(object):
    '''
    Realtime API for bitFlyer by JSON-RPC 2.0 over WebSocket

    *** The description of callback ***
    on_message and on_close are normal callbacks from websocket.
    on_message_board, on_message_board_snapshot, on_message_ticker
    and on_message_executions are special callbacks created
    by parsing message.
    '''

    WS_URL = 'wss://ws.lightstream.bitflyer.com/json-rpc'

    class TradePair(Enum):
        '''Trade pair'''
        BTC_JPY = 'BTC_JPY'
        FX_BTC_JPY = 'FX_BTC_JPY'

    class InfoChannel(Enum):
        '''Information Channel'''
        BOARD_SNAPSHOT = 'lightning_board_snapshot'
        BOARD = 'lightning_board'
        TICKER = 'lightning_ticker'
        EXECUTIONS = 'lightning_executions'

    class ListenChannel(Enum):
        '''Listening Channel'''
        # The channel name generation rule is channel header + trade pair.
        # for BTC_JPY
        BOARD_SNAPSHOT_BTC_JPY = 'lightning_board_snapshot_BTC_JPY'
        BOARD_BTC_JPY = 'lightning_board_BTC_JPY'
        TICKER_BTC_JPY = 'lightning_ticker_BTC_JPY'
        EXECUTIONS_BTC_JPY = 'lightning_executions_BTC_JPY'
        # for FX_BTC_JPY
        BOARD_SNAPSHOT_FX_BTC_JPY = 'lightning_board_snapshot_FX_BTC_JPY'
        BOARD_FX_BTC_JPY = 'lightning_board_FX_BTC_JPY'
        TICKER_FX_BTC_JPY = 'lightning_ticker_FX_BTC_JPY'
        EXECUTIONS_FX_BTC_JPY = 'lightning_executions_FX_BTC_JPY'

    class BoardData(object):
        '''board data class for callback'''
        def __init__(self, msg):
            self.mid_price = msg['mid_price']
            self.bids = msg['bids']
            self.asks = msg['asks']

    class TickerData(object):
        '''ticker data class for callback'''
        def __init__(self, msg):
            self.product_code = msg['product_code']
            self.timestamp = msg['timestamp']
            self.tick_id = msg['tick_id']
            self.best_bid = msg['best_bid']
            self.best_ask = msg['best_ask']
            self.best_bid_size = msg['best_bid_size']
            self.best_ask_size = msg['best_ask_size']
            self.total_bid_depth = msg['total_bid_depth']
            self.total_ask_depth = msg['total_ask_depth']
            self.ltp = msg['ltp']
            self.volume = msg['volume']
            self.volume_by_product = msg['volume_by_product']

    class ExecutionData(object):
        '''executions data class for callback'''
        def __init__(self, msg):
            self.order_id = msg['id']
            self.side = msg['side']
            self.price = msg['price']
            self.size = msg['size']
            self.exec_date = msg['exec_date']
            self.buy_child_order_acceptance_id = \
                msg['buy_child_order_acceptance_id']
            self.sell_child_order_acceptance_id = \
                msg['sell_child_order_acceptance_id']

    def __init__(self,
                 channel_list,
                 on_message=None,
                 on_message_board=None,
                 on_message_board_snapshot=None,
                 on_message_ticker=None,
                 on_message_executions=None,
                 on_close=None):

        # callback
        self.__cb_on_message = on_message
        self.__cb_on_message_board = on_message_board
        self.__cb_on_message_board_snapshot = on_message_board_snapshot
        self.__cb_on_message_ticker = on_message_ticker
        self.__cb_on_message_executions = on_message_executions
        self.__cb_on_close = on_close

        # listen channels
        self.listen_channels = []
        for channel in channel_list:
            self.listen_channels.append(channel.value)

        # websocket
        self.__ws = None

    def __ws_on_open(self, ws):  # pylint: disable-msg=C0103
        for channel in self.listen_channels:
            ws.send(json.dumps({"method": "subscribe", "params": {"channel": channel}}))

    def __parse_channel(self, channel):
        '''Separate channel name into header and pair.'''
        res_header = None
        res_pair = None
        for header in self.InfoChannel:
            if header.value + '_' in channel:
                wk_pair = channel.replace(header.value + '_', '')
                exist_pair = False
                for pair in self.TradePair:
                    if wk_pair == pair.value:
                        exist_pair = True
                        break
                if exist_pair:  # board_snapshotとboardの区別チェック
                    res_header = header.value
                    res_pair = wk_pair
                    break
        return res_header, res_pair

    def __ws_on_message(self, _, message):
        rcv_msg = json.loads(message)
        if rcv_msg["method"] != "channelMessage":
            return

        # parse message
        parsed_prms = rcv_msg["params"]
        parsed_channel = parsed_prms["channel"]
        parsed_message = parsed_prms["message"]
        parsed_ch_header, parsed_ch_pair = self.__parse_channel(parsed_channel)

        # normal callback
        self.__callback(self.__cb_on_message, parsed_ch_pair, parsed_ch_header, parsed_message)

        # special callback
        if parsed_ch_header == self.InfoChannel.BOARD_SNAPSHOT.value:
            self.__ws_on_message_board_snapshot(parsed_ch_pair, parsed_message)
        elif parsed_ch_header == self.InfoChannel.BOARD.value:
            self.__ws_on_message_board(parsed_ch_pair, parsed_message)
        elif parsed_ch_header == self.InfoChannel.TICKER.value:
            self.__ws_on_message_ticker(parsed_ch_pair, parsed_message)
        elif parsed_ch_header == self.InfoChannel.EXECUTIONS.value:
            self.__ws_on_message_executions(parsed_ch_pair, parsed_message)
        else:
            pass

    def __ws_on_message_board_snapshot(self, rcv_pair, rcv_message):
        data = self.BoardData(rcv_message)
        self.__callback(self.__cb_on_message_board_snapshot, rcv_pair, data)

    def __ws_on_message_board(self, rcv_pair, rcv_message):
        data = self.BoardData(rcv_message)
        self.__callback(self.__cb_on_message_board, rcv_pair, data)

    def __ws_on_message_ticker(self, rcv_pair, rcv_message):
        data = self.TickerData(rcv_message)
        self.__callback(self.__cb_on_message_ticker, rcv_pair, data)

    def __ws_on_message_executions(self, rcv_pair, rcv_message):
        data_list = []
        for execution in rcv_message:
            data = self.ExecutionData(execution)
            data_list.append(data)
        self.__callback(self.__cb_on_message_executions, rcv_pair, data_list)

    def __ws_on_close(self, _, *close_args):
        self.__callback(self.__cb_on_close, *close_args)

    def __callback(self, callback, *args):
        if callback:
            try:
                callback(self, *args)
            except:     # pylint: disable-msg=W0702
                import traceback
                traceback.print_exc()

    def start(self):
        '''To start listening'''
        if self.__ws is not None:
            self.stop()

        self.__ws = websocket.WebSocketApp(self.WS_URL,
                                           on_message=self.__ws_on_message,
                                           on_open=self.__ws_on_open,
                                           on_close=self.__ws_on_close)
        self.__ws.run_forever(ping_interval=30, ping_timeout=10)

    def stop(self):
        '''To stop listening'''
        self.__ws.close()
        self.__ws = None
