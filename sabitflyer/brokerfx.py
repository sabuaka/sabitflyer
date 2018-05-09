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
        customer_margin = None      # 委託者証拠金(JPY)
        maintenance_margin = None   # 維持証拠金(JPY)
        margin_rate = None          # 証拠金維持率(%)
        profit_loss = None          # 損益(JPY)

    def get_margin_trading(self):
        '''証拠金の状態を取得'''
        result = False
        rtn_i_mt = None
        try:
            res_cll = self.prv_api.get_getcollateral()
            rtn_i_mt = self.MarginTradingInfo()
            rtn_i_mt.customer_margin = n2d(res_cll['collateral'])
            rtn_i_mt.maintenance_margin = n2d(res_cll['require_collateral'])
            rtn_i_mt.margin_rate = n2d(res_cll['keep_rate'])
            rtn_i_mt.profit_loss = n2d(res_cll['open_position_pnl'])
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            rtn_i_mt = None
        return result, rtn_i_mt

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
