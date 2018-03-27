#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/15 0015 10:19
# @Author  : Hadrianl 
# @File    : sub_client.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import zmq
from zmq import Context
from threading import Thread
import pickle
from spAPI import *

server_IP = '192.168.2.226'
poller = zmq.Poller()
ctx = Context()
req_price_socket = ctx.socket(zmq.REQ)
req_price_socket.connect(f'tcp://{server_IP}:6870')

handle_socket = ctx.socket(zmq.REQ)
handle_socket.setsockopt(zmq.SNDTIMEO, 1000)
handle_socket.setsockopt(zmq.RCVTIMEO, 1000)
handle_socket.connect(f'tcp://{server_IP}:6666')


def _s(func, *args, **kwargs):  # 序列化处理，把函数及其参数序列化
    func = pickle.dumps(func)
    args = pickle.dumps(args)
    kwargs = pickle.dumps(kwargs)
    handle_socket.send_multipart([func, args, kwargs])
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
    handle_socket.send_multipart([*_s(login)])
    print(handle_socket.recv_pyobj())


def Logout():
    handle_socket.send_multipart([*_s(logout)])
    print(handle_socket.recv_pyobj())


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

def help():
    """
    帮助文档
    :return:
    """
    handle_socket.send_multipart([b'help', b''])
    print(handle_socket.recv_pyobj())


def ticker_into_db(prodcode):
    """
    将prodcode插入到数据库
    :param prodcode: 产品代码
    :return:
    """
    def func(prodcode):
        to_sql_list.add(prodcode)
    handle_socket.send_multipart([*_s(func, prodcode)])
    print(handle_socket.recv_pyobj())


def ticker_outof_db(prodcode):
    """
    讲prodcode停止插入数据库
    :param prodcode: 产品代码
    :return:
    """
    def func(prodcode):
        to_sql_list.add(prodcode)
    handle_socket.send_multipart([*_s(func, prodcode)])
    print(handle_socket.recv_pyobj())


def to_sql_list():
    """
    获取插入到数据库的代码列表
    :return:
    """
    def func():
        return to_sql_list
    handle_socket.send_multipart([*_s(func)])
    l = handle_socket.recv_pyobj()
    return l


def sub_ticker_list():
    """
    获取正在订阅ticker的代码列表
    :return:
    """
    def func():
        return sub_ticker_list
    handle_socket.send_multipart([*_s(func)])
    l = handle_socket.recv_pyobj()
    return l


def sub_price_list():
    """
    获取正在订阅price的代码列表
    :return:
    """
    def func():
        return sub_price_list
    handle_socket.send_multipart([*_s(func)])
    l = handle_socket.recv_pyobj()
    return l

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
    ticker_into_db(symbol)