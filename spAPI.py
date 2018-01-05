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


def set_login_info(host, port, license, app_id, user_id, password):
    """
    设置登录信息
    :param host: 服务器地址
    :param port: 连接端口
    :param license: 许可证加密字符串
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
    c_char_p_license.value = license.encode()
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






#######################callback_function###################
def on_login_reply(user_id, ret_code, ret_msg):
    print(f'user_id:{user_id}')
    print(f'ret_code:{ret_code}')
    print(f'ret_msg:{ret_msg}')

login_reply_func = WINFUNCTYPE(None, c_char_p, c_long, c_char_p)(on_login_reply)                  #工厂函数生成回调函数，参数由回调函数返回类型和参数构成,并对接python回调函数
register_login_reply = spdll.SPAPI_RegisterLoginReply           # 注册函数
register_login_reply.restype = None                             # 注册函数的返回类型
register_login_reply(login_reply_func)                        # 把回调函数注册


def on_pswchange_reply(ret_code, ret_msg):
    pass

_pswchange_reply_func = WINFUNCTYPE(None, c_long, c_char_p)(on_pswchange_reply)
_register_pswchange_reply = spdll. SPAPI_RegisterPswChangeReply
_register_pswchange_reply.restype = None
_register_pswchange_reply(_pswchange_reply_func)


def on_order_request_failed(action, order, err_code, err_msg):
    pass

_order_request_failed_func = WINFUNCTYPE(None, c_int, POINTER(SPApiOrder), c_long, c_char_p)(on_order_request_failed)
_register_order_request_failed = spdll.SPAPI_RegisterOrderRequestFailed
_register_order_request_failed.restype = None
_register_order_request_failed(_order_request_failed_func)


def on_order_before_send_report(order):
    pass

_order_before_send_report_func = WINFUNCTYPE(None, POINTER(SPApiOrder))(on_order_before_send_report)
_register_order_before_send_report = spdll.SPAPI_RegisterOrderBeforeSendReport
_register_order_before_send_report.restype = None
_register_order_before_send_report(_order_before_send_report_func)


def on_mmorder_request_failed(mm_order, err_code, err_msg):
    pass

_mmorder_request_failed_func = WINFUNCTYPE(None, POINTER(SPApiMMOrder), c_long, c_char_p)(on_mmorder_request_failed)
_register_mmorder_request_failed = spdll.RegisterMMOrderRequestFailed
_register_mmorder_request_failed.restype = None
_register_mmorder_request_failed(_mmorder_request_failed_func)