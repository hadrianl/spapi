#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/9 0009 15:41
# @Author  : Hadrianl 
# @File    : main.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


from spAPI import *
import time

initialize()
set_login_info(**config2)
@on_login_reply
def reply(user_id, ret_code, ret_msg):
    print(user_id)
    print(ret_code)
    print(ret_code)

@on_ticker_update
def print_ticker(ticker):
    print(f'{ticker.TickerTime}-Price:{ticker.Price}-Qty:{ticker.Qty}')

@on_api_price_update
def printprice(price):
    text = f"""Time:{price.LastTime}
Bid:{price.Bid}   Ask:{price.Ask}
BidQty:{price.BidQty}   AskQty:{price.AskQty}"""
    print(text)

login()
time.sleep(1)
subscribe_ticker('HSIF8', 1)
time.sleep(10)
logout()