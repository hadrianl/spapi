#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 0004 11:40
# @Author  : Hadrianl 
# @File    : sp_struct.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


from ctypes import *


class SPApiOrder(Structure):
    _fields_ = [('Price', c_double),  # 价格
                ('StopLevel', c_double),  # 止损价格
                ('UpLevel', c_double),  # 上限水平
                ('UpPrice', c_double),  # 上限价格
                ('DownLevel', c_double),  # 下限水平
                ('DownPrice', c_double),  # 下限价格
                ('ExtOrderNo', c_int64),  # 外部指示
                ('IntOrderNo', c_int32),  # 用户订单编号
                ('Qty', c_int32),  # 剩下数量
                ('TradedQty', c_int32),  # 已成交数量
                ('TotalQty', c_int32),  # 订单全部数量
                ('ValidTime', c_uint32),  # 有效时间
                ('SchedTime', c_uint32),  # 预订发送时间
                ('TimeStamp', c_uint32),  # 服务器接收订单时间
                ('OrderOptions', c_ulong),  # 0=默认,1=T+1
                ('AccNo', c_char * 16),  # 用户帐号
                ('ProdCode', c_char * 16),  # 合约代号
                ('Initiator', c_char * 16),  # 下单用户
                ('Ref', c_char * 16),  # 参考
                ('Ref2', c_char * 16),  # 参考
                ('GatewayCode', c_char * 16),  # 网关
                ('C1OrderID', c_char * 40),  # 用户自定义参考
                ('BuySell', c_char),  # 买卖方向
                ('StopType', c_char),  # 止损类型
                ('OpenClose', c_char),  # 开平仓
                ('CondType', c_char),  # 订单条件类型
                ('OrderType', c_char),  # 订单类型
                ('ValidType', c_char),  # 订单有效类型
                ('Status', c_char),  # 状态
                ('DecInPrice', c_char),  # 合约小数位
                ('OrderAction', c_char),
                ('updateTime', c_uint32),
                ('updateSeqNo', c_int32)
                ]


class SPApiMMOrder(Structure):
    _fields_ = [('BidExtOrderNo', c_longlong),  # Bid(买)单外部指示
                ('AskExtOrderNo', c_longlong),  # Ask(沽)单外部指示
                ('BidAccOrderNo', c_long),  # Bid(买)单编号
                ('AskAccOrderNo', c_long),  # Ask(沽)单编号
                ('BidPrice', c_long),  # Bid(买)单价格
                ('AskPrice', c_long),  # Ask(沽)单价格
                ('BidQty', c_long),  # Bid(买)单数量
                ('AskQty', c_long),  # Ask(沽)单数量
                ('SpecTime', c_long),  # 预订发送时间
                ('OrderOptions', c_ulong),  # 0=默认,1=T+1
                ('ProdCode', c_char * 16),  # 合约代号
                ('AccNp', c_char * 16),  # 用户帐号
                ('C1OrderId', c_char * 40),  # 用户自定义参考
                ('OrigC1OrderId', c_char * 40),  # 旧用户自定义参考
                ('OrderType', c_char),  # 订单类型
                ('ValidType', c_char),  # 订单有效类型
                ('DecInPrice', c_char)  # 合约小数位
                ]


class SPApiPos(Structure):
    _fields_ = [('Qty', c_int32),  # 上日仓位
                ('DepQty', c_int32),  # 存储仓位
                ('LongQty', c_int32),  # 今日长仓
                ('ShortQty', c_int32),  # 今日短仓
                ('TotalAmt', c_double),  # 上日成交
                ('DepTotalAmt', c_double),  # 上日存储持仓总数(存储数量价格总和)
                ('LongTotalAmt', c_double),  # 今日长仓总数(长仓数量价格总和)
                ('ShortTotalAmt', c_double),  # 今日短仓总数(短仓数量价格总和)
                ('PLBaseCcy', c_double),  # 盈亏(基本货币)
                ('PL', c_double),  # 盈亏
                ('ExchangeRate', c_double),  # 汇率
                ('AccNo', c_char * 16),  # 用户帐号
                ('ProdCode', c_char * 16),  # 合约代码
                ('LongShort', c_char),  # 上日持仓长短方向
                ('DecInPrice', c_char),  # 合约小数点
                ]


class SPApiTrade(Structure):
    _fields_ = [('RecNO', c_double),  # 成交记录
                ('Price', c_double),  # 成交价格
                ('AvgPrice', c_double),  # 成交均价
                ('TradeNo', c_longlong),  # 成交编号
                ('ExtOrderNo', c_longlong),  # 外部指示
                ('IntOrderNo', c_int32),  # 用户订单编号
                ('Qty', c_int32),  # 成交数量
                ('TradeDate', c_uint32),  # 成交日期
                ('TradeTime', c_uint32),  # 成交时间
                ('AccNo', c_char * 16),  # 用户帐号
                ('ProdCode', c_char * 16),  # 合约代码
                ('Initiator', c_char * 16),  # 下单用户
                ('Ref', c_char * 16),  # 参考
                ('Ref2', c_char * 16),  # 参考
                ('GatewayCode', c_char * 16),  # 网关
                ('C1OrderId', c_char * 40),  # 用户自定义参考
                ('BuySell', c_char),  # 买卖方向
                ('OpenClose', c_char),  # 开平仓
                ('Status', c_char),  # 状态
                ('DecInPrice', c_char),  # 小数位
                ('OrderPrice', c_double),
                ('TradeRef', c_char * 40),
                ('TotalQty', c_int32),
                ('RemainingQty', c_int32),
                ('TradedQty', c_int32),
                ('AvgTradedPrice', c_double),
                ]


class SPApiPrice(Structure):
    _fields_ = [('Bid', c_double * 20),  # 买入价
                ('BidQty', c_int32 * 20),  # 买入量
                ('BidTicket', c_int32 * 20),  # 买指令数量
                ('Ask', c_double * 20),  # 卖出价
                ('AskQty', c_int32 * 20),  # 卖出量
                ('AskTicket', c_int32 * 20),  # 卖指令数量
                ('Last', c_double * 20),  # 成交价
                ('LastQty', c_int32 * 20),  # 成交数量
                ('LastTime', c_uint32 * 20),  # 成交时间
                ('Equil', c_double),  # 平衡价
                ('Open', c_double),
                ('High', c_double),
                ('Low', c_double),
                ('Close', c_double),
                ('CloseDate', c_uint32),  # 收市日期
                ('TurnoverVol', c_double),  # 总成交量
                ('TurnoverAmt', c_double),  # 宗成交额
                ('OpenInt', c_int32),  # 未平仓
                ('ProdCode', c_char * 16),  # 合约代码
                ('ProdName', c_char * 40),  # 合约名称
                ('DecInPrice', c_char),  # 合约小数位
                ('ExstateNo', c_int32),  # 港期市场状态
                ('TradeStateNo', c_int32),  # 市场状态
                ('Suspend', c_bool),  # 是否停牌
                ('ExpiryYMD', c_int32),  # 产品到期日期
                ('ContractYMD', c_int32),  # 合约到期日期
                ('Timestamp', c_int32)  # 行情更新时间
                ]


class SPApiInstrument(Structure):
    _fields_ = [('Margin', c_double),
                ('ContractSize', c_double),
                ('MarketCode', c_char * 16),  # 市场代码
                ('InstCode', c_char * 16),  # 产品系列代码
                ('InstName', c_char * 40),  # 英文名称
                ('InstName1', c_char * 40),  # 繁体名称
                ('InstName2', c_char * 40),  # 简体名称
                ('Ccy', c_char * 4),  # 产品系列的交易币种
                ('DecInPrice', c_char),  # 产品系列的小数位
                ('InstType', c_char),  # 产品系列的类型
                ]


class SPApiAccBal(Structure):
    _fields_ = [('CashBF', c_double),  # 上日结余
                ('TodayCash', c_double),  # 今日存取
                ('NotYetValue', c_double),  # 未交手
                ('Unpresented', c_double),  # 未兑现
                ('TodayOut', c_double),  # 提取要求
                ('Ccy', c_char * 4),  # 货币
                ]


class SPApiTicker(Structure):
    _fields_ = [('Price', c_double),  # 价格
                ('Qty', c_int32),  # 成交量
                ('TickerTime', c_uint32),  # 时间
                ('DealSrc', c_int32),  # 来源
                ('ProdCode', c_char * 16),  # 合约代码
                ('DecInPrice', c_char)  # 小数位
                ]


class SPApiAccInfo(Structure):
    _fields_ = [('NAV', c_double),  # 资产净值
                ('BuyingPower', c_double),  # 购买力
                ('CashBal', c_double),  # 现金结余
                ('MarginCall', c_double),  # 追收金额
                ('CommodityPL', c_double),  # 商品盈亏
                ('LockupAmt', c_double),  # 冻结金额
                ('CreditLimit', c_double),  # 信贷限额
                ('MaxMargin', c_double),  # 最高保证金
                ('MaxLoanLimit', c_double),  # 最高借贷上限
                ('TradingLimit', c_double),  # 信用交易额
                ('RawMargin', c_double),  # 原始保证金
                ('IMargin', c_double),  # 基本保证金
                ('MMargin', c_double),  # 维持保证金
                ('TodayTrans', c_double),  # 交易金额
                ('LoanLimit', c_double),  # 证券可按总值
                ('TotalFee', c_double),   # 费用总额
                ('LoanToMR', c_double),  # 借贷/可按值%
                ('LoanToMv', c_double),  # 借贷/市值%
                ('AccName', c_char * 16),  # 名称
                ('BaseCcy', c_char * 4),  # 基本币种
                ('MarginClass', c_char * 16),  # 保证金类别
                ('TradeClass', c_char * 16),  # 交易额别
                ('ClientId', c_char * 16),  # 客户
                ('AEId', c_char * 16),  # 经纪
                ('AccType', c_char),  # 户口类别
                ('CtrlLevel', c_char),  # 控制级数
                ('Active', c_char),  # 生效
                ('MarginPeriod', c_char)  # 时段
                ]


class SPApiProduct(Structure):
    _fields_ = [('ProdCode', c_char * 16),
                ('ProdType', c_char),
                ('ProdName', c_char * 40),
                ('Underlying', c_char * 16),
                ('InstCode', c_char * 16),
                ('ExpiryDate', c_uint32),
                ('CallPut', c_char),
                ('Strike', c_int32),
                ('LotSize', c_int32),
                ('ProdName1', c_char * 40),
                ('ProdName2', c_char * 40),
                ('OptStyle', c_char),
                ('TickSize', c_int32),
                ]