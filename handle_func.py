#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/28 0028 9:25
# @Author  : Hadrianl 
# @File    : handle_func.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import pickle

def dumps(func, *args, **kwargs):  # 序列化处理，把函数及其参数序列化
    _func = pickle.dumps(func)
    _args = pickle.dumps(args)
    _kwargs = pickle.dumps(kwargs)
    return _func, _args, _kwargs

def handle(_func, _args, _kwargs):  # 反序列化处理并执行
    func = pickle.loads(_func)
    args = pickle.loads(_args)
    kwargs = pickle.loads(_kwargs)
    try:
        ret = func(*args, **kwargs)
    except Exception as e:
        ret = e
    return ret