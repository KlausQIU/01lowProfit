#!/usr/bin/env python
#coding=utf-8

import sys
import os

from setting import append_path

sys.path.append(append_path)

from Setting.setting import *
from huobi.Util import *
from huobi import HuobiService
from huobi import method_collection
import urllib2,json,time,threading
from datetime import datetime
from DT_strategy.dual_thrust import handler_data
import requests
from huobi.method_collection import *
from collections import Counter
from db import db_control

__author__ = 'KlausQiu'

#火币网莱特币交易主程序
class ltc_trade():
    def __init__(self):
        #获取行情
        self.ticker_ltc = requests.get(r'http://api.huobi.com/staticmarket/ticker_ltc_json.js',timeout=5).json()
        #获取账户信息
        self.account_info = HuobiService.getAccountInfo(ACCOUNT_INFO)
        #所有委托单。huobi设了上限为50个
        self.getOrder = HuobiService.getOrders(2,GET_ORDERS)
        #卖单数量
        self.sellOne_count = [order for order in self.getOrder if order['type'] == 2]
        #买单数量
        self.buyOne_count = [order for order in self.getOrder if order['type'] == 1]
        #已完成的委托
        #self.dealOrders =  HuobiService.getNewDealOrders(2,NEW_DEAL_ORDERS)
        #资产折合
        self.total = float(self.account_info['total'])
         #卖一价
        self.limit_price = self.ticker_ltc['ticker']['sell']
        #买一价
        self.buyone_price = self.ticker_ltc['ticker']['buy']
        #总量
        self.trade_total = self.ticker_ltc['ticker']['vol']
        #限制挂单数量
        self.orderCount = self.handler_orderCount()
        #可用资金
        self.a_cny_display = float(self.account_info['available_cny_display'])
        #可用莱特币
        self.a_ltc_display = float(self.account_info['available_ltc_display'])
        #数据库操作
        self.db = db_control()
                
        # self.SellOneOrders = self.SellOneOrders if self.SellOneOrders else []
        # self.SellOneOrders = self.handler_SellOne_order()
           
    #获取订单详情
    def orderInfo(self,orderId):
        order_info = HuobiService.getOrderInfo(2,orderId,ORDER_INFO)
        return order_info

    #处理买一的卖出
    def handler_buyOne_sell(self,buyOneOrders):
        global buy_count
        print u'handler_buyOne_Sell---->>>BEGIN'
        try:
            ticker = requests.get(r'http://api.huobi.com/staticmarket/ticker_ltc_json.js',timeout=5)
            ticker_ltc = ticker.json()
            buyOne_price = ticker_ltc['ticker']['buy']
        except BaseException as e:
            print 'handler buyone sell ',e
            return 
        if buyOneOrders:

            SellOrderPrice = []
            for order in self.sellOne_count:
                if float(order['order_amount']) == buy_count:
                    SellOrderPrice.append(float_format(order['order_price']))

            buyOneOrders.sort(key=lambda i:float(i['buy_price']),reverse=True)
            for buyOrder in buyOneOrders:
                try:
                    order_info = self.orderInfo(buyOrder['order_id'])
                except BaseException as e:
                    print u'orderInfo wrong,',e
                    return 

                if float(buyOrder['buy_price'])+0.05 < buyOne_price and float(buyOrder['buy_count']) == buy_count:
                    print u'当前买1价:',buyOne_price
                    method_collection.cancel_order(buyOrder['order_id'])
                    print u'取消单价格:%s'%buyOrder['buy_price']
                    buyOneOrders.remove(buyOrder)
                    self.buyOneOrders = buyOneOrders
                    if not self.buyOneOrders:
                        self.buyOneOrders = []

                if float(buyOrder['buy_price']) == buyOne_price:
                    print u"买1 买一价还是:%s"%buyOne_price

                if order_info:
                    if order_info.has_key('status'):
                        if order_info['status'] == 2:
                            print u'买1 买入价格:%s 已买入成功 委托卖出'%order_info['order_price']
                            d_money = [0.01,0.02,0.03]
                            print 'SELL sellorderprice:',sorted(SellOrderPrice)
                            test_price = [float_format(float(order_info['order_price'])+n) for n in d_money]
                            print 'Sell TEST_PRICE:',test_price

                            if set(test_price).issubset(set(SellOrderPrice)):
                                msg = u'超买！！!价格:%.2f \n'%test_price
                                method_collection.record_log(msg)


                            for price in test_price:
                                if price not in SellOrderPrice:
                                    print price
                                    SellResult = method_collection.ltc_sell(price,order_info['processed_amount'])
                                    if SellResult:
                                        self.SellOneOrders.append({'sell_price':SellResult[0],'sell_count':SellResult[1],'order_id':SellResult[2]})
                                        SellOrderPrice.append(price)
                                break

                            #如果不幸发生超买，那+0.04卖出
                            control = False    
                            if set(test_price).issubset(set(SellOrderPrice)):
                                control = True
                                    
                            if control:
                                sell_price = method_collection.float_format(float(order_info['order_price'])) + 0.5
                                msg = u'control Order price:%s'%sell_price
                                print msg
                                method_collection.ltc_sell(sell_price,order_info['processed_amount'])
                                method_collection.record_log(msg)

                            #删除对应的order元素
                            buyOneOrders.remove(buyOrder)
                            self.buyOneOrders = buyOneOrders
                            
                            if not self.buyOneOrders:
                                self.buyOneOrders = []
                            method_collection.record_log("\n%s"%order_info)
                                                  
                        #手动取消的单移出列表
                        elif order_info['status'] == 3:
                            print u'买单已取消 买入价格:%s'%order_info['order_price']
                            buyOneOrders.remove(buyOrder)
                            self.buyOneOrders = buyOneOrders
                            if not self.buyOneOrders:
                                self.buyOneOrders = []

                    if not order_info.has_key('status'):
                        print u'orderinfo 返回异常'

                if float(buyOrder['buy_price']) < buyOne_price:
                    print u'委托单价格: %.2f 挂单排队'%float(buyOrder['buy_price'])

        print u'handler_buyOne_sell---->>>END'

    #生成买单列表
    def handler_buyOne_order(self):
        if not self.buyOneOrders:
            if self.buyOne_count:
                for order in self.buyOne_count:
                    if float_format(order['order_amount']) == float_format(buy_count):
                        self.buyOneOrders.append({'buy_price':order['order_price'],'buy_count':order['order_amount'],'order_id':order['id']})
        return self.buyOneOrders

    #生成卖单列表
    def handler_SellOne_order(self):
        if not self.SellOneOrders:
            if self.sellOne_count:
                for order in self.sellOne_count:
                    buy_price = self.ticker_ltc['ticker']['buy']
                    if method_collection.float_format(buy_price)+0.1 >= method_collection.float_format(order['order_price']):
                        self.SellOneOrders.append({'sell_price':order['order_price'],'sell_count':order['order_amount'],'order_id':order['id']})
        return self.SellOneOrders

    #根据交易量决定挂单数。
    def handler_orderCount(self):
        #交易总量控制
        if total_dict:
            total_key = sorted([k for k in total_dict],reverse = True)
            for i in range(len(total_key)+1):
                if i == 0:
                    if self.trade_total >= total_key[i]:
                        orderCount = total_dict[total_key[i]]
                else:
                    if total_key[i-1] > self.trade_total >= total_key[i]:
                        orderCount = price_dict[total_key[i]]
        #价格控制
        if price_dict:
            total_key = sorted([k for k in price_dict],reverse = True)
            for i in range(len(total_key)+1):
                if i == 0:
                    if self.buyone_price >= total_key[i]:
                        orderCount = price_dict[total_key[i]]
                else:
                    if total_key[i-1] > self.buyone_price >= total_key[i]:
                        orderCount = price_dict[total_key[i]]
        return orderCount

    def handler_sellOne(self,SellOneOrders):
        if SellOneOrders:
            for SellOrder in SellOneOrders:
                try:
                    order_info = self.orderInfo(SellOrder['order_id'])
                except BaseException as e:
                    print u'orderInfo wrong,',e
                    return 
                if order_info:
                    if order_info.has_key('status'):
                        if order_info['status'] == 2 or order_info['status'] == 3:
                            SellOneOrders.remove(SellOrder)
        return SellOneOrders

    def handler_buy(self,buy_price):
        d_money = [0.01,0.02,0.03]

        #上方挂单
        test_price = [float_format(float(buy_price)+n) for n in d_money]
        print u'测试价格:',test_price

        #当前卖单价格列表
        if self.sellOne_count:
            for order in self.sellOne_count:
                if float_format(float(order['order_price'])) in test_price and float(order['order_amount']) == buy_count:
                    SellOrderPrice.append(float_format(order['order_price']))

        #买单列表(非当前，防超买)
        BuyOrderPrice = []
        for order in self.buyOneOrders:
            BuyOrderPrice.append(float_format(order['buy_price']))

        #清理重复的买单
        repeatBuyOrder = method_collection.listRepeat(BuyOrderPrice if BuyOrderPrice else [])
        if repeatBuyOrder:
            for key in repeatBuyOrder:
                method_collection.cancel_order(order['order_id'] for order in self.buyOne_count if order['order_price'] == key)

        print u'limit_buy BuyOrderPrice:',sorted(BuyOrderPrice)
        print u'limit_buy SellOrderPrice:',sorted(SellOrderPrice)

        #触发够买条件和防超买
        control = False
        superCount = 0
        for price in test_price:
            if price not in SellOrderPrice and buy_price not in BuyOrderPrice:
                control = True

            if price in SellOrderPrice and buy_price == max(BuyOrderPrice) if BuyOrderPrice else None:
                superCount += 1

        if superCount >= 3:
            for order in self.buyOneOrders:
                if order['buy_price'] == buy_price:
                    method_collection.cancel_order(order['order_id'])
                    print u'超买取消单:%s'%order['buy_price']
                    method_collection.record_log(u'超买取消单:%s'%order['buy_price'])
                    self.buyOneOrders.remove(order)
                
        if control:
            buy_result = method_collection.ltc_buy(buy_price, buy_count,)
            if buy_result:
                self.buyOneOrders.append({'buy_price':buy_result[0],'buy_count':buy_result[1],'order_id':buy_result[2]})
                #self.db.insert('BUYORDER','Time',buy_result[2],buy_result[0],buy_result[1],None)
                return
            else:
                print u'没买成功.%s'%buy_price
                self.handler_buyOne_sell(self.buyOneOrders)
                return 

        #下方挂买单
        # d_money.append(0.04)
        listBuyPrice = [float_format(float(buy_price)-n) for n in d_money]
        print 'listBuyPrice:',listBuyPrice
        for x in listBuyPrice:
            if x not in [float(order['buy_price']) for order in self.buyOneOrders]:
                buy_result = method_collection.ltc_buy(x, buy_count,)
                if buy_result:
                    self.buyOneOrders.append({'buy_price':buy_result[0],'buy_count':buy_result[1],'order_id':buy_result[2]})
        self.handler_buyOne_sell(self.buyOneOrders)

    #限制购买次数
    def limit_buy_count(self,buy_price,buy_count,):
        print u'limit_buy_count---->>>BEGIN'
                
        if len(self.buyOne_count) == 0 and self.a_ltc_display == 0:
            print u'买1 没有委托单,尝试买入'
            buy_result = method_collection.ltc_buy(buy_price, buy_count,)
            if buy_result:
                self.buyOneOrders.append({'buy_price':buy_result[0],'buy_count':buy_result[1],'order_id':buy_result[2]})
                self.handler_buyOne_sell(self.buyOneOrders)

        # elif len(self.buyOne_count) == 0 and self.a_ltc_display > 0:
        #     self.buyOneOrders = self.handler_buyOne_order()
        #     self.handler_buyOne_sell(self.buyOneOrders)

        elif len(self.buyOne_count) >= 1 or len(self.sellOne_count) >= 0:
            self.handler_buy(buy_price,)
    
        else:
            self.handler_buyOne_order()
            msg = u'已在同一价格购买超过1次，不再购买\n'
            msg = u'买1 ' + msg
            print msg
            time.sleep(2)
        print u'limit_buy_count------>>>>>END'
                
    #限制委托单
    def handler_getOrders(self):
        global buy_count
        print u'handler_getOrders---->>>BEGIN'  
        # buy_count = self.handler_buy_count(buy_price,buy_count)
        if self.getOrder:
            if len(self.sellOne_count) >= self.orderCount:
                print u'委托超过%s个'%self.orderCount
                print u'监控所有买单'
                for order in self.buyOneOrders:
                    print order
                self.buyOneOrders = self.handler_buyOne_order()
                self.handler_buyOne_sell(self.buyOneOrders)
                time.sleep(10)
            elif  0 < len(self.sellOne_count) < self.orderCount:
                buy_price = self.ticker_ltc['ticker']['buy']
                self.limit_buy_count(buy_price,buy_count,)
        elif len(self.getOrder) == 0:
                buy_price = self.ticker_ltc['ticker']['sell']
                buy_result = method_collection.ltc_buy(buy_price, buy_count,)
                if buy_result:
                    self.buyOneOrders.append({'buy_price':buy_result[0],'buy_count':buy_result[1],'order_id':buy_result[2]})
                    self.handler_buyOne_sell(self.buyOneOrders)
        print u'handler_getOrders----->>>>END'
                        

    def start(self):
        self.buyOneOrders = []
        self.SellOneOrders = []
        # while True:
        #     self.run()
        #     continue
        self.run()

    #主运行程序，策略判断买入卖出
    def run(self):
        with open(path,'r') as c:
            if c.read() == 'True':
                print u'\nRUN---->>>BEGIN'
                method_collection.display_time()
                try:
                    self.__init__()
                except BaseException as e:
                    print u'无法初始化',e
                    return 

                self.buyOneOrders = self.handler_buyOne_order()

                #print u'当前成交量:',self.trade_total
                print u'当前委单数: ',len(self.getOrder) if self.getOrder else None,u'单'
                if self.limit_price >= over_high_price:
                    print u'当前价格:%s 已超过指定金额'%self.limit_price
                    time.sleep(200)
                elif self.limit_price <= over_low_price:
                    print u'当前价格:%s 已低于指定金额,'%self.limit_price
                    time.sleep(200)
                else:
                    self.handler_getOrders()
                print u'RUN----------------->>>>>>END'
                    

#多线程运行，把不同的委托单任务往里面扔然后运行，适合浮动较快的场景
def threading_run(target,args):
    if target:
        t = threading.Thread(target=target,args=args)
        threads.append(t)

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    method_collection.crucifix()
    method_collection.liquidation_price()
    ltc_trade = ltc_trade()
    #method_collection.DT_buy(key)
    #threading_run(method_collection.run_or_not,())
    #threading_run(ltc_trade.start,('sell_1',))
    # threading_run(ltc_trade.start,('buy_1',)) 
    # for t in threads:
    #     t.setDaemon(True)
    #     t.start()
    # t.join()
    ltc_trade.__init__()
    ltc_trade.start()
    print ltc_trade.getOrder
    print ltc_trade.handler_buyOne_order()

#python C:\Klaus\System\08huobi\demo_python-master\lowProfit\huobi_trade.py
#python  C:\Users\moonq\OneDrive\python\06huobi\demo_python-master\lowProfit\huobi_trade.py
