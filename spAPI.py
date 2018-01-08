#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 0004 10:02
# @Author  : Hadrianl 
# @File    : spAPI.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from ctypes import *
from sp_struct import *

spdll = cdll.LoadLibrary('spapidllm64.dll')

config = {'host': 'demo.spsystem1.info',
          'port': 8080,
          'license': '59493B8B4C09F',
          'app_id': 'SPDEMO',
          'user_id': 'DEMO201706051A',
          'password': '1234'}


def initialize():
    """
    API初始化
    :return: 0代表成功
    """
    return spdll.SPAPI_Initialize()


def unintialize():
    """
    释放API
    :return:0, 代表成功.
            -1, 用户未登出
            -2，释放异常
    """
    return spdll.SPAPI_Uninitialize()


def set_language(langid: int):
    """
    设定服务器返回信息的字体.此方法在 SPAPI_Initialize 前使用,如不使用,返回字体默
    认为 0:英文。
    :param langid:0:英  1:繁  2:简
    :return:0:表示请求成功
    """
    return spdll.SPAPI_SetLanguageId(c_int(langid))


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


def login():
    """
    发出登录请求
    :return: 0, 代表成功发送登录请求.
    """
    return spdll.SPAPI_Login()


def logout():
    """
    发送登出请求.
    :return:0, 代表成功发送登出请求.
    """
    if not c_char_p_user_id.value:
        raise Exception('未登录')
    else:
        return spdll.SPAPI_Logout(c_char_p_user_id)


def change_password(old_psw, new_psw):
    """
    修改用户密码.
    :param old_psw:原始密码
    :param new_psw:新密码
    :return:0, 代表成功发送登出请求.
    """
    if not c_char_p_user_id.value:
        raise Exception('未登录')
    else:
        return spdll.SPAPI_Logout(c_char_p_user_id, c_char_p(old_psw), c_char_p(new_psw))


def get_login_status(host_id):
    """
    查询交易连接状态与行情连接状态.
    :param host_id:80,81, 表示交易连接.(用户登录状态)
                   83, 表示一般价格连接.
                   88, 表示一般资讯连接.
    :return:1：没有登入，2：连接中，3：已连接，4：连接失败，5：已登出 6：API阻塞
    """
    if not c_char_p_user_id.value:
        raise Exception('未登录')
    else:
        return spdll.SPAPI_GetLoginStatus(c_char_p_user_id, c_short(host_id))


# order = POINTER(SPApiOrder)
def add_order():
    pass


def add_inactive_order():
    pass


def change_order():
    pass


def change_order_by():
    pass


def get_order_by_orderNo():
    pass


def get_order_count():
    pass


def get_active_order():
    pass


def get_orders_by_array():
    pass


def delete_order_by():
    pass


def delete_all_orders():
    pass


def activate_order_by():
    pass


def activate_all_orders():
    pass


def inactivate_order_by():
    pass


def inactivate_all_orders():
    pass


def send_marketmaking_order():
    pass


def get_pos_count():
    """
    该方法用来获取持仓数量.
    :return:持仓数量.
    """
    pos_count = spdll.SPAPI_GetPosCount(c_char_p_user_id)
    if pos_count == -1:
        raise Exception('获取持仓数量错误！')
    return pos_count


def get_all_pos():
    pass


def get_all_pos_by_array():
    apiPsoList = POINTER(SPApiPos)()
    if spdll.SPAPI_GetAllPosByArray(c_char_p_user_id, apiPsoList) == 0:
        return apiPsoList
    else:
        raise Exception('未获取持仓信息列表')


def get_pos_by_product():
    pass


def get_trade_count():
    return spdll.SPAPI_GetTradeCount(c_char_p_user_id, c_char_p_user_id)


def get_all_trades():
    pass


def get_all_trades_by_array():
    pass


def subscribe_price():
    pass


def get_price_by_code():
    pass


def load_instrument_list():
    pass


def get_instrument_count():
    pass


def get_instrument():
    pass


def get_instrument_by_array():
    pass


def get_instrument_by_code():
    pass

def get_product_count():
    pass


def get_product():
    pass


def get_product_by_array():
    pass


def get_product_by_code():
    pass


def get_accbal_count():
    pass


def get_all_accbal():
    pass


def get_all_accbal():
    pass


def get_all_accbal_by_array():
    pass


def get_accbal_by_currency():
    pass


def subscribe_ticker():
    pass


def subscribe_quote_request():
    pass






# ------------------------callback_function----------------------------------+
def on_login_reply(user_id, ret_code, ret_msg):
    """
    登陆回调方法
    :param user_id:用户登入户口
    :param ret_code:长整型编号.0:表示登录成功.如果登录失败也会有相应的错误编号
    :param ret_msg:登录信息.如果登录成功返回的是一个空字符串.如果登录失败会返回相应的错误提示
    :return:
    """
    print(f'user_id:{user_id}')
    print(f'ret_code:{ret_code}')
    print(f'ret_msg:{ret_msg}')

login_reply_func = WINFUNCTYPE(None, c_char_p, c_long, c_char_p)(on_login_reply)                  # 工厂函数生成回调函数，参数由回调函数返回类型和参数构成,并对接python回调函数,构造一个ctype的回调函数
register_login_reply = spdll.SPAPI_RegisterLoginReply           # 注册函数
register_login_reply.restype = None                             # 注册函数的返回类型
register_login_reply(login_reply_func)                        # 把回调函数注册


def on_pswchange_reply(ret_code, ret_msg):
    """
    修改密码的回调方法
    :param ret_code:返回一个长整型编号.0:表示密码修改成功.如果修改失败也会有相应的错误编号
    :param ret_msg:密码修改信息.如果密码成功返回的是一个空字符串.如果修改失败会返回相应的错误提示
    :return:
    """
    pass

_pswchange_reply_func = WINFUNCTYPE(None, c_long, c_char_p)(on_pswchange_reply)
_register_pswchange_reply = spdll. SPAPI_RegisterPswChangeReply
_register_pswchange_reply.restype = None
_register_pswchange_reply(_pswchange_reply_func)


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

_order_request_failed_func = WINFUNCTYPE(None, c_int, POINTER(SPApiOrder), c_long, c_char_p)(on_order_request_failed)
_register_order_request_failed = spdll.SPAPI_RegisterOrderRequestFailed
_register_order_request_failed.restype = None
_register_order_request_failed(_order_request_failed_func)


def on_order_before_send_report(order):
    """
    订单请求后服务器接收前的发送中回调方法.请求仍在客户端
    :param order:订单信息(SPApiOrder)
    :return:
    """
    pass

_order_before_send_report_func = WINFUNCTYPE(None, POINTER(SPApiOrder))(on_order_before_send_report)
_register_order_before_send_report = spdll.SPAPI_RegisterOrderBeforeSendReport
_register_order_before_send_report.restype = None
_register_order_before_send_report(_order_before_send_report_func)


def on_mmorder_request_failed(mm_order, err_code, err_msg):
    """
    造市商订单请求失败回调方法
    :param mm_order:订单信息(SPApiMMOrder)
    :param err_code:错误编码
    :param err_msg:错误信息
    :return:
    """
    pass

_mmorder_request_failed_func = WINFUNCTYPE(None, POINTER(SPApiMMOrder), c_long, c_char_p)(on_mmorder_request_failed)
_register_mmorder_request_failed = spdll.SPAPI_RegisterMMOrderRequestFailed
_register_mmorder_request_failed.restype = None
_register_mmorder_request_failed(_mmorder_request_failed_func)


def on_mmorder_before_send_report(mm_order):
    """
    造市商订单请求后服务器接收前的发送中回调方法.请求仍在客户端
    :param mm_order:订单信息(SPApiMMOrder)
    :return:
    """
    pass

_mmorder_before_send_report_func = WINFUNCTYPE(None, POINTER(SPApiMMOrder))(on_mmorder_before_send_report)
_register_mmorder_before_send_report = spdll.SPAPI_RegisterMMOrderBeforeSendReport
_register_mmorder_before_send_report.restype = None
_register_mmorder_before_send_report(_mmorder_before_send_report_func)


def on_quote_request_received_report(product_code, buy_sell, qty):
    """
    要求报价行情信息回调方法
    :param product_code:合约名
    :param buy_sell:要求报价方向.0：双向报价  B：买  S：沽
    :param qty:要求报价数量
    :return:
    """
    pass

_quote_request_received_report_func = WINFUNCTYPE(None, c_char_p, c_char_p, c_long)(on_quote_request_received_report)
_register_quote_received_report = spdll.SPAPI_RegisterQuoteRequestReceivedReport
_register_quote_received_report.restype = None
_register_quote_received_report(_quote_request_received_report_func)


def on_trade_report(rec_no, trade):
    """
    成交记录更新(登入后)回调的方法
    :param rec_no:成交记录在服务器中的记录编号
    :param trade:已成交的订单信息(SPApiTrade)
    :return:
    """
    pass

_trade_reporot_func = WINFUNCTYPE(None, c_long, POINTER(SPApiTrade))(on_trade_report)
_register_trade_report = spdll.SPAPI_RegisterTradeReport
_register_trade_report.restype = None
_register_trade_report(_trade_reporot_func)


def on_load_trade_ready_push(rec_no, trade):
    """
    普通客户(Client Mode)登入后,成交信息(登入前的已存的成交)回调方法
    :param rec_no:成交记录在服务器中的记录编号
    :param trade:已成交的订单信息(SPApiTrade)
    :return:
    """
    pass

_load_trade_ready_push_func = WINFUNCTYPE(None, c_long, POINTER(SPApiTrade))(on_load_trade_ready_push)
_register_load_trade_ready_push = spdll.SPAPI_RegisterLoadTradeReadyPush
_register_load_trade_ready_push.restype = None
_register_load_trade_ready_push(_load_trade_ready_push_func)


def on_api_price_update(price):
    """
    行情更新回调的方法
    :param price:合约更新的信息(SPApiPrice)
    :return:
    """
    pass

_api_price_update_func = WINFUNCTYPE(None, POINTER(SPApiPrice))(on_api_price_update)
_register_api_price_update = spdll.SPAPI_RegisterApiPriceUpdate
_register_api_price_update.restype = None
_register_api_price_update(_api_price_update_func)


def on_ticker_update(ticker):
    """
    市场成交记录的回调方法
    :param ticker:新的市场成交记录信息(SPApiTicker)
    :return:
    """
    pass

_ticker_update_func = WINFUNCTYPE(None, POINTER(SPApiTicker))(on_ticker_update)
_register_ticker_update = spdll.SPAPI_RegisterTickerUpdate
_register_ticker_update.restype = None
_register_ticker_update(_ticker_update_func)


def on_order_report(rec_no, order):
    """
    订单报告回调方法
    :param rec_no:订单在服务器中的记录编号
    :param order:订单信息(SPApiOrder)
    :return:
    """
    pass

_order_report_func = WINFUNCTYPE(None, c_long, POINTER(SPApiOrder))(on_order_report)
_register_order_report = spdll.SPAPI_RegisterOrderReport
_register_order_report.restype = None
_register_order_report(_order_report_func)


def on_instrument_list_reply(req_id, is_ready, ret_msg):
    """
    产品系列信息回调方法
    :param req_id:请求时返回值对应此回调req_id
    :param is_ready:是否加载成功：true:产品系列信息加载成功  false:产品系列信息加载没有完成
    :param ret_msg:返回的提示信息
    :return:
    """
    pass

_instrument_list_reply_func = WINFUNCTYPE(None, c_long, c_bool, c_char_p)(on_instrument_list_reply)
_register_instrument_list_reply = spdll.SPAPI_RegisterInstrumentListReply
_register_instrument_list_reply.restype = None
_register_instrument_list_reply(_instrument_list_reply_func)


def on_business_date_reply(business_date):
    """
    登录成功后返回一个交易日期
    :param business_date:Unix 时间戳
    :return:
    """
    pass

_business_date_reply_func = WINFUNCTYPE(None, c_long)(on_business_date_reply)
_register_business_date_reply = spdll.SPAPI_RegisterBusinessDateReply
_register_business_date_reply.restype = None
_register_business_date_reply(_business_date_reply_func)


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

_connecting_reply_func = WINFUNCTYPE(None, c_long, c_long)(on_connecting_reply)
_register_connecting_reply = spdll.SPAPI_RegisterConnectingReply
_register_connecting_reply.restype = None
_register_connecting_reply(_connecting_reply_func)


def on_account_login_reply(accNo, ret_code, ret_msg):
    """
    普通客户(Client Mode)登入的回调方法
    :param accNo:客户账号
    :param ret_code:
    :param ret_msg:
    :return:
    """
    pass

_account_login_reply_func = WINFUNCTYPE(None, c_char_p, c_long, c_char_p)(on_account_login_reply)
_register_account_login_reply = spdll. SPAPI_RegisterAccountLoginReply
_register_account_login_reply.restype = None
_register_account_login_reply(_account_login_reply_func)


def on_account_logout_reply(accNo, ret_code, ret_msg):
    """
    普通客户(Client Mode)登出的回调方法
    :param accNo:客户账号
    :param ret_code:返回一个长整型编号.0:表示登录成功.如果登录 失败也会有相应的错误编号
    :param ret_msg:登录信息.如果登录成功返回的是一个空字符串.如果登录失败会返回相应的错误提示
    :return:
    """
    pass

_account_logout_reply_func = WINFUNCTYPE(None, c_char_p, c_long, c_char_p)(on_account_logout_reply)
_register_account_logout_reply = spdll.SPAPI_RegisterAccountLogoutReply
_register_account_logout_reply.restype = None
_register_account_logout_reply(_account_logout_reply_func)


def on_account_info_push(acc_info):
    """
    普通客户(Client Mode)登入后户口信息回调方法
    :param acc_info:客户信息(SPApiAccInfo)
    :return:
    """
    pass

_account_info_push_func = WINFUNCTYPE(None, POINTER(SPApiAccInfo))(on_account_info_push)
_register_account_info_push = spdll.SPAPI_RegisterAccountInfoPush
_register_account_info_push.restype = None
_register_account_info_push(_account_info_push_func)


def on_account_position_push(pos):
    """
    普通客户(Client Mode)登入后持仓信息(登入前的已存在持仓)回调方法
    :param pos:持仓信息(SPApiPos)
    :return:
    """
    pass

_account_position_push_func = WINFUNCTYPE(None, POINTER(SPApiPos))(on_account_position_push)
_register_account_position_push = spdll.SPAPI_RegisterAccountPositionPush
_register_account_position_push.restype = None
_register_account_position_push(_account_position_push_func)


def on_updated_account_position_push(pos):
    """
    普通客户(Client Mode)登入后持仓信息(登入后新的持仓信息)回调方法
    :param pos:持仓信息(SPApiPos)
    :return:
    """
    pass

_updated_account_position_push_func = WINFUNCTYPE(None, POINTER(SPApiPos))(on_updated_account_position_push)
_register_updated_account_position_push = spdll.SPAPI_RegisterUpdatedAccountPositionPush
_register_updated_account_position_push.restype = None
_register_updated_account_position_push(_updated_account_position_push_func)


def on_updated_account_balance_push(acc_bal):
    """
    户口账户发生变更时回调方法
    :param acc_bal:账户信息(SPApiAccBal)
    :return:
    """
    pass

_updated_account_balance_push_func = WINFUNCTYPE(None, POINTER(SPApiAccBal))(on_updated_account_balance_push)
_register_updated_account_balance_push = spdll.SPAPI_RegisterUpdatedAccountBalancePush
_register_updated_account_balance_push.restype = None
_register_updated_account_balance_push(_updated_account_balance_push_func)


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

_product_list_by_code_reply_func = WINFUNCTYPE(None, c_long, c_char_p, c_bool, c_char_p)(on_product_list_by_code_reply)
_register_product_list_by_code_reply = spdll.SPAPI_RegisterProductListByCodeReply
_register_product_list_by_code_reply.restype = None
_register_product_list_by_code_reply(_product_list_by_code_reply_func)


def on_account_control_reply(ret_code, ret_msg):
    """
    户口控制回调
    :param ret_code:0 成功, 失败 code
    :param ret_msg:成功为空, 失败原因
    :return:
    """
    pass

_account_control_reply_func = WINFUNCTYPE(None, c_long, c_char_p)(on_account_control_reply)
_register_account_control_reply = spdll.SPAPI_RegisterAccountControlReply
_register_account_control_reply.restype = None
_register_account_control_reply(_account_control_reply_func)
