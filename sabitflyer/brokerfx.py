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
    def get_margin_trading(self):
        '''証拠金の状態を取得'''
        result = False
        rtn_mti = None
        try:
            res_cll = self.prv_api.get_getcollateral()
            rtn_mti = MarginTradingInfo(res_cll)
            result = True
        except:     # pylint: disable-msg=W0702
            result = False
            rtn_mti = None
        return result, rtn_mti

    def get_positions(self):
        '''Get open positions'''
        result = False
        rtn_pi_list = []
        rtn_ave_price = n2d(0)
        rtn_total_amount = n2d(0)
        try:
            res_postions = self.prv_api.get_getpositions(self.trade_pair)
            ave_divisor = n2d(0)
            for pos in res_postions:
                pi = PositionInfo(pos)
                rtn_pi_list.append(pi)
                rtn_total_amount += pi.amount
                ave_divisor = ave_divisor + (pi.price * pi.amount)
            if rtn_total_amount > 0:
                rtn_ave_price = ave_divisor / rtn_total_amount
            result = True
        except:
            result = False
            rtn_pi_list = None
            rtn_ave_price = None
            rtn_total_amount = None
        return result, rtn_pi_list, rtn_ave_price, rtn_total_amount

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


class PositionInfo(object):
    '''Position information'''
    pair = None
    side = None
    price = None
    amount = None
    commission = None
    swap = None
    required_margin = None
    open_date = None
    leverage = None
    profit_loss = None
    sfd = None

    def __init__(self, info=None):
        if info is not None:
            self.pair = info['product_code']
            self.side = BrokerAPI.str2side(info['side'])
            self.price = n2d(info['price'])
            self.amount = n2d(info['size'])
            self.commission = n2d(info['commission'])
            self.swap = n2d(info['swap_point_accumulate'])
            self.required_margin = n2d(info['require_collateral'])
            self.open_date = BrokerAPI.str2dt(info['open_date'])
            self.leverage = n2d(info['leverage'])
            self.profit_loss = n2d(info['pnl'])
            self.sfd = n2d(info['sfd'])

    def out_shell(self):
        '''Display information to shell'''
        print('pair=%s' % str(self.pair))
        print('side=%s' % str(self.side))
        print('price=%s' % str(self.price))
        print('amount=%s' % str(self.amount))
        print('commission=%s' % str(self.commission))
        print('swap=%s' % str(self.swap))
        print('required_margin=%s' % str(self.required_margin))
        print('open_date=%s' % str(self.open_date))
        print('leverage=%s' % str(self.leverage))
        print('profit_loss=%s' % str(self.profit_loss))
        print('sfd=%s' % str(self.sfd))
