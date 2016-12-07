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
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
for order in buyOne_count:
    result = cancel_order(order['id'])
    print result
    time.sleep(2)





        








