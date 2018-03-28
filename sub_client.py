#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/15 0015 10:19
# @Author  : Hadrianl 
# @File    : sub_client.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import zmq
from zmq import Context
from threading import Thread
from spapi.spAPI import *
from spapi.handle_func import dumps

server_IP = '192.168.2.237'
poller = zmq.Poller()
ctx = Context()
req_price_socket = ctx.socket(zmq.REQ)
req_price_socket.connect(f'tcp://{server_IP}:6870')

handle_socket = ctx.socket(zmq.REQ)
handle_socket.setsockopt(zmq.SNDTIMEO, 1000)
handle_socket.setsockopt(zmq.RCVTIMEO, 1000)
handle_socket.connect(f'tcp://{server_IP}:6666')


def _s(func, *args, **kwargs):  # 序列化处理，把函数及其参数序列化
    handle_socket.send_multipart([*dumps(func, *args, **kwargs)])
    ret = handle_socket.recv_pyobj()
    if isinstance(ret, Exception):
        raise ret
    return ret

class SubTicker:
    def __init__(self, prodcode, addr=f'tcp://{server_IP}:6868'):
        self._sub_socket = ctx.socket(zmq.SUB)
        self._sub_socket.set_string(zmq.SUBSCRIBE, prodcode)
        self._sub_socket.setsockopt(zmq.RCVTIMEO, 5000)
        self._addr = addr
        self._prodcode = prodcode
        self.__is_active = False
        self.__is_sub = False
        self.__thread = Thread()

    def __run(self, func):
        while self.__is_active:
            try:
                ticker = self._sub_socket.recv_pyobj()
                if ticker.ProdCode.decode() == self._prodcode:
                    func(ticker)
            except zmq.ZMQError:
                ...

    def __call__(self, func):
        self._func = func
        return self

    def start(self):
        if not self.__is_active:
            self.__is_active = True
            self._sub_socket.connect(self._addr)
            self.__thread = Thread(target=self.__run, args=(self._func,))
            self.__thread.setDaemon(True)
            self.__thread.start()

    def stop(self):
        self.__is_active = False
        self.__thread.join()
        self._sub_socket.disconnect(self._addr)

    def is_alive(self):
        return self.__is_active


    def sub(self):
        _s(subscribe_ticker, self._prodcode, 1)
        self.__is_sub = True


    def unsub(self):
        _s(subscribe_ticker, self._prodcode, 0)
        self.__is_sub = False



class SubPrice:
    def __init__(self, prodcode, addr=f'tcp://{server_IP}:6869'):
        self._sub_socket = ctx.socket(zmq.SUB)
        self._sub_socket.set_string(zmq.SUBSCRIBE, prodcode)
        self._sub_socket.setsockopt(zmq.RCVTIMEO, 5000)
        self._addr = addr
        self._prodcode = prodcode
        self.__is_active = False
        self.__is_sub = False
        self.__thread = Thread()

    def __run(self, func):
        while self.__is_active:
            try:
                price = self._sub_socket.recv_pyobj()
                func(price)
            except zmq.ZMQError:
                ...

    def __call__(self, func):
        self._func = func
        return self

    def start(self):
        if not self.__is_active:
            self.__is_active = True
            self._sub_socket.connect(self._addr)
            self.__thread = Thread(target=self.__run, args=(self._func,))
            self.__thread.setDaemon(True)
            self.__thread.start()

    def stop(self):
        self.__is_active = False
        self.__thread.join()
        self._sub_socket.disconnect(self._addr)

    def is_alive(self):
        return self.__is_active

    def sub(self):
        _s(subscribe_price, self._prodcode, 1)
        self.__is_sub = True

    def unsub(self):
        _s(subscribe_price, self._prodcode, 0)
        self.__is_sub = False

    def get_price(self):
        req_price_socket.send_string(self._prodcode)
        price = req_price_socket.recv_pyobj()
        return price


def Login():
    _s(login)


def Logout():
    _s(logout)


def Add_normal_order(ProdCode, BuySell, Qty, Price=None, AO=False, OrderOption=0, ClOrderId='', ):
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
    return _s(add_order, **kwargs)

# def Get_

def into_sql(prodcode):
    _s('to_sql', prodcode, 1)

def outof_sql(prodcode):
    _s('to_sql', prodcode, 0)

def to_sql_list():
    return _s('get_to_sql_list')

def sub_ticker_list():
    return _s('get_sub_ticker_list')

def sub_price_list():
    return _s('get_sub_price_list')

# def check_thread_alive():
#     """
#     查询get_price线程是否alive
#     :return:
#     """
#     handle_socket.send_multipart([b'check_thread_alive', b''])
#     l = handle_socket.recv_string()
#     print(l)


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
    on_price = SubPrice(symbol)
    on_tick.sub()
    on_price.sub()
    into_sql(symbol)
    print(sub_price_list())
    print(sub_ticker_list())