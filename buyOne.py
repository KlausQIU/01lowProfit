#!/usr/bin/env python
#coding=utf-8

import sys
import os

append_path = r'C:\Klaus\System\08huobi\demo_python-master'
sys.path.append(append_path)

from Setting.setting import *
from huobi.Util import *
from huobi import HuobiService
from huobi import method_collection
import urllib2,json,time,threading
from datetime import datetime
from DT_strategy.dual_thrust import handler_data

__author__ = 'KlausQiu'

#火币网莱特币交易主程序
class ltc_trade():
    def __init__(self):
        try:
            self.ticker_ltc = json.loads(urllib2.urlopen(r'http://api.huobi.com/staticmarket/ticker_ltc_json.js').read())
            self.account_info = HuobiService.getAccountInfo(ACCOUNT_INFO)
            self.getOrder = HuobiService.getOrders(2,GET_ORDERS)
            #卖单数量
            self.sellOne_count = [order for order in self.getOrder if order['type'] == 2]
            #买单数量
            self.buyOne_count = [order for order in self.getOrder if order['type'] == 1]
            #已完成的委托
            self.dealOrders =  HuobiService.getNewDealOrders(2,NEW_DEAL_ORDERS)
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
        except BaseException as e:
            print u'无法获取数据',e
           

    #处理卖1的卖出
    def handler_sell(self,sell_price,sell_count,trade_id):
        sell_price += 0.01
        #没有买入成功就撤单
        getOrders = HuobiService.getOrders(2,GET_ORDERS)
        order_id = HuobiService.getOrderIdByTradeId(2, trade_id, ORDER_ID_BY_TRADE_ID)
        if getOrders:
            for order in getOrders:
                if order['type'] == 1 and order['id'] == order_id['order_id']:
                    method_collection.cancel_order(order['id'])
        sell_count = self.handler_sell_count(sell_count)
        method_collection.ltc_sell(sell_price,sell_count)

    #处理买一的卖出
    def handler_buyOne_sell(self,sell_price,sell_count,trade_id):
        sell_price += 0.01
        order_id = (HuobiService.getOrderIdByTradeId(2, trade_id, ORDER_ID_BY_TRADE_ID))['order_id'] if trade_id else self.buyOne_count[0]['id']
        if order_id:
            while True:
                order_info = HuobiService.getOrderInfo(2,order_id,ORDER_INFO)
                try:
                    surplus_count = HuobiService.getAccountInfo(ACCOUNT_INFO)['available_ltc_display']
                    if order_info['status'] == 0 or order_info['status'] == 1:
                        ticker_ltc = json.loads(urllib2.urlopen(r'http://api.huobi.com/staticmarket/ticker_ltc_json.js').read())
                        test_price = ticker_ltc['ticker']['buy']
                        if float(order_info['order_price']) == test_price:
                            print u'买1 当前买1价还是:%s\n'%test_price
                            time.sleep(2)
                        elif float(order_info['order_price'])+0.01 < test_price:
                            print u'买1 买单已往下，取消之\n'
                            method_collection.cancel_order(order_id)
                            break
                        elif float(order_info['order_price']) < test_price:
                            break
                        elif float(order_info['order_amount']) > float(order_info['processed_amount']) > 0.0000:
                            print u'买1 成交了%s\n'%order_info['processed_amount']
                            sell_count = self.handler_sell_count(order_info['processed_amount'])
                            method_collection.ltc_sell(sell_price,sell_count)
                            break
                    elif order_info['status'] == 2 and float(surplus_count) == 0.0000:
                        print u'买1 这单是卖1的\n'
                        break
                    elif order_info['status'] == 2 and float(surplus_count) > 0.0000:
                        msg =  u'买1 已成交 尝试挂单卖出\n'
                        print msg
                        sell_count = self.handler_sell_count(order_info['processed_amount'])
                        method_collection.ltc_sell(sell_price,sell_count)
                        break
                    else:
                        print u'有其他情况，清注意'
                        break
                except BaseException as e:
                    print u'买1 暂时无法获取数据',e
                time.sleep(2)
                continue

    #处理买单数量
    def handler_buy_count(self,buy_price,buy_count):
        try:
            yesterday = json.loads(urllib2.urlopen(r'http://api.huobi.com/staticmarket/ltc_kline_100_json.js').read())
        except:
            print u'无法获取昨日数据'
        #昨天的最高价
        if yesterday:
            yesterday_total = yesterday[-2][2]
            #昨天的最低价
            yesterday_low = yesterday[-2][3]
            if buy_price >= yesterday_total:
                buy_count -= 0.05
            if buy_price < yesterday_low:
                buy_count += 0.01
            return buy_count    


    #处理卖出数量
    def handler_sell_count(self,buy_count):
        sell_count = HuobiService.getAccountInfo(ACCOUNT_INFO)['available_ltc_display']
        if sell_count == u'0.0000':
            return None
        else:
            if sell_count > buy_count:
                return buy_count
            else:
                return sell_count


    #根据交易量决定挂单数。
    def handler_orderCount(self):
    #二选一个控制即可
        if total_dict:
            total_key = sorted([k for k in total_dict],reverse = True)
            for i in range(len(total_key)+1):
                if i == 0:
                    if self.trade_total >= total_key[i]:
                        orderCount = total_dict[total_key[i]]
                else:
                    if total_key[i-1] > self.trade_total >= total_key[i]:
                        orderCount = price_dict[total_key[i]]
        if price_dict:
            total_key = sorted([k for k in price_dict],reverse = True)
            for i in range(len(total_key)+1):
                if i == 0:
                    if self.limit_price >= total_key[i]:
                        orderCount = price_dict[total_key[i]]
                else:
                    if total_key[i-1] > self.limit_price >= total_key[i]:
                        orderCount = price_dict[total_key[i]]
        return orderCount

    #限制购买次数
    def limit_buy_count(self,buy_price,buy_count,buy_type):
        count = 0
        test_price = float(buy_price)+0.01
        print 'test price:',test_price
        #卖单里同一个价格还没卖出去，就不买  
        for order in self.sellOne_count:
            if '%.2f'%float(order['order_price']) == '%.2f'%(test_price) and float(order['order_amount']) == buy_count:
                count += 1
        print 'count:',count
        if 0 <= count < buyCount:
            if buy_type == 'buy_1':
                if len(self.buyOne_count) == 0 :
                    print u'买1 没有委托单,尝试买入'
                    buy_result = method_collection.ltc_buy(buy_price, buy_count,buy_type)
                    if buy_result:
                        self.handler_buyOne_sell(buy_result[0], buy_result[1], buy_result[2])
                elif len(self.buyOne_count) >= 1:
                    count = 0
                    for order in self.buyOne_count:
                        if float(order['order_amount']) ==  buy_count and float(order['order_price']) == float(buy_price):
                            count += 1
                        if float(order['order_amount']) ==  buy_count and float(order['order_price'])+0.02 < float(buy_price):
                            method_collection.cancel_order(order['id'])
                    if count >= buyCount:
                        print u'买1 已有买单，侦测目前状态'
                        self.handler_buyOne_sell(buy_price,buy_count,None)
                    else:
                        buy_result = method_collection.ltc_buy(buy_price, buy_count,buy_type)
                        if buy_result:
                            self.handler_buyOne_sell(buy_result[0], buy_result[1], buy_result[2])
            elif buy_type == 'sell_1':
                print u'卖1 下跌，正在尝试买入\n'
                # buy_count = self.handler_buy_count(second_price,buy_count)
                buy_result = method_collection.ltc_buy(buy_price, buy_count,buy_type)
                if buy_result:
                    self.handler_sell(buy_result[0], buy_result[1], buy_result[2])
        else:
            msg = u'已在同一价格购买超过1次，不再购买\n'
            msg = u'卖1 ' + msg if buy_type == 'sell_1' else u'买1 ' + msg
            print msg
            time.sleep(20)


    #限制委托单
    def handler_getOrders(self,buy_type):
        global buy_count
        if buy_type == 'buy_1':
            print u'正在进入买1通道\n'  
            # buy_count = self.handler_buy_count(buy_price,buy_count)
            if len(self.getOrder) >= self.orderCount:
                print u'买1 委托超过%s个\n'%self.orderCount
                time.sleep(60)
            elif len(self.getOrder) == 0:
                buy_price = self.ticker_ltc['ticker']['sell']
                buy_result = method_collection.ltc_buy(buy_price, buy_count,buy_type)
                if buy_result:
                    self.handler_buyOne_sell(buy_result[0], buy_result[1], buy_result[2])
            elif  0 < len(self.getOrder) < self.orderCount:
                buy_price = self.ticker_ltc['ticker']['buy']
                self.limit_buy_count(buy_price,buy_count,buy_type)

        if buy_type == 'sell_1':
            print u'正在进入卖1通道\n'
            #没有订单的情况下，先来一发。直接成交卖1。
            method_collection.show_cost_price(total_money)
            if len(self.sellOne_count) == 0:
                print u'卖1 没有委托单,尝试买入'
                buy_price = self.ticker_ltc['ticker']['sell']
                #buy_count = self.handler_buy_count(buy_price,buy_count)
                buy_result = method_collection.ltc_buy(buy_price, buy_count,buy_type)
                if buy_result:
                    self.handler_sell(buy_result[0], buy_result[1], buy_result[2])


            #委托单超过x个，那停止交易。万一是大跌呢。PS：如果是大涨是会不断赚一分钱的所以不担心
            if len(self.sellOne_count) >= self.orderCount:
                print u'卖1 委托超过%s个\n'%self.orderCount
                time.sleep(60)
            #委托单x个内，那继续下委托吧。
            if 0< len(self.sellOne_count) < self.orderCount:
                sell_price = self.ticker_ltc['ticker']['sell']
                print u'卖1 当前卖一价:%0.2f\n'%sell_price
                time.sleep(2)
                #发现有时候获取数据的网址有打不开的时候，所以，加个报错以免直接挂掉了。
                try:
                    ticker_ltc = json.loads(urllib2.urlopen(r'http://api.huobi.com/staticmarket/ticker_ltc_json.js').read())
                except:
                    print u'卖1 无法获取数据'
                if ticker_ltc:
                    second_price = ticker_ltc['ticker']['sell']
                    if sell_price == second_price:
                        print u'卖1 价格没有变化\n'
                    if sell_price < second_price:
                        print u'卖1 币价上涨\n'
                    if sell_price > second_price:
                        self.limit_buy_count(second_price,buy_count,buy_type)

    #主运行程序，策略判断买入卖出
    def start(self,buy_type):
        while True:
            method_collection.liquidation_price()
            test_money_result = method_collection.test_money()
            if test_money_result['msg'] == 'success':
                time.sleep(100000)
            else:
                with open(path,'r') as c:
                    if c.read() == 'True':
                        self.__init__()
                        method_collection.display_time()
                        print u'当前成交量:',self.trade_total
                        print u'当前委单数: ',len(self.getOrder),u'单'
                        #成交量大于1100万的时候，量太大的时候要么暴跌要么爆涨
                        if self.trade_total > limit_total:
                            print u'成交量超过%s，中止交易'%(limit_total)
                            time.sleep(200)
                        elif self.limit_price >= over_high_price:
                            print u'当前价格:%s 已超过指定金额'%self.limit_price
                            time.sleep(200)
                        elif self.limit_price <= over_low_price:
                            print u'当前价格:%s 已低于指定金额,'%self.limit_price
                            time.sleep(200)
                        else:
                            self.handler_getOrders(buy_type)
            continue

#多线程运行，把不同的委托单任务往里面扔然后运行，适合浮动较快的场景
def threading_run(target,args):
    if target:
        t = threading.Thread(target=target,args=args)
        threads.append(t)

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    ltc_trade = ltc_trade()
    threads = []
    method_collection.DT_buy(key)
    threading_run(method_collection.run_or_not,())
    #threading_run(ltc_trade.start,('sell_1',))
    threading_run(ltc_trade.start,('buy_1',)) 
    for t in threads:
        t.setDaemon(True)
        t.start()
    t.join()

#python C:\Klaus\System\08huobi\demo_python-master\lowProfit\huobi_trade.py
#python  C:\Users\moonq\OneDrive\python\06huobi\demo_python-master\lowProfit\huobi_trade.py
