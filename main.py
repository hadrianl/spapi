#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/9 0009 15:41
# @Author  : Hadrianl 
# @File    : main.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


from spAPI import *
import time
from datetime import datetime
import configparser

loginfo = configparser.ConfigParser()
loginfo.read(r'conf\loginfo.ini')
spid = 'SP_ID2'
initialize()
sp_config = {'host': loginfo.get(spid, 'host'),
             'port': loginfo.getint(spid, 'port'),
             'License': loginfo.get(spid, 'License'),
             'app_id': loginfo.get(spid, 'app_id'),
             'user_id': loginfo.get(spid, 'user_id'),
             'password': loginfo.get(spid, 'password')}

set_login_info(**sp_config)
@on_login_reply  # 登录成功时候调用
def reply(user_id, ret_code, ret_msg):
    if ret_code == 0:
        print(f'@{user_id.decode()}登录成功')
    else:
        print(f'@{user_id.decode()}登录失败--errcode:{ret_code}--errmsg:{ret_msg.decode()}')

@on_ticker_update  # 有订阅中的成交ticker数据更新时会调用
def print_ticker(ticker):
    print(f'{datetime.fromtimestamp(ticker.TickerTime)}-Price:{ticker.Price}-Qty:{ticker.Qty}')

# @on_api_price_update  # 有订阅中的更新行情会调用
# def printprice(price):
#     text = f"""Time:{price.Timestamp}
# Bid:{price.Bid}   Ask:{price.Ask}
# BidQty:{price.BidQty}   AskQty:{price.AskQty}"""
#     print(text)

@on_pswchange_reply  # 修改密码调用
def pswchange_reply(ret_code, ret_msg):
    if ret_code == 0:
        print('修改密码成功')
    else:
        print(f'errcode:{ret_code}-errmsg:{ret_msg.decode()}')

@on_order_request_failed  # 订单请求失败时候调用
def order_request_failed(action, order, err_code, err_msg):
    print(f'订单请求失败--ACTION:{action}-ProdCode:{order.ProdCode.decode()}-Price:{order.Price}-errcode;{err_code}-errmsg:{err_msg.decode()}')

@on_order_before_send_report  # 订单发送前调用
def order_before_snd_report(order):
    print(f'即将发送订单请求--ProdCode:{order.ProdCode.decode()}-Price:{order.Price}-Qty:{order.Qty}-BuySell:{order.BuySell.decode()}')

@on_quote_request_received_report  # 要求报价行情信息时调用
def quote_request_received_report(prod_code, buy_sell, qty):
    BS = {0: '双向报价', b'B': '买', b'S':'卖'}
    print(f'报价行情信息--ProdCode:{prod_code.decode()}--{BS[buy_sell]}--Qty:{qty}')

@on_trade_report  # 成交记录更新后回调出推送新的成交记录
def trade_report(rec_no, trade):
    print(f'{rec_no}--{trade.OpenClose.decode()}成交@{trade.ProdCode.decode()}--{trade.BuySell.decode()}--Price:{trade.Price}--Qty:{trade.Qty}')

@on_load_trade_ready_push  # 登入后，登入前已存的成交信息推送
def trade_ready_push(rec_no, trade):
    print(f'已有成交记录--{rec_no}--{trade.OpenClose.decode()}成交@{trade.ProdCode.decode()}--{trade.BuySell.decode()}--Price:{trade.Price}--Qty:{trade.Qty}')

@on_order_report  # 订单报告的回调推送
def order_report(rec_no, order):
    print(f'订单报告--编号:{rec_no}-ProdCode:{order.ProdCode.decode()}-Status:{ORDER_STATUS[order.Status]}')

@on_instrument_list_reply  # 产品系列信息的回调推送，用load_instrument_list()触发
def inst_list_reply(req_id, is_ready, ret_msg):
    if is_ready:
        print(f'加载{req_id}产品信息成功')
    else:
        print(f'加载{req_id}产品信息未完成')

@on_business_date_reply  # 登录成功后会返回一个交易日期
def business_date_reply(business_date):
    print(f'当前交易日为:{datetime.fromtimestamp(business_date)}')

@on_connecting_reply  # 当连接状态发生改变时会调用
def connecting_reply(host_type, con_status):
    print(f'{host_type}{HOST_TYPE[host_type]}......{HOST_CON_STATUS[con_status]}')

@on_account_login_reply  # 普通客户登入回调
def login_reply(accNo, ret_code, ret_msg):
    if ret_code == 0:
        print(f'{accNo.decode()}登入成功')
    else:
        print(f'{accNo.decode()}登入失败--errcode:{ret_code}--errmsg:{ret_msg.decode()}')

@on_account_logout_reply  # 普通客户登出回调
def logout_reply(accNo, ret_code, ret_msg):
    if ret_code == 0:
        print(f'{accNo.decode()}登出成功')
    else:
        print(f'{accNo.decode()}登出失败--errcode:{ret_code}--errmsg:{ret_msg.decode()}')

@on_account_info_push  # 普通客户登入后返回登入前的户口信息
def account_info_push(acc_info):
    print(f'@{acc_info.ClientId.decode()}账户信息--NAV:{acc_info.NAV}-BaseCcy:{acc_info.BaseCcy.decode()}-BuyingPower:{acc_info.BuyingPower}-CashBal:{acc_info.CashBal}')

@on_account_position_push  # 普通客户登入后返回登入前的已存在持仓信息
def account_position_push(pos):
    print(f'@{pos.AccNo.decode()}持仓信息--ProdCode:{pos.ProdCode.decode()}-PLBaseCcy:{pos.PLBaseCcy}-Qty:{pos.Qty}')

@on_updated_account_position_push  # 普通客户登入后返回登入前的已存在持仓信息
def updated_account_position_push(pos):
    print(f'@{pos.AccNo.decode()}持仓信息--ProdCode:{pos.ProdCode.decode()}-PLBaseCcy:{pos.PLBaseCcy}-Qty:{pos.Qty}')

@on_updated_account_balance_push  # 户口账户发生变更时的回调
def updated_account_balance_push(acc_bal):
    print(f'账户信息变化-{acc_bal.Ccy.decode()}-CashBF:{acc_bal.CashBF}-TodayCash:{acc_bal.TodayCash}-NotYetValue:{acc_bal.NotYetValue}-Unpresented:{acc_bal.Unpresented}-TodayOut:{acc_bal.TodayOut}')

@on_product_list_by_code_reply  # 根据产品系列名返回合约信息
def product_list_by_code_reply(req_id, inst_code, is_ready, ret_msg):
    if is_ready:
        if inst_code == '':
            print(f'合约信息-{req_id}:该系列没有product信息   {ret_msg.decode()}')
        else:
            print(f'合约信息-{req_id}:{inst_code.decode()}产品合约信息加载成功    {ret_msg.decode()}')
    else:
        print(f'合约信息-{req_id}:{inst_code.decode()}产品合约信息加载未完成    {ret_msg.decode()}')


login()

def add_normal_order(ProdCode, BuySell, Qty, Price=None, AO=False, OrderOption=0, ClOrderId='', ):
    CondType = 0
    price_map = {0: Price, 2: 0x7fffffff, 6: 0}
    if Price:
        assert isinstance(Price, (int, float))
        OrderType = 0
        Price = price_map[OrderType]
    elif AO:
        OrderType = 2
        Price = price_map[OrderType]
    else:
        OrderType = 6
        Price = price_map[OrderType]
    kwargs={'ProdCode': ProdCode,
            'BuySell': BuySell,
            'Qty': Qty,
            'Price': Price,
            'CondType': CondType,
            'OrderType': OrderType,
            'OrderOption': OrderOption,
            'ClOrderId': ClOrderId}
    add_order(**kwargs)

def add_stop_order(ProdCode, BuySell, Qty, Price, StopType='L', StopLevelValidType=0, ValidTime=None, OrderOption=0, ClOrderId=''):
    CondType = 1
    OrderType = 0


# time.sleep(1)
# subscribe_ticker('HSIF8', 1)
# time.sleep(10)
# logout()