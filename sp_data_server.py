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
from threading import Thread
import configparser
conf = configparser.ConfigParser()
conf.read('conf.ini')
dbconfig = {'host': conf.get('MYSQL', 'host'),
            'port': conf.getint('MYSQL', 'port'),
            'user': conf.get('MYSQL', 'user'),
            'password': conf.get('MYSQL', 'password'),
            'db': conf.get('MYSQL', 'db'),
            'cursorclass': pm.cursors.DictCursor
            }
ctx1 = Context()
ctx2 = Context()
ctx3 = Context()
ctx4 = Context()
ticker_socket = ctx1.socket(zmq.PUB)
price_socket = ctx2.socket(zmq.PUB)
rep_price_socket = ctx3.socket(zmq.REP)
rep_socket = ctx4.socket(zmq.REP)
ticker_socket.bind(f'tcp://*: {conf.getint("SOCKET_PORT", "ticker_pub")}')
price_socket.bind(f'tcp://*: {conf.getint("SOCKET_PORT", "price_pub")}')
rep_price_socket.bind(f'tcp://*: {conf.getint("SOCKET_PORT", "rep_price_pub")}')
rep_socket.bind(f'tcp://*: {conf.getint("SOCKET_PORT", "handle_rep")}')
conn = pm.connect(**dbconfig)
cursor = conn.cursor()

from datetime import datetime
spid = 'SP_ID3'
initialize()
sp_config = {'host': conf.get(spid, 'host'),
             'port': conf.getint(spid, 'port'),
             'License': conf.get(spid, 'License'),
             'app_id': conf.get(spid, 'app_id'),
             'user_id': conf.get(spid, 'user_id'),
             'password': conf.get(spid, 'password')}
set_login_info(**sp_config)

@on_login_reply  # 登录成功时候调用
def reply(user_id, ret_code, ret_msg):
    if ret_code == 0:
        print(f'@{user_id.decode()}登录成功')
    else:
        print(f'@{user_id.decode()}登录失败--errcode:{ret_code}--errmsg:{ret_msg.decode()}')

@on_ticker_update
def ticker_update(ticker):
    ticker_socket.send_pyobj(ticker)
    sql = f'insert into futures_tick(prodcode, price, tickertime, qty, dealsrc, decinprice) \
values ("{ticker.ProdCode.decode()}", {ticker.Price}, "{datetime.fromtimestamp(ticker.TickerTime)}", {ticker.Qty}, {ticker.DealSrc}, "{ticker.DecInPrice.decode()}")'
    cursor.execute(sql)
    conn.commit()

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


def get_price():
    while True:
        prodcode = rep_price_socket.recv_string()
        price = get_price_by_code(prodcode)
        rep_price_socket.send_pyobj(price)
if __name__ == '__main__':
    is_login = True
    get_price_thread = Thread(target=get_price)
    get_price_thread.start()
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
                    rep_socket.send_string(f'{sp_config["user_id"]}已登出---{prodcode}')
                    break
                elif handle == 'login':
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
                if prodcode in ['SP_ID1', 'SP_ID2', 'SP_ID3']:
                    spid = prodcode
                    sp_config = {'host': conf.get(spid, 'host'),
                                 'port': conf.getint(spid, 'port'),
                                 'License': conf.get(spid, 'License'),
                                 'app_id': conf.get(spid, 'app_id'),
                                 'user_id': conf.get(spid, 'user_id'),
                                 'password': conf.get(spid, 'password')}
                    set_login_info(**sp_config)
                time.sleep(1)
                login()
                rep_socket.send_string(f'{sp_config["user_id"]}已登入---{prodcode}')
            else:
                time.sleep(1)