#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/15 0015 8:59
# @Author  : Hadrianl 
# @File    : sp_data_server.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import os
dirpath = os.path.dirname(__file__)  # 获取模块路径

from spapi.spAPI import *
import zmq
from zmq import Context
import pymysql as pm
import time
from threading import Thread
import configparser
import logging.config
from datetime import datetime
from queue import Queue
import pickle


conf = configparser.ConfigParser()
conf.read(os.path.join(dirpath, 'conf', 'conf.ini'))
loginfo = configparser.ConfigParser()
loginfo.read(os.path.join(dirpath,'conf', 'loginfo.ini'))
logging.config.fileConfig(os.path.join(dirpath,'conf', 'sp_log.conf'))
server_logger = logging.getLogger('root.sp_server')
dbconfig = {'host': conf.get('MYSQL', 'host'),
            'port': conf.getint('MYSQL', 'port'),
            'user': conf.get('MYSQL', 'user'),
            'password': conf.get('MYSQL', 'password'),
            'db': conf.get('MYSQL', 'db'),
            'cursorclass': pm.cursors.DictCursor
            }
ctx = Context()
ticker_socket = ctx.socket(zmq.PUB)
price_socket = ctx.socket(zmq.PUB)
rep_price_socket = ctx.socket(zmq.REP)
rep_socket = ctx.socket(zmq.REP)
ticker_socket.bind(f'tcp://*: {conf.getint("SOCKET_PORT", "ticker_pub")}')
price_socket.bind(f'tcp://*: {conf.getint("SOCKET_PORT", "price_pub")}')
rep_price_socket.bind(f'tcp://*: {conf.getint("SOCKET_PORT", "rep_price_pub")}')
rep_socket.bind(f'tcp://*: {conf.getint("SOCKET_PORT", "handle_rep")}')
conn = pm.connect(**dbconfig)
cursor = conn.cursor()
to_sql_list = set()
sub_ticker_list = set()
sub_price_list = set()

spid = 'SP_ID1'
initialize()
sp_config = {'host': loginfo.get(spid, 'host'),
             'port': loginfo.getint(spid, 'port'),
             'License': loginfo.get(spid, 'License'),
             'app_id': loginfo.get(spid, 'app_id'),
             'user_id': loginfo.get(spid, 'user_id'),
             'password': loginfo.get(spid, 'password')}
set_login_info(**sp_config)
insert_ticker_queue = Queue()

# -----------------------------------------------初始登录的信息回调------------------------------------------------------------------------------
@on_login_reply  # 登录成功时候调用
def reply(user_id, ret_code, ret_msg):
    if ret_code == 0:
        server_logger.info(f'<账户>{user_id.decode()}登录成功')
    else:
        server_logger.error(f'<账户>{user_id.decode()}登录失败--errcode:{ret_code}--errmsg:{ret_msg.decode()}')
    try:
        for t in sub_ticker_list:
            if subscribe_ticker(t, 1) == 0:
                server_logger.info(f'<数据>Ticker-{t}续订成功')
        for p in sub_price_list:
            if subscribe_ticker(p, 1) == 0:
                server_logger.info(f'<数据>Price-{p}续订成功')
    except Exception as e:
        server_logger.info(f'<数据>续订数据失败')

@on_account_login_reply  # 普通客户登入回调
def login_reply(accNo, ret_code, ret_msg):
    if ret_code == 0:
        server_logger.info(f'<账户>{accNo.decode()}登入成功')
    else:
        server_logger.error(f'<账户>{accNo.decode()}登入失败--errcode:{ret_code}--errmsg:{ret_msg.decode()}')

@on_account_logout_reply  # 登出成功后调用
def logout_reply(accNo, ret_code, ret_msg):
    if ret_code == 0:
        server_logger.info(f'<账户>{accNo.decode()}登出成功')
    else:
        server_logger.error(f'<账户>{accNo.decode()}登出失败--errcode:{ret_code}--errmsg:{ret_msg.decode()}')

@on_account_info_push  # 普通客户登入后返回登入前的户口信息
def account_info_push(acc_info):
    server_logger.info(f'<账户>{acc_info.ClientId.decode()}信息--NAV:{acc_info.NAV}-BaseCcy:{acc_info.BaseCcy.decode()}-BuyingPower:{acc_info.BuyingPower}-CashBal:{acc_info.CashBal}')

@on_load_trade_ready_push  # 登入后，登入前已存的成交信息推送
def trade_ready_push(rec_no, trade):
    server_logger.info(f'<成交>历史成交记录--NO:{rec_no}--{trade.OpenClose.decode()}成交@{trade.ProdCode.decode()}--{trade.BuySell.decode()}--Price:{trade.Price}--Qty:{trade.Qty}')

@on_account_position_push  # 普通客户登入后返回登入前的已存在持仓信息
def account_position_push(pos):
    server_logger.info(f'<持仓>历史持仓信息--ProdCode:{pos.ProdCode.decode()}-PLBaseCcy:{pos.PLBaseCcy}-PL:{pos.PL}-Qty:{pos.Qty}-DepQty:{pos.DepQty}')

@on_business_date_reply  # 登录成功后会返回一个交易日期
def business_date_reply(business_date):
    server_logger.info(f'<日期>当前交易日--{datetime.fromtimestamp(business_date)}')
# ------------------------------------------------------------------------------------------------------------------------------------------------------

# ----------------------------------------行情数据主推---------------------------------------------------------------------------------------------------
@on_ticker_update  # ticker数据推送
def ticker_update(ticker):
    ticker_socket.send_pyobj(ticker)
    insert_ticker_queue.put(ticker)

@on_api_price_update  # price数据推送
def price_update(price):
    price_socket.send_pyobj(price)
# -------------------------------------------------------------------------------------------------------------------------------------------------------

@on_connecting_reply  # 连接状态改变时调用
def connecting_reply(host_type, con_status):
    server_logger.info(f'<账户>{HOST_TYPE[host_type]}连接状态改变--{HOST_CON_STATUS[con_status]}')
    if con_status >=3:
        for i in range(3):
            try:
                logout()
                time.sleep(1)
                break
            except Exception:
                ...
        for i in range(3):
            try:
                login()
                server_logger.info(f'<账户>{loginfo.get(spid, "user_id")}-断线重连成功')
                break
            except:
                server_logger.error(f'<账户>{loginfo.get(spid, "user_id")}-断线重连失败')
                time.sleep(3)
        else:
            server_logger.info(f'<账户>{loginfo.get(spid, "user_id")}-断线重连三次失败')

            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.application import MIMEApplication
            me = "LogServer" + "<" + loginfo.get('EMAIL', 'sender') + ">"
            msg = MIMEMultipart()
            msg['Subject'] = 'Server邮件'
            msg['From'] = me
            msg['To'] = "137150224@qq.com"

            txt = MIMEText('断线重连失败', _subtype='plain', _charset='utf-8')
            msg.attach(txt)

            att = MIMEApplication(open('SP_LOG/sp_server.log', 'rb').read())
            att.add_header('Content-Disposition', 'attachment', filename='sp_server.log')
            msg.attach(att)

            smtp = smtplib.SMTP()
            smtp.connect(loginfo.get('EMAIL', 'host'), loginfo.get('EMAIL', 'port'))
            smtp.login(loginfo.get('EMAIL', 'username'), loginfo.get('EMAIL', 'password'))
            smtp.sendmail(me, '137150224@qq.com', msg.as_string())
            smtp.quit()
            del smtplib
            del MIMEText
            del MIMEMultipart
            del MIMEApplication

# -----------------------------------------------登入后的新信息回调------------------------------------------------------------------------------
@on_order_request_failed  # 订单请求失败时候调用
def order_request_failed(action, order, err_code, err_msg):
    server_logger.error(f'<订单>请求失败--ACTION:{action}-@{order.ProdCode.decode()}-Price:{order.Price}-Qty:{order.Qty}-BuySell:{order.BuySell.decode()}      errcode;{err_code}-errmsg:{err_msg.decode()}')

@on_order_before_send_report  # 订单发送前调用
def order_before_snd_report(order):
    server_logger.info(f'<订单>即将发送请求--@{order.ProdCode.decode()}-Price:{order.Price}-Qty:{order.Qty}-BuySell:{order.BuySell.decode()}')

@on_trade_report  # 成交记录更新后回调出推送新的成交记录
def trade_report(rec_no, trade):
    server_logger.info(f'<成交>{rec_no}新成交{trade.OpenClose.decode()}--@{trade.ProdCode.decode()}--{trade.BuySell.decode()}--Price:{trade.Price}--Qty:{trade.Qty}')

@on_updated_account_position_push  # 新持仓信息
def updated_account_position_push(pos):
    server_logger.info(f'<持仓>信息变动--@{pos.ProdCode.decode()}-PLBaseCcy:{pos.PLBaseCcy}-PL:{pos.PL}-Qty:{pos.Qty}-DepQty:{pos.DepQty}')

@on_updated_account_balance_push  # 户口账户发生变更时的回调，新的账户信息
def updated_account_balance_push(acc_bal):
    server_logger.info(f'<账户>信息变动-{acc_bal.Ccy.decode()}-CashBF:{acc_bal.CashBF}-TodayCash:{acc_bal.TodayCash}-NotYetValue:{acc_bal.NotYetValue}-Unpresented:{acc_bal.Unpresented}-TodayOut:{acc_bal.TodayOut}')
# ------------------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------请求回调函数------------------------------------------------------------------------------------
@on_order_report  # 订单报告的回调推送
def order_report(rec_no, order):
    server_logger.info(f'<订单>--编号:{rec_no}-@{order.ProdCode.decode()}-Status:{ORDER_STATUS[order.Status]}')

@on_instrument_list_reply  # 产品系列信息的回调推送，用load_instrument_list()触发
def inst_list_reply(req_id, is_ready, ret_msg):
    if is_ready:
        server_logger.info(f'<产品>信息加载成功      req_id:{req_id}-msg:{ret_msg.decode()}')
    else:
        server_logger.info(f'<产品>信息正在加载......req_id{req_id}-msg:{ret_msg.decode()}')

@on_product_list_by_code_reply  # 根据产品系列名返回合约信息
def product_list_by_code_reply(req_id, inst_code, is_ready, ret_msg):
    if is_ready:
        if inst_code == '':
            server_logger.info(f'<合约>该产品系列没有合约信息      req_id:{req_id}-msg:{ret_msg.decode()}')
        else:
            server_logger.info(f'<合约>产品：{inst_code.decode()}合约信息加载成功      req_id:{req_id}-msg:{ret_msg.decode()}')
    else:
        server_logger.info(f'<合约>产品：{inst_code.decode()}合约信息正在加载......req_id{req_id}-msg:{ret_msg.decode()}')

@on_pswchange_reply  # 修改密码调用
def pswchange_reply(ret_code, ret_msg):
    if ret_code == 0:
        server_logger.info('<密码>修改成功')
    else:
        server_logger.error(f'<密码>修改失败  errcode:{ret_code}-errmsg:{ret_msg.decode()}')
# ---------------------------------------------------------------------------------------------------------------------------------------------------------

def insert_ticker():
    while True:
        try:
            ticker = insert_ticker_queue.get()
            if ticker.ProdCode.decode() in to_sql_list:
                sql = f'insert into futures_tick(prodcode, price, tickertime, qty, dealsrc, decinprice) \
            values ("{ticker.ProdCode.decode()}", {ticker.Price}, "{datetime.fromtimestamp(ticker.TickerTime)}", \
            {ticker.Qty}, {ticker.DealSrc}, "{ticker.DecInPrice.decode()}")'
                cursor.execute(sql)
                conn.commit()
        except pm.Error as e:
            server_logger.info(f'sqlerror:{e}')
            conn.ping()



login()
time.sleep(1)


def get_price():
    while True:
        prodcode = rep_price_socket.recv_string()
        server_logger.info(f'请求{prodcode}数据')
        try:
            price = get_price_by_code(prodcode)
        except Exception:
            price = None
        rep_price_socket.send_pyobj(price)
        server_logger.info(f'发送{prodcode}数据成功')

def to_sql(prodcode, mode):
    if mode == 1:
        to_sql_list.add(prodcode)
    elif mode == 0:
        to_sql_list.remove(prodcode)
    else:
        raise Exception(f'不存在mode:{mode}')

def get_to_sql_list():
    return to_sql_list

def get_sub_ticker_list():
    return sub_ticker_list

def get_sub_price_list():
    return sub_price_list





if __name__ == '__main__':
    from handle_func import handle
    from inspect import isfunction
    is_login = True
    get_price_thread = Thread(target=get_price)
    insert_ticker_thread = Thread(target=insert_ticker)
    get_price_thread.start()
    insert_ticker_thread.start()
    def handle_str_func(_func, _args, _kwargs):
        func = pickle.loads(_func)
        args = pickle.loads(_args)
        kwargs = pickle.loads(_kwargs)
        handle = getattr(sys.modules['__main__'], func, None)
        try:
            if handle:
                ret = handle(*args, **kwargs)
            else:
                raise Exception(f'不存在{func}')
        except Exception as e:
            ret = e
        return ret

    while True:
        if is_login:
            while True:
                _func, _args, _kwargs = rep_socket.recv_multipart()
                func = pickle.loads(_func)

                if isfunction(func):
                    ret = handle(_func, _args, _kwargs)
                    if func.__name__ == 'subscribe_ticker':
                        prodcode, mode = pickle.loads(_args)
                        if mode == 1:
                            sub_ticker_list.add(prodcode)
                        else:
                            sub_ticker_list.remove(prodcode)
                    elif func.__name__ == 'subscribe_price':
                        prodcode, mode = pickle.loads(_args)
                        if mode == 1:
                            sub_price_list.add(prodcode)
                        else:
                            sub_price_list.remove(prodcode)

                elif isinstance(func, str):
                    ret = handle_str_func(_func, _args, _kwargs)

                rep_socket.send_pyobj(ret)




        #         handle = handle.decode()
        #         arg = arg.decode()
        #         server_logger.info(f'{handle}-{arg}')
        #
        #         if handle == 'sub_ticker':
        #             if subscribe_ticker(arg, 1) == 0:
        #                 sub_ticker_list.add(arg)
        #                 rep_text = f'{arg}-Ticker订阅成功'
        #             else:
        #                 rep_text = f'{arg}-Ticker订阅失败'
        #             rep_socket.send_string(rep_text)
        #         elif handle == 'sub_price':
        #             if subscribe_price(arg, 1) == 0:
        #                 sub_price_list.add(arg)
        #                 rep_text = f'{arg}-Price订阅成功'
        #             else:
        #                 rep_text = f'{arg}-Price订阅失败'
        #             rep_socket.send_string(rep_text)
        #         elif handle == 'unsub_ticker':
        #             if subscribe_ticker(arg, 0) == 0:
        #                 sub_ticker_list.remove(arg)
        #                 rep_text = f'{arg}-Ticker取消订阅成功'
        #             else:
        #                 rep_text = f'{arg}-Ticker取消订阅失败'
        #             rep_socket.send_string(rep_text)
        #         elif handle == 'unsub_price':
        #             if subscribe_price(arg, 0) == 0:
        #                 sub_price_list.remove(arg)
        #                 rep_text = f'{arg}-Price取消订阅成功'
        #             else:
        #                 rep_text = f'{arg}-Price取消订阅失败'
        #             rep_socket.send_string(rep_text)
        #         elif handle == 'into_db':
        #             if arg in sub_ticker_list:
        #                 to_sql_list.add(arg)
        #                 rep_text = f'{arg}-启动插入DB'
        #             else:
        #                 rep_text = f'{arg}-未订阅，无法插入DB'
        #             rep_socket.send_string(rep_text)
        #         elif handle == 'outof_db':
        #             try:
        #                 to_sql_list.remove(arg)
        #                 rep_text = f'{arg}-取消插入DB'
        #                 rep_socket.send_string(rep_text)
        #             except KeyError as e:
        #                 rep_text = f'{arg}-不存在插入DB队列中'
        #                 rep_socket.send_string(rep_text)
        #         elif handle in ['to_sql_list', 'sub_ticker_list', 'sub_price_list']:
        #             rep_text = f'{",".join(getattr(sys.modules[__name__], handle, set()))}'
        #             rep_socket.send_string(rep_text)
        #         elif handle == 'check_thread_alive':
        #             rep_text = f'get_price线程运行情况:{get_price_thread.is_alive()}'
        #             rep_socket.send_string(rep_text)
        #         elif handle == 'logout':
        #             logout()
        #             unintialize()
        #             to_sql_list.clear()
        #             sub_ticker_list.clear()
        #             sub_price_list.clear()
        #             is_login = False
        #             rep_text = f'{sp_config["user_id"]}已登出---{arg}'
        #             rep_socket.send_string(rep_text)
        #             break
        #         elif handle == 'login':
        #             rep_text = f'已登录，重复登陆指令未处理'
        #             rep_socket.send_string('已经登录中，请勿重复登陆')
        #         elif handle == 'help':
        #             rep_text = f"""CommandList:
        #             sub_ticker:订阅ticker数据
        #             sub_price:订阅price数据
        #             unsub_ticker:取消订阅ticker数据
        #             unsub_price:取消订阅price数据
        #             into_db:添加ticker数据到数据库
        #             outof_db:取消添加ticker数据到数据库
        #             to_sql_list:正在插入数据库的代码列表
        #             sub_ticker_list:正在订阅ticker的代码列表
        #             sub_price_list:正在订阅price的代码列表
        #             logout:登出
        #             login:登入"""
        #             rep_socket.send_string(rep_text)
        #         else:
        #             rep_text = f'未知指令--{handle}'
        #             rep_socket.send_string('未知指令')
        #         server_logger.info(rep_text)
        # else:
        #     handle, arg = rep_socket.recv_multipart()
        #     handle = handle.decode()
        #     arg = arg.decode()
        #     if handle == 'login':
        #         is_login = True
        #         initialize()
        #         if arg in ['SP_ID1', 'SP_ID2', 'SP_ID3']:
        #             spid = arg
        #             sp_config = {'host': conf.get(spid, 'host'),
        #                          'port': conf.getint(spid, 'port'),
        #                          'License': conf.get(spid, 'License'),
        #                          'app_id': conf.get(spid, 'app_id'),
        #                          'user_id': conf.get(spid, 'user_id'),
        #                          'password': conf.get(spid, 'password')}
        #             set_login_info(**sp_config)
        #         time.sleep(1)
        #         login()
        #         rep_socket.send_string(f'{sp_config["user_id"]}已登入---{arg}')
        #     else:
        #         time.sleep(1)
