#coding=utf-8
#
import sys
import os

path = r'C:\Users\moonq\OneDrive\python\06huobi\demo_python-master'
sys.path.append(path)


from huobi.Util import *
from huobi import HuobiService
from datetime import datetime
from ltc_trade_setting import *
import json
import urllib2

# print "提交限价单接口"
# #print HuobiService.buy(1,"2355","0.01",None,None,BUY)
# print "提交市价单接口"
# #print HuobiService.buyMarket(2,"30",None,None,BUY_MARKET)
# print "取消订单接口"
# #print HuobiService.cancelOrder(1,68278313,CANCEL_ORDER)
# print "获取账号详情"
#print HuobiService.getAccountInfo(ACCOUNT_INFO)
# print "查询个人最新10条成交订单"
print HuobiService.getNewDealOrders(2,NEW_DEAL_ORDERS)
# print "根据trade_id查询order_id"
# print HuobiService.getOrderIdByTradeId(1,274424,ORDER_ID_BY_TRADE_ID)
# print "获取所有正在进行的委托"
# print HuobiService.getOrders(2,GET_ORDERS)
# print "获取订单详情"
# #print HuobiService.getOrderInfo(1,68278313,ORDER_INFO)
# print "限价卖出"
# #print HuobiService.sell(2,"22.1","0.2",None,None,SELL)
# print "市价卖出"
# #print HuobiService.sellMarket(2,"1.3452",None,None,SELL_MARKET)
#
#



# buy = [order for order in HuobiService.getOrders(2,GET_ORDERS) if order['type'] == 1]
# print buy
# if buy[0]['order_amount'] == 1:
#     print '1'
