#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/15 0015 10:19
# @Author  : Hadrianl 
# @File    : sub_client.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import zmq
from zmq import Context
from datetime import datetime
from threading import Thread
poller = zmq.Poller()
# ctx1 = Context()
# ticker_sub_socket = ctx1.socket(zmq.SUB)
# ticker_sub_socket.connect('tcp://192.168.2.226:6868')
# ticker_sub_socket.setsockopt_unicode(zmq.SUBSCRIBE, '')
# poller.register(ticker_sub_socket, zmq.POLLIN)
# ctx2 = Context()
# price_sub_socket = ctx2.socket(zmq.SUB)
# price_sub_socket.connect('tcp://192.168.2.226:6869')
# price_sub_socket.setsockopt_unicode(zmq.SUBSCRIBE, '')
# poller.register(price_sub_socket, zmq.POLLIN)
ctx3 = Context()
req_price_socket = ctx3.socket(zmq.REQ)
req_price_socket.connect('tcp://192.168.2.226:6870')
ctx4 = Context()
handle_socket = ctx4.socket(zmq.REQ)
handle_socket.connect('tcp://192.168.2.226:6666')

class sub_ticker:
    def __init__(self, prodcode, addr='tcp://192.168.2.226:6868'):
        self._sub_socket = Context().socket(zmq.SUB)
        self._sub_socket.set_string(zmq.SUBSCRIBE, '')
        self._addr = addr
        self._prodcode = prodcode
        self._is_active = False
        self._is_sub = False

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
        if self._is_active == False:
            self._is_active = True
            self._thread.is_alive()
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


class sub_price:
    def __init__(self,prodcode, addr='tcp://192.168.2.226:6869'):
        self._sub_socket = Context().socket(zmq.SUB)
        self._sub_socket.set_string(zmq.SUBSCRIBE, '')
        self._addr = addr
        self._prodcode = prodcode
        self._is_active = False
        self._is_sub = False

    def _run(self, func):
        self._sub_socket.connect(self._addr)
        while self._is_active:
            price = price_sub_socket.recv_pyobj()
            func(price)

    def __call__(self, func):
        self._func = func
        return self

    def start(self):
        if self._is_active == False:
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

def login(msg=''):
    handle_socket.send_multipart([b'login', msg.encode()])
    print(handle_socket.recv_string())

def logout(msg=''):
    handle_socket.send_multipart([b'logout', msg.encode()])
    print(handle_socket.recv_string())



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