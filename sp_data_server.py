#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/15 0015 8:59
# @Author  : Hadrianl 
# @File    : sp_data_server.py
# @License : (C) Copyright 2013-2017, 凯瑞投资


from spAPI import *
import zmq
from zmq import Context
import pymysql as pm
import time
from threading import Thread
import configparser
import logging.config
from datetime import datetime
conf = configparser.ConfigParser()
conf.read(r'conf\conf.ini')
loginfo = configparser.ConfigParser()
loginfo.read(r'conf\loginfo.ini')
logging.config.fileConfig(r'conf\sp_log.conf')
server_logger = logging.getLogger('root.sp_server')
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
        server_logger.info(f'@{user_id.decode()}登录成功')
    else:
        server_logger.error(f'@{user_id.decode()}登录失败--errcode:{ret_code}--errmsg:{ret_msg.decode()}')


to_sql_list = set()
    #('HSIF8', )
@on_ticker_update
def ticker_update(ticker):
    ticker_socket.send_pyobj(ticker)
    if ticker.ProdCode.decode() in to_sql_list:
        sql = f'insert into futures_tick(prodcode, price, tickertime, qty, dealsrc, decinprice) \
    values ("{ticker.ProdCode.decode()}", {ticker.Price}, "{datetime.fromtimestamp(ticker.TickerTime)}", \
    {ticker.Qty}, {ticker.DealSrc}, "{ticker.DecInPrice.decode()}")'
        cursor.execute(sql)
        conn.commit()


@on_api_price_update
def price_update(price):
    price_socket.send_pyobj(price)


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
                handle, arg = rep_socket.recv_multipart()
                handle = handle.decode()
                arg = arg.decode()
                server_logger.info(f'{handle}-{arg}')

                server_logger.info(rep_text)
                if handle == 'sub_ticker':
                    subscribe_ticker(arg, 1)
                    rep_text = f'{arg}-Ticker订阅成功'
                    rep_socket.send_string(rep_text)
                elif handle == 'sub_price':
                    subscribe_price(arg, 1)
                    rep_text = f'{arg}-Price订阅成功'
                    rep_socket.send_string(rep_text)
                elif handle == 'unsub_ticker':
                    subscribe_ticker(arg, 0)
                    rep_text = f'{arg}-Ticker取消订阅成功'
                    rep_socket.send_string(rep_text)
                elif handle == 'unsub_price':
                    subscribe_price(arg, 0)
                    rep_text = f'{arg}-Price取消订阅成功'
                    rep_socket.send_string(rep_text)
                elif handle == 'into_db':
                    to_sql_list.add(arg)
                    rep_text = f'{arg}-启动插入DB'
                    rep_socket.send_string(rep_text)
                elif handle == 'outof_db':
                    try:
                        to_sql_list.add(arg)
                        rep_text = f'{arg}-取消插入DB'
                        rep_socket.send_string(rep_text)
                    except KeyError as e:
                        rep_text = f'{arg}-不存在插入DB队列中'
                        rep_socket.send_string(rep_text)
                elif handle == 'to_sql_list':
                    rep_text = f'ticker_to_DB队列：{",".join(to_sql_list)}'
                    rep_socket.send_string(rep_text)
                elif handle == 'logout':
                    logout()
                    unintialize()
                    is_login = False
                    rep_text = f'{sp_config["user_id"]}已登出---{arg}'
                    rep_socket.send_string(rep_text)
                    break
                elif handle == 'login':
                    rep_text = f'已登录，重复登陆指令未处理'
                    rep_socket.send_string('已经登录中，请勿重复登陆')
                else:
                    rep_text = f'未知指令--{handle}'
                    rep_socket.send_string('未知指令')

        else:
            handle, arg = rep_socket.recv_multipart()
            handle = handle.decode()
            arg = arg.decode()
            if handle == 'login':
                is_login = True
                initialize()
                if arg in ['SP_ID1', 'SP_ID2', 'SP_ID3']:
                    spid = arg
                    sp_config = {'host': conf.get(spid, 'host'),
                                 'port': conf.getint(spid, 'port'),
                                 'License': conf.get(spid, 'License'),
                                 'app_id': conf.get(spid, 'app_id'),
                                 'user_id': conf.get(spid, 'user_id'),
                                 'password': conf.get(spid, 'password')}
                    set_login_info(**sp_config)
                time.sleep(1)
                login()
                rep_socket.send_string(f'{sp_config["user_id"]}已登入---{arg}')
            else:
                time.sleep(1)
