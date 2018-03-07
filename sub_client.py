#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/15 0015 10:19
# @Author  : Hadrianl 
# @File    : sub_client.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import zmq
from zmq import Context
from threading import Thread

server_IP = '192.168.2.226'
poller = zmq.Poller()
req_price_ctx = Context()
req_price_socket = req_price_ctx.socket(zmq.REQ)
req_price_socket.connect(f'tcp://{server_IP}:6870')
handle_ctx = Context()
handle_socket = handle_ctx.socket(zmq.REQ)
handle_socket.setsockopt(zmq.SNDTIMEO, 1000)
handle_socket.setsockopt(zmq.RCVTIMEO, 1000)
handle_socket.connect(f'tcp://{server_IP}:6666')


class SubTicker:
    def __init__(self, prodcode, addr=f'tcp://{server_IP}:6868'):
        self._sub_socket = Context().socket(zmq.SUB)
        self._sub_socket.set_string(zmq.SUBSCRIBE, '')
        self._addr = addr
        self._prodcode = prodcode
        self._is_active = False
        self._is_sub = False
        self._thread = Thread()

    def _run(self, func):
        self._sub_socket.connect(self._addr)
        while self._is_active:
            ticker = self._sub_socket.recv_pyobj()
            if ticker.ProdCode.decode() == self._prodcode:
                func(ticker)

    def __call__(self, func):
        self._func = func
        return self

    def start(self):
        if not self._is_active:
            self._is_active = True
            self._thread = Thread(target=self._run, args=(self._func,))
            self._thread.setDaemon(True)
            self._thread.start()

    def stop(self):
        self._is_active = False
        self._sub_socket.disconnect(self._addr)

    def sub(self):
        handle_socket.send_multipart([b'sub_ticker', self._prodcode.encode()])
        self._is_sub = True
        print(handle_socket.recv_string())

    def unsub(self):
        handle_socket.send_multipart([b'unsub_ticker', self._prodcode.encode()])
        self._is_sub = False
        print(handle_socket.recv_string())


class SubPrice:
    def __init__(self, prodcode, addr=f'tcp://{server_IP}:6869'):
        self._sub_socket = Context().socket(zmq.SUB)
        self._sub_socket.set_string(zmq.SUBSCRIBE, '')
        self._addr = addr
        self._prodcode = prodcode
        self._is_active = False
        self._is_sub = False
        self._thread = Thread()

    def _run(self, func):
        self._sub_socket.connect(self._addr)
        while self._is_active:
            price = self._sub_socket.recv_pyobj()
            func(price)

    def __call__(self, func):
        self._func = func
        return self

    def start(self):
        if not self._is_active:
            self._is_active = True
            self._thread = Thread(target=self._run, args=(self._func,))
            self._thread.setDaemon(True)
            self._thread.start()

    def stop(self):
        self._sub_socket.disconnect(self._addr)
        self._is_active = False

    def sub(self):
        handle_socket.send_multipart([b'sub_price', self._prodcode.encode()])
        self._is_sub = True
        print(handle_socket.recv_string())

    def unsub(self):
        handle_socket.send_multipart([b'unsub_price', self._prodcode.encode()])
        self._is_sub = False
        print(handle_socket.recv_string())

    def get_price(self):
        req_price_socket.send_string(self._prodcode)
        price = req_price_socket.recv_pyobj()
        return price


def login(id=''):
    handle_socket.send_multipart([b'login', id.encode()])
    print(handle_socket.recv_string())


def logout(msg=''):
    handle_socket.send_multipart([b'logout', msg.encode()])
    print(handle_socket.recv_string())


def help():
    """
    帮助文档
    :return:
    """
    handle_socket.send_multipart([b'help', b''])
    print(handle_socket.recv_string())


def ticker_into_db(prodcode):
    """
    将prodcode插入到数据库
    :param prodcode: 产品代码
    :return:
    """
    handle_socket.send_multipart([ b'into_db', prodcode.encode()])
    print(handle_socket.recv_string())


def ticker_outof_db(prodcode):
    """
    讲prodcode停止插入数据库
    :param prodcode: 产品代码
    :return:
    """
    handle_socket.send_multipart([b'outof_db', prodcode.encode()])
    print(handle_socket.recv_string())


def to_sql_list():
    """
    获取插入到数据库的代码列表
    :return:
    """
    handle_socket.send_multipart([b'to_sql_list', b''])
    l = handle_socket.recv_string().split(',')
    return l


def sub_ticker_list():
    """
    获取正在订阅ticker的代码列表
    :return:
    """
    handle_socket.send_multipart([b'sub_ticker_list', b''])
    l = handle_socket.recv_string().split(',')
    return l


def sub_price_list():
    """
    获取正在订阅price的代码列表
    :return:
    """
    handle_socket.send_multipart([b'sub_price_list', b''])
    l = handle_socket.recv_string().split(',')
    return l


# while True:
#     try:
#         # price = socket.recv_pyobj(0)
#         # text = f"""Time:{price.Timestamp}
#         # Bid:{price.Bid}   Ask:{price.Ask}
#         # BidQty:{price.BidTicket}   AskQty:{price.AskTicket}"""
#         # print(text)
#         # quote =ticker_sub_socket.recv_pyobj()
#         sockets = dict(poller.poll())
#         if ticker_sub_socket in sockets:
#             ticker = ticker_sub_socket.recv_pyobj()
#             print(f'{datetime.fromtimestamp(ticker.TickerTime)}-Price:{ticker.Price}-Qty:{ticker.Qty}')
#         if price_sub_socket in sockets:
#             price = price_sub_socket.recv_pyobj()
#             text = f"""Time:{price.Timestamp}
#             Bid:{price.Bid}   Ask:{price.Ask}
#             BidQty:{price.BidTicket}   AskQty:{price.AskTicket}"""
#             print(text)
#     except Exception as e:
#         print(e)

if __name__ == '__main__':
    import datetime as dt
    MONTH_LETTER_MAPS = {1: 'F',
                         2: 'G',
                         3: 'H',
                         4: 'J',
                         5: 'K',
                         6: 'M',
                         7: 'N',
                         8: 'Q',
                         9: 'U',
                         10: 'V',
                         11: 'X',
                         12: 'Z'
                         }
    symbol = 'HSI' + MONTH_LETTER_MAPS[dt.datetime.now().month] + str(dt.datetime.now().year)[-1]
    on_tick = SubTicker(symbol)
    on_tick.sub()
    ticker_into_db(symbol)