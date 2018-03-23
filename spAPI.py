#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 0004 10:02
# @Author  : Hadrianl 
# @File    : spAPI.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import logging.config

from sp_struct import *
from conf.util import *

spdll = cdll.LoadLibrary(r'dll\spapidllm64.dll')
logging.config.fileConfig(r'conf\sp_log.conf')
api_logger = logging.getLogger('root.sp_api')


def initialize():
    """
    API初始化
    :return: 0代表成功
    """
    ret = spdll.SPAPI_Initialize()
    if ret == 0:
        api_logger.info('初始化成功')
    else:
        api_logger.error(f'初始化失败,errcode:{ret}')
    return ret


def unintialize():
    """
    释放API
    :return:0, 代表成功.
            -1, 用户未登出
            -2，释放异常
    """
    ret = spdll.SPAPI_Uninitialize()
    if ret == 0:
        api_logger.info('释放API成功')
    else:
        api_logger.error(f'释放API失败,errcode:{ret},err:{RET_CODE_MSG_UNINIT[ret]}')
    return ret


def set_language(langid: int):
    """
    设定服务器返回信息的字体.此方法在 SPAPI_Initialize 前使用,如不使用,返回字体默
    认为 0:英文。
    :param langid:0:英  1:繁  2:简
    :return:0:表示请求成功
    """
    ret = spdll.SPAPI_SetLanguageId(c_int(langid))
    if ret == 0:
        api_logger.info('设置语言成功')
    else:
        api_logger.error(f'设置语言失败,errcode:{ret}')
    return ret


c_char_p_host = c_char_p()
c_char_p_license = c_char_p()
c_char_p_app_id = c_char_p()
c_char_p_user_id = c_char_p()
c_char_p_password = c_char_p()


def set_login_info(host, port, License, app_id, user_id, password):
    """
    设置登录信息
    :param host: 服务器地址
    :param port: 连接端口
    :param License: 许可证加密字符串
    :param app_id: 应用编号
    :param user_id: 用户名
    :param password: 用户密码
    :return:
    """
    global c_char_p_host
    global c_char_p_license
    global c_char_p_app_id
    global c_char_p_user_id
    global c_char_p_password
    c_char_p_host.value = host.encode()
    c_char_p_license.value = License.encode()
    c_char_p_app_id.value = app_id.encode()
    c_char_p_user_id.value = user_id.encode()
    c_char_p_password.value = password.encode()
    spdll.SPAPI_SetLoginInfo(c_char_p_host, c_int(port), c_char_p_license, c_char_p_app_id, c_char_p_user_id, c_char_p_password)
    api_logger.info(f'设置登录信息-host:{host} port:{port} license:{License} app_id:{app_id} user_id:{user_id}')


def login():
    """
    发出登录请求
    :return: 0, 代表成功发送登录请求.
    """
    ret = spdll.SPAPI_Login()
    if ret == 0:
        api_logger.info(f'{c_char_p_user_id.value.decode()}登录请求发送成功')
    else:
        api_logger.error(f'{c_char_p_user_id.value.decode}登录请求发送失败,errcode:{ret}')
    return ret


def logout():
    """
    发送登出请求.
    :return:0, 代表成功发送登出请求.
    """

    ret = spdll.SPAPI_Logout(c_char_p_user_id)
    if ret == 0:
        api_logger.info(f'{c_char_p_user_id.value.decode()}登出请求发送成功')
    else:
        api_logger.error(f'{c_char_p_user_id.value.decode()}登出请求发送失败,errcode:{ret}')
    return ret


def change_password(old_psw, new_psw):
    """
    修改用户密码.
    :param old_psw:原始密码
    :param new_psw:新密码
    :return:0, 代表成功发送登出请求.
    """
    ret = spdll.SPAPI_Logout(c_char_p_user_id, c_char_p(old_psw), c_char_p(new_psw))
    if ret == 0:
        api_logger.info(f'{c_char_p_user_id.value.decode()}修改密码请求发送成功')
    else:
        api_logger.error(f'{c_char_p_user_id.value.decode()}修改密码请求发送失败,errcode:{ret}')
    return ret


def get_login_status(host_id):
    """
    查询交易连接状态与行情连接状态.
    :param host_id:80,81, 表示交易连接.(用户登录状态)
                   83, 表示一般价格连接.
                   88, 表示一般资讯连接.
    :return:1：没有登入，2：连接中，3：已连接，4：连接失败，5：已登出 6：API阻塞
    """

    ret = spdll.SPAPI_GetLoginStatus(c_char_p_user_id, c_short(host_id))
    if ret in RET_CODE_MSG_LOGIN_STATUS:
        api_logger.info(f'获取{host_id}连接状态成功,{RET_CODE_MSG_LOGIN_STATUS[ret]}')
    else:
        api_logger.error(f'获取{host_id}连接状态失败,errcode:{ret}')
    return ret


def add_order(buy_sell, prod_code, qty, price=None, condtype=0, validtype=0, stoptype=0, stoplevel=0, decinprice=0, **kwargs):
    order = SPApiOrder()
    order.AccNo = c_char_p_user_id.value
    order.Initiator = c_char_p_user_id.value
    order.BuySell = buy_sell.encode()
    order.Qty = qty
    order.ProdCode = prod_code.encode()
    order.Ref = b'@PYTHON#TRADEAPI'
    order.GatewayCode = b''
    order.CondType = condtype
    order.DecInPrice = b'0'
    order.StopType = stoptype.encode()
    if 'ClOrderId' in kwargs: order.ClOrderId = kwargs['C1OrderId'].encode()
    order.ValidType = validtype
    order.DecInPrice = decinprice
    if order.CondType == 0:
        if price:
            order.OrderType = 0
            order.Price = c_double(price)
            order.Ref2 = b'Limit Order'
        else:
            order.OrderType = 6
            order.Ref2 = b'Market Order'
    elif order.CondType == 1:
        if order.StopType == b'L':
            order.StopLevel = stoplevel
            order.Price = price
            order.ValidType = validtype  # 当天有效
            order.Ref2 = b'Stop Limit Order'
        elif order.StopType == b'U':
            order.StopLevel = stoplevel
            order.Price = price
            order.ValidType = validtype  # 当天有效
            order.Ref2 = b'Up Trigger Limit Order'
        elif order.StopType == b'D':
            order.StopLevel = stoplevel
            order.Price = price
            order.ValidType = validtype  # 当天有效
            order.Ref2 = b'Down Trigger Limit Order'

    ret = spdll.SPAPI_AddOrder(order)
    if ret == 0:
        api_logger.info(f'添加订单成功')
    else:
        api_logger.error(f'添加订单失败,errcode:{ret},err:{RET_CODE_MSG_ORDER[ret]}')
    return ret


def add_inactive_order(buy_sell, prod_code, qty, price, is_ao=False, condtype=0, validtype=0, decinprice=0, **kwargs):
    order = SPApiOrder()
    order.AccNo = c_char_p_user_id.value
    order.Initiator = c_char_p_user_id.value
    order.BuySell = buy_sell.encode()
    order.Qty = qty
    order.ProdCode = prod_code.encode()
    order.Ref = b'@PYTHON#TRADEAPI'
    order.Ref2 = b'0'
    order.GatewayCode = b''
    order.CondType = condtype
    order.DecInPrice = b'0'
    if 'ClOrderId' in kwargs: order.ClOrderId = kwargs['C1OrderId'].encode()
    order.ValidType = validtype
    order.DecInPrice = decinprice
    # if
    if is_ao:
        order.OrderType = 2
        order.Price = c_long(0x7fffffff)
        order.StopType = 0
        order.StopLevel = 0
    else:
        order.OrderType = 0
        order.Price = c_double(price)

    ret = spdll.SPAPI_AddOrder(order)
    if ret == 0:
        api_logger.info(f'添加无效订单成功')
    else:
        api_logger.error(f'添加无效订单失败,,errcode:{ret},err:{RET_CODE_MSG_ORDER[ret]}')
    return order


def change_order(order, org_price, org_qty):
    ret = spdll.SPAPI_ChangeOrder(c_char_p_user_id, pointer(order), c_double(org_price), c_double(org_qty))
    if ret == 0:
        api_logger.info(f'修改工作中的订单：#{order.IntOrderNo}成功')
    else:
        api_logger.error(f'修改工作中的订单：#{order.IntOrderNo}失败,errcode:{ret},err:{RET_CODE_MSG_CHANGE_ORDER[ret]}')
    return ret


def change_order_by(accOrderNo, org_price, org_qty, newPrice, newQty):
    ret = spdll.SPAPI_ChangeOrderBy(c_char_p_user_id,
                                    c_char_p_user_id,
                                    c_long(accOrderNo),
                                    c_double(org_price),
                                    c_long(org_qty),
                                    c_double(newPrice),
                                    c_long(newQty))
    if ret == 0:
        api_logger.info(f'修改工作中的订单：#{accOrderNo}成功')
    else:
        api_logger.error(f'修改工作中的订单：#{accOrderNo}失败,errcode:{ret},err:{RET_CODE_MSG_CHANGE_ORDER[ret]}')
    return ret


def get_order_by_orderNo(order_no):
    order = SPApiOrder()
    ret = spdll.SPAPI_GetOrderByOrderNo(c_char_p_user_id, c_char_p_user_id, c_long(order_no), byref(order))
    if ret == 0:
        api_logger.info(f'获取订单：#{order_no}成功')
    else:
        api_logger.error(f'获取订单：#{order_no}失败,errcode:{ret}')
    return order


def get_order_count():
    ret = spdll.SPAPI_GetOrderCount(c_char_p_user_id, c_char_p_user_id)
    if ret == 0:
        api_logger.info(f'获取订单数量成功')
    else:
        api_logger.error(f'获取订单数量失败,errcode:{ret}')
    return ret


# def get_active_order():
#     orders = POINTER(SPApiOrder)
#     ret = spdll.SPAPI_GetActiveOrder(c_char_p_user_id, c_char_p_user_id, orders)
#     if ret == 0:
#         return  orders
#     else:
#         raise Exception('获取订单失败！')


def get_orders_by_array():
    orders_list = (SPApiOrder * get_order_count())()
    ret =spdll.SPAPI_GetOrdersByArray(c_char_p_user_id, c_char_p_user_id, byref(orders_list))
    if ret == 0:
        api_logger.info(f'获取所有订单列表成功')
    else:
        api_logger.error(f'获取所有订单列表失败,errcode:{ret}')
    return orders_list


def delete_order_by(accOrderNo, productCode, clOrderId=''):
    ret = spdll.SPAPI_DeleteOrderBy(c_char_p_user_id, c_char_p_user_id,
                                    c_long(accOrderNo),
                                    c_char_p(productCode.encode()),
                                    c_char_p(clOrderId.encode()))
    if ret == 0:
        api_logger.info(f'删除{productCode}订单：#{accOrderNo}成功')
    else:
        api_logger.error(f'删除{productCode}订单：#{accOrderNo}失败,errcode：{ret}')
    return ret


def delete_all_orders():
    ret = spdll.SPAPI_DeleteAllOrders(c_char_p_user_id, c_char_p_user_id)
    if ret == 0:
        api_logger.info('删除全部订单成功')
    else:
        api_logger.error(f'删除全部订单失败,errcode:{ret}')
    return ret


def activate_order_by(accOrderNo):
    ret = spdll.SPAPI_ActiveateOrderBy(c_char_p_user_id, c_char_p_user_id, c_long(accOrderNo))
    if ret == 0:
        api_logger.info(f'设置订单：#{accOrderNo}为有效订单成功')
    else:
        api_logger.error(f'设置订单：#{accOrderNo}为有效订单失败,errcode:{ret}')
    return ret


def activate_all_orders():
    ret = spdll.SPAPI_ActiveateAllOrders(c_char_p_user_id, c_char_p_user_id)
    if ret == 0:
        api_logger.info('设置全部订单为有效订单成功')
    else:
        api_logger.error(f'设置全部订单为有效订单失败,errcode:{ret}')
    return ret


def inactivate_order_by(accOrderNo):
    ret = spdll.SPAPI_InactivateOrderBy(c_char_p_user_id, c_char_p_user_id, c_long(accOrderNo))
    if ret == 0:
        api_logger.info(f'设置订单：#{accOrderNo}为无效订单成功')
    else:
        api_logger.error(f'设置订单：#{accOrderNo}为无效订单失败,errcode:{ret}')
    return ret


def inactivate_all_orders():
    ret = spdll.SPAPI_InactiveateAllOrders(c_char_p_user_id, c_char_p_user_id)
    if ret == 0:
        api_logger.info('设置全部订单为无效订单成功')
    else:
        api_logger.error('设置全部订单为无效订单失败,errcode:{ret}')
    return ret


def send_marketmaking_order(*args):
    mmorder = SPApiMMOrder(*args)  # TODO mmorder
    ret = spdll.SPAPI_SendMarketMakingOrder(pointer(mmorder))
    if ret == 0:
        api_logger.info('造市商下单成功')
    else:
        api_logger.error(f'造市商下单失败,errcode：{ret}')
    return ret


def get_pos_count():
    """
    该方法用来获取持仓数量.
    :return:持仓数量.
    """
    ret = spdll.SPAPI_GetPosCount(c_char_p_user_id)
    if ret >= 0:
        api_logger.info('获取持仓数量成功')
    else:
        api_logger.error(f'获取持仓数量失败,errcode:{ret}')
    return ret


# def get_all_pos():
#     all_pos = pointer(SPApiPos())
#     ret = spdll.SPAPI_GetAllPos(c_char_p_user_id, all_pos)
#     if ret == 0:
#         return all_pos
#     else:
#         raise Exception('获取全部持仓信息失败')


def get_all_pos_by_array():
    all_pos = (SPApiPos * get_pos_count())()
    ret = spdll.SPAPI_GetAllPosByArray(c_char_p_user_id, byref(all_pos))
    if ret == 0:
        api_logger.info('获取全部持仓信息列表成功')
    else:
        api_logger.error(f'获取全部持仓信息列表失败,errcode:{ret}')
    return all_pos


def get_pos_by_product(prod_code):
    product_pos = SPApiPos()
    ret = spdll.SPAPI_GetPosByProduct(c_char_p_user_id, c_char_p(prod_code.encode()), byref(product_pos))
    if ret == 0:
        api_logger.info(f'获取{prod_code}持仓信息列表成功')
    else:
        api_logger.error(f'获取{prod_code}持仓信息列表失败,errcode:{ret}')
    return product_pos


def get_trade_count():
    ret = spdll.SPAPI_GetTradeCount(c_char_p_user_id, c_char_p_user_id)
    if ret >=0 :
        api_logger.info(f'获取成交数量成功')
    else:
        api_logger.error(f'获取成交数量失败,errcode:{ret}')
    return ret

# def get_all_trades():
#     all_trades = POINTER(SPApiTrade)()
#     ret = spdll.SPAPI_GetAllTrades(c_char_p_user_id, c_char_p_user_id, all_trades)
#     if ret == 0:
#         return all_trades
#     else:
#         raise Exception(f'获取成交信息列表失败，errcode：{ret}')


def get_all_trades_by_array():
    all_trades = (SPApiTrade * get_trade_count())()
    ret = spdll.SPAPI_GetAllTrades(c_char_p_user_id, c_char_p_user_id, byref(all_trades))
    if ret == 0:
        api_logger.info(f'获取成交信息列表成功')
    else:
        api_logger.error(f'获取成交信息列表失败,errcode:{ret}')
    return all_trades


def subscribe_price(prod_code, mode):
    mode_type = {0: '取消', 1:'订阅'}
    ret = spdll.SPAPI_SubscribePrice(c_char_p_user_id, c_char_p(prod_code.encode()), c_int(mode))
    if ret == 0:
        api_logger.info(f'{mode_type[mode]}{prod_code}市场数据成功')
    else:
        api_logger.error(f'{mode_type[mode]}{prod_code}市场数据失败,errcode:{ret}')
    return ret


def get_price_by_code(prod_code):
    price_by_code = SPApiPrice()
    ret = spdll.SPAPI_GetPriceByCode(c_char_p_user_id, c_char_p(prod_code.encode()), pointer(price_by_code))
    if ret == 0:
        api_logger.info(f'获取{prod_code}价格信息成功')
    else:
        api_logger.error(f'获取{prod_code}价格信息失败,errcode:{ret}')
    return price_by_code


def load_instrument_list():
    ret = spdll.SPAPI_LoadInstrumentList()
    if ret >= 0:
        api_logger.info('加载所有合约系列信息成功')
    else:
        api_logger.error(f'加载所有合约系列信息失败,errcode:{ret}')
    return ret


def get_instrument_count():
    ret = spdll.SPAPI_GetInstrumentCount()
    if ret >= 0:
        api_logger.info('获取市场产品系列数量成功')
    else:
        api_logger.error(f'获取市场产品系列数量失败,errcode:{ret}')
    return ret

# def get_instrument():
#     inst_list = (SPApiInstrument * get_instrument_count())()  # TODO SPApiInstrument
#     ret = spdll.SPAPI_GetInstrument(byref(inst_list))
#     if ret == 0:
#         return inst_list
#     else:
#         raise Exception('获取产品系列信息失败')
#     pass


def get_instrument_by_array():
    inst_list = (SPApiInstrument * get_instrument_count())()
    ret = spdll.SPAPI_GetInstrumentByArray(byref(inst_list))
    if ret == 0:
        api_logger.info('获取市场产品系列数量成功')
    else:
        api_logger.error(f'获取产品系列信息失败,errcode:{ret}')
    return inst_list


def get_instrument_by_code(inst_code):
    inst_by_code = SPApiInstrument()
    ret = spdll.SPAPI_GetInstrumentByCode(c_char_p(inst_code.encode()), byref(inst_by_code))
    if ret == 0:
        api_logger.info(f'获取~{inst_code}~产品系列信息成功')
    else:
        api_logger.error(f'获取~{inst_code}~产品系列信息失败,errcode:{ret}')
    return inst_by_code


def get_product_count():
    ret = spdll.SPAPI_GetProductCount()
    if ret >= 0 :
        api_logger.info('获取市场合约数量成功')
    else:
        api_logger.error(f'获取市场合约数量失败,errcode:{ret}')
    return ret

# def get_product():
#     prod_list = pointer(SPApiProduct())  # TODO SPApiProduct
#     ret = spdll.SPAPI_GetProduct(prod_list)
#     if ret == 0 :
#         return prod_list
#     else:
#         raise Exception('获取已加载的产品合约信息失败')


def get_product_by_array():
    prod_list = (SPApiProduct * get_product_count())()
    ret = spdll.SPAPI_GetProductByArray(byref(prod_list))
    if ret == 0 :
        api_logger.info('获取已加载的产品合约信息成功')
    else:
        api_logger.info('获取已加载的产品合约信息失败,errcode:{ret}')
    return prod_list


def get_product_by_code(prod_code):
    prod_by_code = SPApiProduct()
    ret = spdll.SPAPI_GetProductByCode(c_char_p(prod_code.encode()), byref(prod_by_code))
    if ret == 0:
        api_logger.info(f'获取{prod_code}合约信息成功')
    else:
        api_logger.error(f'获取{prod_code}合约信息失败,errcode:{ret}')
    return prod_by_code


def get_accbal_count():
    ret = spdll.SPAPI_GetAccBalCount(c_char_p_user_id)
    if ret >= 0:
        api_logger.info('获取账户现金结余数量成功')
    else:
        api_logger.error(f'获取账户现金结余数量失败,errcode:{ret}')
    return ret


# def get_all_accbal():
#     all_accbal = pointer(SPApiAccBal())
#     ret = spdll.SPAPI_GetAllAccBal(c_char_p_user_id, all_accbal)
#     if ret == 0:
#         print('获取账户全部现金结余信息成功')
#         return all_accbal
#     else:
#         print(f'获取账户全部现金结余信息失败')


def get_all_accbal_by_array():
    all_accbal = (SPApiAccBal * get_accbal_count())()
    ret = spdll.SPAPI_GetAllAccBalByArray(c_char_p_user_id, byref(all_accbal))
    if ret == 0:
        api_logger.info('获取账户全部现金结余信息成功')
    else:
        api_logger.error(f'获取账户全部现金结余信息失败,errcode:{ret}')
    return all_accbal


def get_accbal_by_currency(ccy):
    accbal_by_currency = SPApiAccBal()
    ret = spdll.SPAPI_GetAccBalByCurrency(c_char_p_user_id, c_char_p(ccy.encode()), byref(accbal_by_currency))
    if ret == 0:
        api_logger.info(f'获取{ccy}现金结余信息成功')
    else:
        api_logger.error(f'获取{ccy}现金结余信息失败,errcode:{ret}')
    return accbal_by_currency


def subscribe_ticker(prod_code, mode):
    """
    订阅/取消指定合约的市场成交信息
    :param prod_code:合约代码
    :param mode:0:取消市场成交记录 1:订阅市场成交记录
    :return:
    """
    mode_type = {0: '取消', 1: '订阅'}
    ret = spdll.SPAPI_SubscribeTicker(c_char_p_user_id, c_char_p(prod_code.encode()), c_int(mode))
    if ret == 0:
        api_logger.info(f'{mode_type[mode]}{prod_code}市场成交信息成功')
    else:
        api_logger.error(f'{mode_type[mode]}{prod_code}市场成交信息失败,errcode:{ret}')
    return ret


def subscribe_quote_request(prod_code, mode):
    """
    订阅/取消指定合约的要求报价行情
    :param prod_code: 合约代码
    :param mode:0:取消此合约的要求报价行情  1:订阅此合约的要求报价行情.
    :return:
    """
    mode_type = {0: '取消', 1: '订阅'}
    ret = spdll.SPAPI_SubscribeQuoteRequest (c_char_p_user_id, c_char_p(prod_code.encode()), c_int(mode))
    if ret == 0:
        api_logger.info(f'{mode_type[mode]}{prod_code}报价行情成功')
    else:
        api_logger.error(f'{mode_type[mode]}{prod_code}报价行情失败,errcode:{ret}')
    return ret


def subscribe_all_quote_request(mode):
    """
    订阅/取消所有合约的要求报价行情
    :param mode:0:取消此合约的要求报价行情  1:订阅此合约的要求报价行情.
    :return: 0,成功
    """
    mode_type = {0: '取消', 1: '订阅'}
    ret = spdll.SPAPI_SubscribeQuoteRequest(c_char_p_user_id, c_int(mode))
    if ret == 0:
        api_logger.info(f'{mode_type[mode]}所有报价行情成功')
    else:
        api_logger.error(f'{mode_type[mode]}所有报价行情失败,errcode:{ret}')
    return ret


def get_acc_info():
    """
    获取帐户信息
    :return: 账户信息
    """
    acc_info = SPApiAccInfo()
    ret = spdll.SPAPI_GetAccInfo(c_char_p_user_id, byref(acc_info))
    if ret == 0:
        api_logger.info('获取账户信息成功')
    else:
        api_logger.error(f'获取账户信息失败,errcode:{ret}')
    return acc_info

def get_dll_version():
    """
    查询 DLL 版本信息
    :return:
    """
    c_dll_ver_no = c_char_p()
    c_dll_rel_no = c_char_p()
    c_dll_suffix = c_char_p()
    ret = spdll.SPAPI_GetDllVersion(c_dll_ver_no, c_dll_rel_no, c_dll_suffix)
    if ret == 0:
        version = {'DLL的版本信息': c_dll_ver_no,
                   '发布版本号': c_dll_rel_no,
                   '更新时间': c_dll_suffix}
        return version
    else:
        raise Exception('查询DLL版本信息失败')


def load_productinfolist_by_market(market_code):
    """
    根据交易所加载该交易所下的合约信息
    :param market_code:
    :return:
    """
    ret = spdll.SPAPI_LoadProductInfoListByMarket(c_char_p(market_code.encode()))
    if ret >= 0:
        api_logger.info(f'请求加载<{market_code}>交易所合约信息成功')
    else:
        api_logger.error(f'请求加载<{market_code}>交易所合约信息失败,errcode:{ret}')
    return ret


def load_productinfolist_by_code(inst_code):
    """
    根据产品系列代码加载该系列下的合约信息,需要先加载产品代码，才可以取合约代码
    :param inst_code:产品系列代码
    :return:
    """
    ret = spdll.SPAPI_LoadProductInfoListByCode(c_char_p(inst_code.encode()))
    if ret >= 0:
        api_logger.info(f'请求加载~{inst_code}~产品系列代码合约信息成功')
    else:
        api_logger.error(f'请求加载~{inst_code}~产品系列代码合约信息失败,errcode:{ret}')
    return ret


def set_ApiLog_path(path):
    """
    设置日志的存放位置
    :param path:路径
    :return:
    """
    ret = spdll.SPAPI_SetApiLogPath(c_char_p(path))
    if ret == 0:
        api_logger.info('设置日志存放位置成功')
    else:
        api_logger.error(f'设置日志存放位置失败,errcode:{ret}')
    return ret


def get_ccy_rate_by_ccy(ccy):
    """
    获取兑换率
    :param ccy:货币名
    :return:
    """
    c_rate = c_double()
    ret = spdll.SPAPI_GetCcyRateByCcy(c_char_p_user_id, c_char_p(ccy.encode()), byref(c_rate))
    if ret == 0:
        api_logger.info(f'获取{ccy}兑换率成功')
    else:
        api_logger.error(f'获取{ccy}兑换率失败,errcode:{ret}')
    return c_rate


def account_login(user_id, acc_no):
    """
    该方法只针对 AE,当 AE 登录后可选择性登录账户
    :param user_id: 登入时用户帐号(即AE登入时账号)
    :param acc_no:指定客户账户名
    :return:
    """
    ret = spdll.SPAPI_AccountLogin(c_char_p(user_id.encode()), c_char_p(acc_no.encode()))
    if ret == 0:
        api_logger.info(f'登入acc账户{acc_no}成功')
    else:
        api_logger.error(f'登入acc账户{acc_no}失败,errcode:{ret}')
    return ret


def account_logout(user_id, acc_no):
    """
    该方法只针对 AE,当 AE 选择账户后可用它来释放账户
    :param user_id: 登入时用户帐号(即AE登入时账号)
    :param acc_no:指定客户账户名
    :return:
    """
    ret = spdll.SPAPI_AccountLogout(c_char_p(user_id.encode()), c_char_p(acc_no.encode()))
    if ret == 0:
        api_logger.info(f'释放acc账户{acc_no}成功')
    else:
        api_logger.error(f'释放acc账户{acc_no}失败')
    return ret


def send_acc_control(user_id, acc_no, ctrl_mask, ctrl_level):
    """
    户口控制，该方法只针对 AE
    :param user_id:
    :param acc_no:
    :param ctrl_mask:CTRLMASK_CTRL_LEVEL 1 //户口控制:级别
                     CTRLMASK_KICKOUT 2 //户口控制:踢走
                     当ctrl_mask为1设置户口级数，为2时踢出用户登录状态
    :param ctrl_level:0:"级别0 - 正常客户使用",
                      1:"级别1 - 暂停客户交易",
                      2:"级别2 - 暂停客户登入及交易",
                      3:"级别3 - 冻结户口",
                      4:"级别4 – 只限客户交易",
                        当ctrl_mask为1，ctrl_level输入0-4的级别,
                        当ctrl_mask为2，ctrl_level输入0就可以了。
    :return:
    """
    ret = spdll.SPAPI_SetAccControl(c_char_p(user_id.encode()),
                                    c_char_p(acc_no.encode()),
                                    c_char(ctrl_mask.encode()),
                                    c_char(ctrl_level.encode())
                                    )
    if ret == 0:
        api_logger.info('请求控制成功')
    else:
        api_logger.error('请求控制失败,errcode:{ret}')
    return ret


# ------------------------callback_function----------------------------------+
def on_login_reply(user_id, ret_code, ret_msg):
    """
    登陆回调方法
    :param user_id:用户登入户口
    :param ret_code:长整型编号.0:表示登录成功.如果登录失败也会有相应的错误编号
    :param ret_msg:登录信息.如果登录成功返回的是一个空字符串.如果登录失败会返回相应的错误提示
    :return:
    """
    # print(user_id)
    # if not ret_code:
    #     print('登录成功')
    pass

def on_pswchange_reply(ret_code, ret_msg):
    """
    修改密码的回调方法
    :param ret_code:返回一个长整型编号.0:表示密码修改成功.如果修改失败也会有相应的错误编号
    :param ret_msg:密码修改信息.如果密码成功返回的是一个空字符串.如果修改失败会返回相应的错误提示
    :return:
    """
    pass


def on_order_request_failed(action, order, err_code, err_msg):
    """
    订单请求失败回调方法.
    :param action:订单操作编号
    :param order:订单信息(SPApiOrder)
    :param err_code:错误编码
    :param err_msg:错误信息
    :return:
    """
    pass


def on_order_before_send_report(order):
    """
    订单请求后服务器接收前的发送中回调方法.请求仍在客户端
    :param order:订单信息(SPApiOrder)
    :return:
    """
    pass


def on_mmorder_request_failed(mm_order, err_code, err_msg):
    """
    造市商订单请求失败回调方法
    :param mm_order:订单信息(SPApiMMOrder)
    :param err_code:错误编码
    :param err_msg:错误信息
    :return:
    """
    pass


def on_mmorder_before_send_report(mm_order):
    """
    造市商订单请求后服务器接收前的发送中回调方法.请求仍在客户端
    :param mm_order:订单信息(SPApiMMOrder)
    :return:
    """
    pass


def on_quote_request_received_report(product_code, buy_sell, qty):
    """
    要求报价行情信息回调方法
    :param product_code:合约名
    :param buy_sell:要求报价方向.0：双向报价  B：买  S：沽
    :param qty:要求报价数量
    :return:
    """
    pass


def on_trade_report(rec_no, trade):
    """
    成交记录更新(登入后)回调的方法
    :param rec_no:成交记录在服务器中的记录编号
    :param trade:已成交的订单信息(SPApiTrade)
    :return:
    """
    pass


def on_load_trade_ready_push(rec_no, trade):
    """
    普通客户(Client Mode)登入后,成交信息(登入前的已存的成交)回调方法
    :param rec_no:成交记录在服务器中的记录编号
    :param trade:已成交的订单信息(SPApiTrade)
    :return:
    """
    pass


def on_api_price_update(price):
    """
    行情更新回调的方法
    :param price:合约更新的信息(SPApiPrice)
    :return:
    """
    pass


def on_ticker_update(ticker):
    """
    市场成交记录的回调方法
    :param ticker:新的市场成交记录信息(SPApiTicker)
    :return:
    """
    pass


def on_order_report(rec_no, order):
    """
    订单报告回调方法
    :param rec_no:订单在服务器中的记录编号
    :param order:订单信息(SPApiOrder)
    :return:
    """
    pass


def on_instrument_list_reply(req_id, is_ready, ret_msg):
    """
    产品系列信息回调方法
    :param req_id:请求时返回值对应此回调req_id
    :param is_ready:是否加载成功：true:产品系列信息加载成功  false:产品系列信息加载没有完成
    :param ret_msg:返回的提示信息
    :return:
    """
    pass


def on_business_date_reply(business_date):
    """
    登录成功后返回一个交易日期
    :param business_date:Unix 时间戳
    :return:
    """
    pass


def on_connecting_reply(host_type, con_status):
    """
    连接状态的回调方法
    :param host_type:返回发生改变的行情状态服务器的ID
                     80,81： 表示交易连接
                     83：表示一般价格连接
                     88：表示一般资讯连接
    :param con_status:1：连接中，2：已连接，3：连接错误， 4：连接失败
    :return:
    """
    pass


def on_account_login_reply(accNo, ret_code, ret_msg):
    """
    普通客户(Client Mode)登入的回调方法
    :param accNo:客户账号
    :param ret_code:
    :param ret_msg:
    :return:
    """
    pass


def on_account_logout_reply(accNo, ret_code, ret_msg):
    """
    普通客户(Client Mode)登出的回调方法
    :param accNo:客户账号
    :param ret_code:返回一个长整型编号.0:表示登录成功.如果登录 失败也会有相应的错误编号
    :param ret_msg:登录信息.如果登录成功返回的是一个空字符串.如果登录失败会返回相应的错误提示
    :return:
    """
    pass


def on_account_info_push(acc_info):
    """
    普通客户(Client Mode)登入后户口信息回调方法
    :param acc_info:客户信息(SPApiAccInfo)
    :return:
    """
    pass


def on_account_position_push(pos):
    """
    普通客户(Client Mode)登入后持仓信息(登入前的已存在持仓)回调方法
    :param pos:持仓信息(SPApiPos)
    :return:
    """
    pass


def on_updated_account_position_push(pos):
    """
    普通客户(Client Mode)登入后持仓信息(登入后新的持仓信息)回调方法
    :param pos:持仓信息(SPApiPos)
    :return:
    """
    pass


def on_updated_account_balance_push(acc_bal):
    """
    户口账户发生变更时回调方法
    :param acc_bal:账户信息(SPApiAccBal)
    :return:
    """
    pass


def on_product_list_by_code_reply(req_id, inst_code, is_ready, ret_msg):
    """
    根据产品系列名返回合约信息的回调方法(当 is_ready=true 时 inst_code=空，说明请求的系列没有 Product 信息)
    :param req_id:请求时返回值对应此回调req_id
    :param inst_code:产品系列代码
    :param is_ready:是否加载成功：true:产品合约信息加载成功 false:产品合约信息加载没有完成
    :param ret_msg:提示信息
    :return:
    """
    pass

def on_account_control_reply(ret_code, ret_msg):
    """
    户口控制回调
    :param ret_code:0 成功, 失败 code
    :param ret_msg:成功为空, 失败原因
    :return:
    """
    pass

class register_base:
    def __init__(self, func, register_func, *args):
        self._func = func
        self._ctype_func = WINFUNCTYPE(None, *args)(self._func)
        self._register_func = register_func
        self._register_func.restype = None
        self._register_func(self._ctype_func)


callback_register_cfun_ctype = {'on_login_reply':
                                    [spdll.SPAPI_RegisterLoginReply, c_char_p, c_long, c_char_p],
                                'on_pswchange_reply':
                                    [spdll.SPAPI_RegisterPswChangeReply, c_long, c_char_p],
                                'on_order_request_failed':
                                    [spdll.SPAPI_RegisterOrderRequestFailed, c_char, SPApiOrder, c_long, c_char_p],
                                'on_order_before_send_report':
                                    [spdll.SPAPI_RegisterOrderBeforeSendReport, SPApiOrder],
                                # 'on_mmorder_request_failed':
                                #     [spdll.SPAPI_RegisterMMOrderRequestFailed, SPApiMMOrder, c_long, c_char_p],
                                # 'on_mmorder_before_send_report':
                                #     [spdll.SPAPI_RegisterMMOrderBeforeSendReport, SPApiMMOrder],
                                'on_quote_request_received_report':
                                    [spdll.SPAPI_RegisterQuoteRequestReceivedReport, c_char_p, c_char_p, c_long],
                                'on_trade_report':
                                    [spdll.SPAPI_RegisterTradeReport, c_long, SPApiTrade],
                                'on_load_trade_ready_push':
                                    [spdll.SPAPI_RegisterLoadTradeReadyPush, c_long, SPApiTrade],
                                'on_api_price_update':
                                    [spdll.SPAPI_RegisterApiPriceUpdate, SPApiPrice],
                                'on_ticker_update':
                                    [spdll.SPAPI_RegisterTickerUpdate, SPApiTicker],
                                'on_order_report':
                                    [spdll.SPAPI_RegisterOrderReport, c_long, SPApiOrder],
                                'on_instrument_list_reply':
                                    [spdll.SPAPI_RegisterInstrumentListReply, c_long, c_bool, c_char_p],
                                'on_business_date_reply':
                                    [spdll.SPAPI_RegisterBusinessDateReply, c_long],
                                'on_connecting_reply':
                                    [spdll.SPAPI_RegisterConnectingReply, c_long, c_long],
                                'on_account_login_reply':
                                    [spdll.SPAPI_RegisterAccountLoginReply, c_char_p, c_long, c_char_p],
                                'on_account_logout_reply':
                                    [spdll.SPAPI_RegisterAccountLogoutReply, c_char_p, c_long, c_char_p],
                                'on_account_info_push':
                                    [spdll.SPAPI_RegisterAccountInfoPush, SPApiAccInfo],
                                'on_account_position_push':
                                    [spdll.SPAPI_RegisterAccountPositionPush, SPApiPos],
                                'on_updated_account_position_push':
                                    [spdll.SPAPI_RegisterUpdatedAccountPositionPush, SPApiPos],
                                'on_updated_account_balance_push':
                                    [spdll.SPAPI_RegisterUpdatedAccountBalancePush, SPApiAccBal],
                                'on_product_list_by_code_reply':
                                    [spdll.SPAPI_RegisterProductListByCodeReply, c_long, c_char_p, c_bool, c_char_p],
                                # 'on_account_control_reply':
                                #     [spdll.SPAPI_RegisterAccountControlReply, c_long, c_char_p],
                                }



import sys
# for k, v in callback_register_cfun_ctype.items():
#     def register_init(self, func):
#         register_base.__init__(self, func, *v)
#     _doc = getattr(getattr(sys.modules[__name__], k), '__doc__')
#     setattr(sys.modules[__name__],
#             k,
#             type(k,
#                  (register_base, ),
#                  dict(__init__= register_init,
#                       __doc__= _doc))
#                  )
#             )
def _on_login_reply_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterLoginReply, c_char_p, c_long, c_char_p)


def _on_pswchange_reply_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterPswChangeReply, c_long, c_char_p)


def _on_order_request_failed_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterOrderRequestFailed, c_char, SPApiOrder, c_long, c_char_p)


def _on_order_before_send_report_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterOrderBeforeSendReport, SPApiOrder)


def _on_quote_request_received_report_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterQuoteRequestReceivedReport, c_char_p, c_char_p, c_long)


def _on_trade_report_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterTradeReport, c_long, SPApiTrade)


def _on_load_trade_ready_push_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterLoadTradeReadyPush, c_long, SPApiTrade)


def _on_order_report_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterOrderReport, c_long, SPApiOrder)


def _on_business_date_reply_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterBusinessDateReply, c_long)


def _on_ticker_update_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterTickerUpdate, SPApiTicker)


def _on_api_price_update_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterApiPriceUpdate, SPApiPrice)


def _on_account_login_reply_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterAccountLoginReply, c_char_p, c_long, c_char_p)


def _on_account_logout_reply_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterAccountLogoutReply, c_char_p, c_long, c_char_p)


def _on_account_info_push_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterAccountInfoPush, SPApiAccInfo)


def _on_account_position_push_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterAccountPositionPush, SPApiPos)


def _on_updated_account_position_push_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterUpdatedAccountPositionPush, SPApiPos)


def _on_updated_account_balance_push_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterUpdatedAccountBalancePush, SPApiAccBal)


def _on_product_list_by_code_reply_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterProductListByCodeReply, c_long, c_char_p, c_bool, c_char_p)


def _on_instrument_list_reply_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterInstrumentListReply, c_long, c_bool, c_char_p)


def _on_connecting_reply_init(self, func):
    register_base.__init__(self, func, spdll.SPAPI_RegisterConnectingReply, c_long, c_long)


for k, v in callback_register_cfun_ctype.items():
    _doc = getattr(getattr(sys.modules[__name__], k), '__doc__')
    setattr(sys.modules[__name__],
                k,
                type(k,
                     (register_base, ),
                     dict(__init__= getattr(sys.modules[__name__], f'_{k}_init'),
                          __doc__= _doc)
                     )
            )
# @on_ticker_update
# def print_ticker(ticker):
#     print(f'{ticker.TickerTime}-Price:{ticker.Price}-Qty:{ticker.Qty}')

# _login_reply_func = WINFUNCTYPE(None, c_char_p, c_long, c_char_p)(on_login_reply)                  # 工厂函数生成回调函数，参数由回调函数返回类型和参数构成,并对接python回调函数,构造一个ctype的回调函数
# _register_login_reply = spdll.SPAPI_RegisterLoginReply           # 注册函数
# _register_login_reply.restype = None                             # 注册函数的返回类型
# _register_login_reply(_login_reply_func)                        # 把回调函数注册

# _pswchange_reply_func = WINFUNCTYPE(None, c_long, c_char_p)(on_pswchange_reply)
# _register_pswchange_reply = spdll.SPAPI_RegisterPswChangeReply
# _register_pswchange_reply.restype = None
# _register_pswchange_reply(_pswchange_reply_func)

# _order_request_failed_func = WINFUNCTYPE(None, c_int, POINTER(SPApiOrder), c_long, c_char_p)(on_order_request_failed)
# _register_order_request_failed = spdll.SPAPI_RegisterOrderRequestFailed
# _register_order_request_failed.restype = None
# _register_order_request_failed(_order_request_failed_func)

# _order_before_send_report_func = WINFUNCTYPE(None, POINTER(SPApiOrder))(on_order_before_send_report)
# _register_order_before_send_report = spdll.SPAPI_RegisterOrderBeforeSendReport
# _register_order_before_send_report.restype = None
# _register_order_before_send_report(_order_before_send_report_func)

# _mmorder_request_failed_func = WINFUNCTYPE(None, POINTER(SPApiMMOrder), c_long, c_char_p)(on_mmorder_request_failed)
# _register_mmorder_request_failed = spdll.SPAPI_RegisterMMOrderRequestFailed
# _register_mmorder_request_failed.restype = None
# _register_mmorder_request_failed(_mmorder_request_failed_func)

# _mmorder_before_send_report_func = WINFUNCTYPE(None, POINTER(SPApiMMOrder))(on_mmorder_before_send_report)
# _register_mmorder_before_send_report = spdll.SPAPI_RegisterMMOrderBeforeSendReport
# _register_mmorder_before_send_report.restype = None
# _register_mmorder_before_send_report(_mmorder_before_send_report_func)

# _quote_request_received_report_func = WINFUNCTYPE(None, c_char_p, c_char_p, c_long)(on_quote_request_received_report)
# _register_quote_received_report = spdll.SPAPI_RegisterQuoteRequestReceivedReport
# _register_quote_received_report.restype = None
# _register_quote_received_report(_quote_request_received_report_func)

# _trade_reporot_func = WINFUNCTYPE(None, c_long, POINTER(SPApiTrade))(on_trade_report)
# _register_trade_report = spdll.SPAPI_RegisterTradeReport
# _register_trade_report.restype = None
# _register_trade_report(_trade_reporot_func)

# _load_trade_ready_push_func = WINFUNCTYPE(None, c_long, POINTER(SPApiTrade))(on_load_trade_ready_push)
# _register_load_trade_ready_push = spdll.SPAPI_RegisterLoadTradeReadyPush
# _register_load_trade_ready_push.restype = None
# _register_load_trade_ready_push(_load_trade_ready_push_func)

# _api_price_update_func = WINFUNCTYPE(None, POINTER(SPApiPrice))(on_api_price_update)
# _register_api_price_update = spdll.SPAPI_RegisterApiPriceUpdate
# _register_api_price_update.restype = None
# _register_api_price_update(_api_price_update_func)
#
# _ticker_update_func = WINFUNCTYPE(None, SPApiTicker)(on_ticker_update)
# _register_ticker_update = spdll.SPAPI_RegisterTickerUpdate
# _register_ticker_update.restype = None
# _register_ticker_update(_ticker_update_func)

# _order_report_func = WINFUNCTYPE(None, c_long, POINTER(SPApiOrder))(on_order_report)
# _register_order_report = spdll.SPAPI_RegisterOrderReport
# _register_order_report.restype = None
# _register_order_report(_order_report_func)

# _instrument_list_reply_func = WINFUNCTYPE(None, c_long, c_bool, c_char_p)(on_instrument_list_reply)
# _register_instrument_list_reply = spdll.SPAPI_RegisterInstrumentListReply
# _register_instrument_list_reply.restype = None
# _register_instrument_list_reply(_instrument_list_reply_func)

# _business_date_reply_func = WINFUNCTYPE(None, c_long)(on_business_date_reply)
# _register_business_date_reply = spdll.SPAPI_RegisterBusinessDateReply
# _register_business_date_reply.restype = None
# _register_business_date_reply(_business_date_reply_func)

# _connecting_reply_func = WINFUNCTYPE(None, c_long, c_long)(on_connecting_reply)
# _register_connecting_reply = spdll.SPAPI_RegisterConnectingReply
# _register_connecting_reply.restype = None
# _register_connecting_reply(_connecting_reply_func)

# _account_login_reply_func = WINFUNCTYPE(None, c_char_p, c_long, c_char_p)(on_account_login_reply)
# _register_account_login_reply = spdll.SPAPI_RegisterAccountLoginReply
# _register_account_login_reply.restype = None
# _register_account_login_reply(_account_login_reply_func)

# _account_logout_reply_func = WINFUNCTYPE(None, c_char_p, c_long, c_char_p)(on_account_logout_reply)
# _register_account_logout_reply = spdll.SPAPI_RegisterAccountLogoutReply
# _register_account_logout_reply.restype = None
# _register_account_logout_reply(_account_logout_reply_func)

# _account_info_push_func = WINFUNCTYPE(None, POINTER(SPApiAccInfo))(on_account_info_push)
# _register_account_info_push = spdll.SPAPI_RegisterAccountInfoPush
# _register_account_info_push.restype = None
# _register_account_info_push(_account_info_push_func)

# _account_position_push_func = WINFUNCTYPE(None, POINTER(SPApiPos))(on_account_position_push)
# _register_account_position_push = spdll.SPAPI_RegisterAccountPositionPush
# _register_account_position_push.restype = None
# _register_account_position_push(_account_position_push_func)

# _updated_account_position_push_func = WINFUNCTYPE(None, POINTER(SPApiPos))(on_updated_account_position_push)
# _register_updated_account_position_push = spdll.SPAPI_RegisterUpdatedAccountPositionPush
# _register_updated_account_position_push.restype = None
# _register_updated_account_position_push(_updated_account_position_push_func)

# _updated_account_balance_push_func = WINFUNCTYPE(None, POINTER(SPApiAccBal))(on_updated_account_balance_push)
# _register_updated_account_balance_push = spdll.SPAPI_RegisterUpdatedAccountBalancePush
# _register_updated_account_balance_push.restype = None
# _register_updated_account_balance_push(_updated_account_balance_push_func)
#
# _product_list_by_code_reply_func = WINFUNCTYPE(None, c_long, c_char_p, c_bool, c_char_p)(on_product_list_by_code_reply)
# _register_product_list_by_code_reply = spdll.SPAPI_RegisterProductListByCodeReply
# _register_product_list_by_code_reply.restype = None
# _register_product_list_by_code_reply(_product_list_by_code_reply_func)
#
# _account_control_reply_func = WINFUNCTYPE(None, c_long, c_char_p)(on_account_control_reply)
# _register_account_control_reply = spdll.SPAPI_RegisterAccountControlReply
# _register_account_control_reply.restype = None
# _register_account_control_reply(_account_control_reply_func)


# from functools import wraps
# def on_login_reply(func):
#     """
#     登陆回调方法
#     :param user_id:用户登入户口
#     :param ret_code:长整型编号.0:表示登录成功.如果登录失败也会有相应的错误编号
#     :param ret_msg:登录信息.如果登录成功返回的是一个空字符串.如果登录失败会返回相应的错误提示
#     :return:
#     """
#     @wraps(func)
#     def reply(*args, **kwargs):
#         return func(*args, **kwargs)
#     global _login_reply_func
#     global _register_login_reply
#     _login_reply_func = WINFUNCTYPE(None, c_char_p, c_long, c_char_p)(func)  # 工厂函数生成回调函数，参数由回调函数返回类型和参数构成,并对接python回调函数,构造一个ctype的回调函数
#     _register_login_reply = spdll.SPAPI_RegisterLoginReply  # 注册函数
#     _register_login_reply.restype = None  # 注册函数的返回类型
#     _register_login_reply(_login_reply_func)  #
#     return reply

#
# class on_login_reply:
#     def __init__(self, func):
#         self._func = func
#         self._login_reply_func = WINFUNCTYPE(None, c_char_p, c_long, c_char_p)(self._func)
#         self._register_login_reply = spdll.SPAPI_RegisterLoginReply
#         self._register_login_reply.restype = None
#     def __call__(self, func):
#         self._register_login_reply(self._login_reply_func)
