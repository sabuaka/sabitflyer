# -*- coding: utf-8 -*-
'''共通ロジックモジュール'''

import datetime
from decimal import Decimal

def error_parser(response):
    '''エラーパーサー(エラー発生時は例外を発生させます)'''
    try:
        res_json = response.json()
    except:
        res_json = None

    if response.status_code == 200:  # OK
        return res_json
    else:
        if res_json is not None:
            raise Exception(res_json)
        else:
            errmsg = str('レスポンスを取得できませんでした。')
            raise Exception(errmsg)

    return None

def get_dt_short():
    """現在の日時を文字列(YYYYMMDDHHMMSS)で返す"""
    return datetime.datetime.now().strftime('%Y%m%d%H%M')

def get_dt_long():
    """現在の日時を文字列(YYYY/MM/DD HH/MM/SS.f)で返す"""
    return datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S.%f')

def n2d(value) -> Decimal:
    '''数値(int,float)をDecimal型へ変換'''
    return Decimal(str(value))

