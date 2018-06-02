# -*- coding: utf-8 -*-
'''private API module'''
import time
import json
from urllib.parse import urlencode
from hashlib import sha256
import hmac
import requests
from .common import error_parser


class PrivateAPI(object):
    '''private API class'''

    def __init__(self, api_key, api_secret, *, get_timeout=None, post_timeout=None):
        '''イニシャライザー'''
        self.__api_endpoint = "https://api.bitflyer.jp"
        self.__api_key = api_key
        self.__api_secret = api_secret
        self.__get_timeout = get_timeout
        self.__post_timeout = post_timeout

    def __make_header(self, query_data):
        '''リクエストヘッダーの生成'''
        access_timestamp = str(time.time())
        plain_text = access_timestamp + query_data
        hmac_key = bytearray(self.__api_secret, 'utf8')
        hmac_msg = bytearray(plain_text, 'utf8')
        access_sign = hmac.new(hmac_key, hmac_msg, sha256).hexdigest()
        return {
            'ACCESS-KEY': self.__api_key,
            "ACCESS-TIMESTAMP": access_timestamp,
            "ACCESS-SIGN": access_sign,
            'Content-Type': 'application/json'
        }

    def __get_query(self, path, query_dct):
        '''GET Method'''
        query = ''
        if len(query_dct) > 0:  # pylint: disable-msg=C1801
            query = '?' + urlencode(query_dct)
        headers = self.__make_header('GET' + path + query)
        uri = self.__api_endpoint + path + query
        response = requests.get(uri, headers=headers, timeout=self.__get_timeout)
        return error_parser(response)

    def __post_query(self, path, query_dct):
        '''POST Method'''
        data = ''
        if len(query_dct) > 0:  # pylint: disable-msg=C1801
            data = json.dumps(query_dct)
        headers = self.__make_header('POST' + path + data)
        uri = self.__api_endpoint + path
        response = requests.post(uri, data=data, headers=headers, timeout=self.__post_timeout)
        return error_parser(response)

    def get_permissions(self):
        '''API キーの権限を取得'''
        path = '/v1/me/getpermissions'
        return self.__get_query(path, {})

    def get_getbalance(self):
        '''資産残高を取得'''
        path = '/v1/me/getbalance'
        return self.__get_query(path, {})

    def get_getcollateral(self):
        '''証拠金の状態を取得'''
        path = '/v1/me/getcollateral'
        return self.__get_query(path, {})

    def get_getcollateralaccounts(self):
        '''証拠金の状態を取得'''
        path = '/v1/me/getcollateralaccounts'
        return self.__get_query(path, {})

    def get_deposits(self, *, count=None, before=None, after=None):
        '''入金履歴を取得'''
        path = '/v1/me/getdeposits'
        query_dct = {}
        if count is not None:
            query_dct['count'] = count
        if before is not None:
            query_dct['before'] = before
        if after is not None:
            query_dct['after'] = after
        return self.__get_query(path, query_dct)

    def get_childorders(self, product_code, *,
                        count=None, before=None, after=None,
                        child_order_state=None,
                        child_order_id=None,
                        child_order_acceptance_id=None,
                        parent_order_id=None):
        '''注文の一覧を取得'''
        path = '/v1/me/getchildorders'
        query_dct = {'product_code': product_code}
        if count is not None:
            query_dct['count'] = count
        if before is not None:
            query_dct['before'] = before
        if after is not None:
            query_dct['after'] = after
        if child_order_state is not None:
            query_dct['child_order_state'] = child_order_state
        if child_order_id is not None:
            query_dct['child_order_id'] = child_order_id
        if child_order_acceptance_id is not None:
            query_dct['child_order_acceptance_id'] = child_order_acceptance_id
        if parent_order_id is not None:
            query_dct['parent_order_id'] = parent_order_id
        return self.__get_query(path, query_dct)

    def get_parentorders(self, product_code, *,
                         count=None, before=None, after=None,
                         parent_order_state=None):
        '''親注文の一覧を取得'''
        path = '/v1/me/getparentorders'
        query_dct = {'product_code': product_code}
        if count is not None:
            query_dct['count'] = count
        if before is not None:
            query_dct['before'] = before
        if after is not None:
            query_dct['after'] = after
        if parent_order_state is not None:
            query_dct['parent_order_state'] = parent_order_state
        return self.__get_query(path, query_dct)

    def send_childorder(self, product_code,
                        child_order_type, side,
                        price, size,
                        *, minute_to_expire=None, time_in_force=None):
        '''新規注文を出す'''
        path = '/v1/me/sendchildorder'
        query_dct = {
            'product_code': product_code,
            'child_order_type': child_order_type,
            'side': side,
            'price': price,
            'size': size
        }
        if minute_to_expire is not None:
            query_dct['minute_to_expire'] = minute_to_expire
        if time_in_force is not None:
            query_dct['time_in_force'] = time_in_force
        return self.__post_query(path, query_dct)

    def send_childorder_limit_buy(self, product_code,
                                  price, size,
                                  *,
                                  minute_to_expire=None, time_in_force=None):
        '''[EXTRA]指値買い注文を出す'''
        return self.send_childorder(product_code,
                                    'LIMIT', 'BUY',
                                    price, size,
                                    minute_to_expire=minute_to_expire,
                                    time_in_force=time_in_force)

    def send_childorder_limit_sell(self, product_code,
                                   price, size,
                                   *,
                                   minute_to_expire=None, time_in_force=None):
        '''[EXTRA]指値売り注文を出す'''
        return self.send_childorder(product_code,
                                    'LIMIT', 'SELL',
                                    price, size,
                                    minute_to_expire=minute_to_expire,
                                    time_in_force=time_in_force)

    def send_childorder_market_buy(self, product_code, size,
                                   *,
                                   minute_to_expire=None, time_in_force=None):
        '''[EXTRA]成行買い注文を出す'''
        return self.send_childorder(product_code,
                                    'MARKET', 'BUY',
                                    None, size,
                                    minute_to_expire=minute_to_expire,
                                    time_in_force=time_in_force)

    def send_childorder_market_sell(self, product_code, size,
                                    *,
                                    minute_to_expire=None, time_in_force=None):
        '''[EXTRA]成行売り注文を出す'''
        return self.send_childorder(product_code,
                                    'MARKET', 'SELL',
                                    None, size,
                                    minute_to_expire=minute_to_expire,
                                    time_in_force=time_in_force)

    def send_cancelchildorder(self, product_code,
                              *,
                              child_order_acceptance_id=None,
                              child_order_id=None):
        '''注文をキャンセルする'''
        path = '/v1/me/cancelchildorder'
        query_dct = {'product_code': product_code}
        if child_order_acceptance_id is not None:
            query_dct['child_order_acceptance_id'] = child_order_acceptance_id
        if child_order_id is not None:
            query_dct['child_order_id'] = child_order_id
        return self.__post_query(path, query_dct)

    def send_cancelchildorder_acceptance_id(self, product_code,         # pylint: disable-msg=C0103
                                            child_order_acceptance_id):
        '''[EXTRA]child_order_acceptance_idで指定した注文をキャンセルする'''
        return self.send_cancelchildorder(
            product_code,
            child_order_acceptance_id=child_order_acceptance_id)

    def send_cancelchildorder_id(self, product_code, child_order_id):
        '''[EXTRA]child_order_idで指定した注文をキャンセルする'''
        return self.send_cancelchildorder(
            product_code,
            child_order_id=child_order_id)

    def get_getpositions(self, product_code):
        '''建玉の一覧を取得'''
        path = '/v1/me/getpositions'
        query_dct = {'product_code': product_code}
        return self.__get_query(path, query_dct)
