# -*- coding: utf-8 -*-
'''取引所アクセスモジュール for FX'''
from enum import Enum
from .common import n2d
from .broker import BrokerAPI


class BrokerFXAPI(BrokerAPI):
    '''取引所アクセス仮想APIクラスfor 証拠金取引'''

    class Asset(Enum):  # override
        '''(override)enumeration of asset'''
        BTC = 'BTC'
        JPY = 'JPY'

    class TradePair(Enum):  # override
        '''enumeration of trade pair'''
        FX_BTC_JPY = 'FX_BTC_JPY'

    # -------------------------------------------------------------------------
    # Private API
    # -------------------------------------------------------------------------
    class MarginTradingInfo(object):
        '''margin trading information'''
        margin_deposit = None   # 預入証拠金(JPY)
        required_margin = None  # 必要証拠金(JPY)
        margin_rate = None      # 証拠金維持率(%)
        profit_loss = None      # 損益(JPY)

        def __init__(self, info=None):
            if info is not None:
                self.margin_deposit = n2d(info['collateral'])
                self.required_margin = n2d(info['require_collateral'])
                self.margin_rate = n2d(info['keep_rate'])
                self.profit_loss = n2d(info['open_position_pnl'])

        def out_shell(self):
            '''Display information to shell'''
            print('margin_deposit=%s' % str(self.margin_deposit))
            print('required_margin=%s' % str(self.required_margin))
            print('margin_rate=%s' % str(self.margin_rate))
            print('profit_loss=%s' % str(self.profit_loss))

    def get_margin_trading(self):
        '''証拠金の状態を取得'''
        result = False
        rtn_mti = None
        try:
            res_cll = self.prv_api.get_getcollateral()
            rtn_mti = self.MarginTradingInfo(res_cll)
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            rtn_mti = None
        return result, rtn_mti

    def get_assets(self):
        '''資産残高を取得(PrivateAPI使用回数: 1 + pair数分 回)'''
        result = False
        rtn_assets = {}
        try:
            # JPY(証拠金残高)を取得する
            res_collateral = self.prv_api.get_getcollateral()
            asset_jpy = self.AssetInfo()
            asset_jpy.name = self.Asset.JPY.value
            asset_jpy.onhand_amount = n2d(res_collateral['collateral'])  # 預託証拠金
            wk_req_amount = n2d(res_collateral['require_collateral'])    # 必要証拠金
            asset_jpy.free_amount = asset_jpy.onhand_amount - wk_req_amount
            rtn_assets[asset_jpy.name] = asset_jpy

            # 仮想通貨(建玉)を取得する
            for pair in self.TradePair:
                res_posiotns = self.prv_api.get_getpositions(pair.value)
                for position in res_posiotns:
                    # 通貨名の取得
                    name = position['product_code'].split('_')[1]
                    # 保持量の取得(ショートポジションの場合は-とする)
                    amount = n2d(position['size'])
                    if position['side'] == 'SELL':
                        amount = amount * n2d(-1)
                    # 資産情報の生成
                    if name not in rtn_assets:
                        asset_vc = self.AssetInfo()
                        asset_vc.name = name
                        asset_vc.onhand_amount = amount
                        asset_vc.free_amount = amount
                    else:
                        asset_vc = rtn_assets[name]
                        asset_vc.name = name
                        asset_vc.onhand_amount += amount
                        asset_vc.free_amount += amount
                    rtn_assets[asset_vc.name] = asset_vc

            # 生成されなかった資産情報を擬似的に生成する
            for asset in self.Asset:
                if asset.value not in rtn_assets:
                    asset_vc = self.AssetInfo()
                    asset_vc.name = asset.value
                    asset_vc.onhand_amount = n2d(0)
                    asset_vc.free_amount = n2d(0)
                    rtn_assets[asset_vc.name] = asset_vc

            result = True

        except:     # pylint: disable-msg=W0702
            result = False
            rtn_assets = None
        return result, rtn_assets

    def get_positions(self):
        '''建玉の一覧を取得'''
        result = False
        res_dct = None
        try:
            res_dct = self.prv_api.get_getpositions(self.trade_pair)
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            res_dct = None
        return result, res_dct
