#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/26 0026 11:22
# @Author  : Hadrianl 
# @File    : setup


from setuptools import setup, find_packages


setup(name='spapi',
      version='1.1',
      description='HK SharpPoint API - Python',
      author='Hadrianl',
      author_email='137150224@qq.com',
      url='https://github.com/hadrianl/spapi',
      packages = find_packages(),
      include_package_data=True,
      )