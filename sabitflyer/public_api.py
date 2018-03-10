import requests
from .common import error_parser

class public_api(object):

    def __init__(self):
        self.__endpoint = "https://api.bitflyer.jp"

    def _query(self, query_url):
        response = requests.get(query_url)
        return error_parser(response.json())

    def get_depth(self, pair='BTC_JPY'):
        ''' 板情報を取得 '''
        path = '/v1/board'
        query = '?product_code=' + pair
        return self._query(self.__endpoint + path + query)