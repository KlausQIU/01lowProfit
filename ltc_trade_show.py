# !/urs/bin/env python
# -*- coding:utf-8 -*-

import sys
import os

append_path = r'C:\Klaus\System\08huobi\demo_python-master'
sys.path.append(append_path)
from huobi.Util import *
from huobi import HuobiService
import urllib2
import json
import time
import threading
from datetime import datetime
import logging
import requests
#from lowProfit.huobi_trade import ltc_trade
from huobi.method_collection import *

__author__ = 'KlausQiu'




getOrders= HuobiService.getOrders(2,GET_ORDERS)
# count = 0 
# for order in getOrders:
#     if order['type'] == 1:
#         count += 1
sellOne_count = [order for order in getOrders if order['type'] == 2]
buyOne_count = [order for order in getOrders if order['type'] == 1]
order = sellOne_count[0]
print sellOne_count[0]

d_money = [0.01,0.02,0.03]
SellOrderPrice = []
for order in sellOne_count:
    SellOrderPrice.append(float_format(float(order['order_price'])))
print 'SELL sellorderprice:',SellOrderPrice
print HuobiService.getOrderInfo(2,sellOne_count[0]['id'],ORDER_INFO)
test_price = [27.69,27.7,27.71,28]
print 'Sell TEST_PRICE:',test_price
for price in test_price:
    if price not in SellOrderPrice:
        print price
        print '1'
    else:
        print price
        print price+0.01
for _ in range(30):
    account_info = HuobiService.getAccountInfo(ACCOUNT_INFO)
    print account_info
    time.sleep(2)
# for i in range(5):
    #     print datetime.now()
#     account_info = HuobiService.getAccountInfo(ACCOUNT_INFO)
#     print datetime.now()
#     print account_info
#     print datetime.now()
#     a_ltc_display = float(account_info['available_ltc_display'])
#     print datetime.now()
#     print a_ltc_display
#     print datetime.now()
#     ticker_ltc = json.loads(urllib2.urlopen(r'http://api.huobi.com/staticmarket/ticker_ltc_json.js',timeout=5).read())
#     print datetime.now()
#     print ticker_ltc

r = requests.get('http://api.huobi.com/staticmarket/ticker_ltc_json.js',timeout=2)
print r
print r.text

print type(r.text)
# print HuobiService.getOrderIdByTradeId(2, 20161020121709, ORDER_ID_BY_TRADE_ID)
# order_info = HuobiService.getOrderInfo(2, 319851575,ORDER_INFO)
# print order_info



        








