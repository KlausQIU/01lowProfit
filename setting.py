# !/urs/bin/env python
#  -*- coding:utf-8 -*-
#
__author__ = 'KlausQiu'


#每次购买的数量:
buy_count = 1

#DT策略需要的参数，不改
key = -2

#你投入的总金额
total_money = 500

#以下二选一个控制即可
#根据成交量决定可以委托的数量
#格式如：total_dict = {50000000:2,30000000:6,15000000:20,0:25}
#如果不设置请保留，删除大括号中间的数字即可

total_dict = {}

#根据价格决定可以委托的单量
#格式如：price_dict = {25.7:2,25.6:20,25.5:25}
#如果不设置请保留，删除大括号中间的数字即可

price_dict = {25.6:2,25.5:10,25.4:27,0:35}


#控制程序是否运转的开关文本。根据自己的路径保存
#path = 'C:\\Klaus\\System\\08huobi\\demo_python-master\\lowProfit\\control.txt'
path = 'C:\\Users\\moonq\\OneDrive\\python\\06huobi\\demo_python-master\\lowProfit\\control.txt'
#
#超过不再买入的金额限制.
over_high_price = 27
over_low_price = 25

#同一价格的购买次数
buyCount = 1

#交易量限制
limit_total = 35000000

testmoney_path = r'C:\Users\moonq\OneDrive\python\06huobi\demo_python-master\lowProfit\test_money.txt'
coefficient = 0.985

append_path = r'C:\Users\moonq\OneDrive\python\06huobi\demo_python-master'