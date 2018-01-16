#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/15 0015 8:59
# @Author  : Hadrianl 
# @File    : sp_data_server.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


from spAPI import *
from util import *
import zmq
from zmq import Context
import pymysql as pm
import time

ctx1 = Context()
ctx2 = Context()
ctx3 = Context()
ticker_socket = ctx1.socket(zmq.PUB)
price_socket = ctx2.socket(zmq.PUB)
rep_socket = ctx3.socket(zmq.REP)
ticker_socket.bind('tcp://*: 6868')
price_socket.bind('tcp://*: 6869')
rep_socket.bind('tcp://*: 6666')
conn = pm.connect(host='192.168.2.226', port=3306, user='kairuitouzi', password='kairuitouzi', db='carry_investment', cursorclass=pm.cursors.DictCursor)
cursor = conn.cursor()

from datetime import datetime
initialize()
set_login_info(**config3)

@on_login_reply  # 登录成功时候调用
def reply(user_id, ret_code, ret_msg):
    if ret_code == 0:
        print(f'@{user_id.decode()}登录成功')
    else:
        print(f'@{user_id.decode()}登录失败--errcode:{ret_code}--errmsg:{ret_msg.decode()}')

@on_ticker_update
def ticker_update(ticker):
    sql = f'insert into futures_tick(prodcode, price, tickertime, qty, dealsrc, decinprice) \
values ("{ticker.ProdCode.decode()}", {ticker.Price}, "{datetime.fromtimestamp(ticker.TickerTime)}", {ticker.Qty}, {ticker.DealSrc}, "{ticker.DecInPrice.decode()}")'
    cursor.execute(sql)
    conn.commit()
    ticker_socket.send_pyobj(ticker)

@on_api_price_update
def price_update(price):
    price_socket.send_pyobj(price)

# @on_quote_request_received_report
# def quote_request_received(prod_code, buy_sell, qty):
#     d = {'prod_code': prod_code, 'buy_sell': buy_sell, 'qty': qty}
#     print(d)
#     socket.send_pyobj(d)
login()

time.sleep(1)


if __name__ == '__main__':
    is_login = True
    while True:
        if is_login:
            while True:
                handle, prodcode = rep_socket.recv_multipart()
                handle = handle.decode()
                prodcode = prodcode.decode()
                print(handle, prodcode)
                if handle == 'sub_ticker':
                    subscribe_ticker(prodcode, 1)
                    rep_socket.send_string(f'{prodcode}-Ticker订阅成功')
                elif handle == 'sub_price':
                    subscribe_price(prodcode, 1)
                    rep_socket.send_string(f'{prodcode}-Price订阅成功')
                elif handle == 'unsub_ticker':
                    subscribe_ticker(prodcode, 0)
                    rep_socket.send_string(f'{prodcode}-Ticker取消订阅成功')
                elif handle == 'unsub_price':
                    subscribe_price(prodcode, 0)
                    rep_socket.send_string(f'{prodcode}-Price取消订阅成功')
                elif handle == 'logout':
                    logout()
                    unintialize()
                    is_login = False
                    rep_socket.send_string(f'已登出---{prodcode}')
                    break
                elif handle =='login':
                    rep_socket.send_string('已经登录中，请勿重复登陆')
                else:
                    rep_socket.send_string('未知指令')

        else:
            handle, prodcode = rep_socket.recv_multipart()
            handle = handle.decode()
            prodcode = prodcode.decode()
            if handle == 'login':
                is_login = True
                initialize()
                set_login_info(**config3)
                time.sleep(1)
                login()
                rep_socket.send_string(f'已登入---{prodcode}')
            else:
                time.sleep(1)