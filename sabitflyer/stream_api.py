# -*- coding: utf-8 -*-
from enum import Enum
import json
import websocket

class stream_api(object):
    '''
    Realtime API for Bitflayer by JSON-RPC 2.0 over WebSocket

    *** The description of callback ***
    on_message and on_close are normal callbacks from websocket.
    on_message_board, on_message_board_snapshot, on_message_ticker
    and on_message_executions are special callbacks created
    by parsing message.
    '''

    WS_URL = 'wss://ws.lightstream.bitflyer.com/json-rpc'

    class enum_pair(Enum):
        BTC_JPY = 'BTC_JPY'
        FX_BTC_JPY = 'FX_BTC_JPY'

    class enum_channel(Enum):
        board_snapshot = 'lightning_board_snapshot_'
        board = 'lightning_board_'
        ticker = 'lightning_ticker_'
        executions = 'lightning_executions_'

    class data_board(object):
        '''board data class for callback'''
        def __init__(self, msg):
            self.mid_price = msg['mid_price']
            self.bids = msg['bids']
            self.asks = msg['asks']

    class data_ticker(object):
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

    class data_execution(object):
        '''executions data class for callback'''
        def __init__(self, msg):
            self.id = msg['id']
            self.side = msg['side']
            self.price = msg['price']
            self.size = msg['size']
            self.exec_date = msg['exec_date']
            self.buy_child_order_acceptance_id = msg['buy_child_order_acceptance_id']
            self.sell_child_order_acceptance_id = msg['sell_child_order_acceptance_id']

    def __init__(self, pair, channels, \
                    on_message=None,  \
                    on_message_board=None,  \
                    on_message_board_snapshot=None,  \
                    on_message_ticker=None,  \
                    on_message_executions=None, \
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
        for ch in channels:
            self.listen_channels.append(ch.value + pair.value)

        # websocket
        self.__ws = None

    def __ws_on_open(self, ws):
        for channel in self.listen_channels:
            ws.send(json.dumps({"method": "subscribe", "params": {"channel": channel}}))
    
    def __ws_on_message(self, ws, message):
        rcv_msg = json.loads(message)
        if rcv_msg["method"] != "channelMessage":
            return

        # parse message
        parsed_prms = rcv_msg["params"]
        parsed_channel = parsed_prms["channel"]
        parsed_message = parsed_prms["message"]

        # normal callback
        self.__callback(self.__cb_on_message, parsed_channel, parsed_message)

        # special callback
        if self.enum_channel.board_snapshot.value in parsed_channel:
            self.__ws_on_message_board_snapshot(parsed_message)
        elif self.enum_channel.board.value in parsed_channel:
            self.__ws_on_message_board(parsed_message)
        elif self.enum_channel.ticker.value in parsed_channel:
            self.__ws_on_message_ticker(parsed_message)
        elif self.enum_channel.executions.value in parsed_channel:
            self.__ws_on_message_executions(parsed_message)
        else:
            pass

    def __ws_on_message_board_snapshot(self, parsed_message):
        data = self.data_board(parsed_message)
        self.__callback(self.__cb_on_message_board_snapshot, data)

    def __ws_on_message_board(self, parsed_message):
        data = self.data_board(parsed_message)
        self.__callback(self.__cb_on_message_board, data)

    def __ws_on_message_ticker(self, parsed_message):
        data = self.data_ticker(parsed_message)
        self.__callback(self.__cb_on_message_ticker, data)

    def __ws_on_message_executions(self, parsed_message):
        data_list = []
        for execution in parsed_message:
            data = self.data_execution(execution)
            data_list.append(data)
        self.__callback(self.__cb_on_message_executions, data_list)

    def __ws_on_close(self, ws, *close_args):
        self.__callback(self.__cb_on_close, *close_args)

    def __callback(self, callback, *args):
        if callback:
            try:
                callback(self, *args)
            except:
                import traceback
                traceback.print_exc()

    def start(self):
        if self.__ws is not None:
            self.stop()

        self.__ws = websocket.WebSocketApp(self.WS_URL,
                                            on_message = self.__ws_on_message,
                                            on_open = self.__ws_on_open,
                                            on_close = self.__ws_on_close)
        self.__ws.run_forever()
    
    def stop(self):
        self.__ws.close()
        self.__ws = None
