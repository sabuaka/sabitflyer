# -*- coding: utf-8 -*-
'''public API module'''

import requests
from .common import error_parser


class PublicAPI(object):
    '''public API class'''

    def __init__(self, *, timeout=None):
        self.__api_endpoint = "https://api.bitflyer.com"
        self.__timeout = timeout

    def __query(self, query_url):
        '''query'''
        response = requests.get(query_url, timeout=self.__timeout)
        return error_parser(response)

    def get_by_url(self, url):
        '''get by URL(include endpoint)'''
        return self.__query(url)

    def get_markets(self):
        '''マーケットの一覧取得'''
        path = '/v1/getmarkets'
        query = ''
        return self.__query(self.__api_endpoint + path + query)

    def get_depth(self, pair):
        ''' 板情報の取得 '''
        path = '/v1/getboard'
        query = '?product_code=' + pair
        return self.__query(self.__api_endpoint + path + query)

    def get_ticker(self, pair):
        '''Tickerの取得'''
        path = '/v1/getticker'
        query = '?product_code=' + pair
        return self.__query(self.__api_endpoint + path + query)

    def get_executions(self, pair):
        ''' 約定履歴の取得 '''
        path = '/v1/getexecutions'
        query = '?product_code=' + pair
        return self.__query(self.__api_endpoint + path + query)

    def get_boardstate(self, pair):
        ''' 板の状態の取得 '''
        path = '/v1/getboardstate'
        query = '?product_code=' + pair
        return self.__query(self.__api_endpoint + path + query)

    def get_health(self, pair):
        ''' 取引所の状態の取得 '''
        path = '/v1/gethealth'
        query = '?product_code=' + pair
        return self.__query(self.__api_endpoint + path + query)

    def get_chats(self):
        ''' チャットの取得 '''
        path = '/v1/getchats'
        query = ''
        return self.__query(self.__api_endpoint + path + query)
