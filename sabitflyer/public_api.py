import requests
from .common import error_parser

class public_api(object):

    def __init__(self):
        self.__api_endpoint = "https://api.bitflyer.jp"

    def __query(self, query_url):

        response = requests.get(query_url)
        return error_parser(response)

    def get_markets(self):
        '''マーケットの一覧取得'''
        path = '/v1/getmarkets'
        query = ''
        return self.__query(self.__api_endpoint + path + query)    

    def get_depth(self, pair='BTC_JPY'):
        ''' 板情報の取得 '''
        path = '/v1/getboard'
        query = '?product_code=' + pair
        return self.__query(self.__api_endpoint + path + query)
    
    def get_ticker(self, pair='BTC_JPY'):
        '''Tickerの取得'''
        path = '/v1/getticker'
        query = '?product_code=' + pair
        return self.__query(self.__api_endpoint + path + query)

    def get_executions(self, pair='BTC_JPY'):
        ''' 約定履歴の取得 '''
        path = '/v1/getexecutions'
        query = '?product_code=' + pair
        return self.__query(self.__api_endpoint + path + query)

    def get_boardstate(self, pair='BTC_JPY'):
        ''' 板の状態の取得 '''
        path = '/v1/getboardstate'
        query = '?product_code=' + pair
        return self.__query(self.__api_endpoint + path + query)

    def get_health(self, pair='BTC_JPY'):
        ''' 取引所の状態の取得 '''
        path = '/v1/gethealth'
        query = '?product_code=' + pair
        return self.__query(self.__api_endpoint + path + query)

    def get_chats(self):
        ''' チャットの取得 '''
        path = '/v1/getchats'
        query = ''
        return self.__query(self.__api_endpoint + path + query)
