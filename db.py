# !/usr/bin/env python
# -*- coding:utf-8 -*-
# 
import sqlite3
import os
import sys

def intailze(func):
    def init(self,*args,**kw):
        self.cx = sqlite3.connect(r'C:\Klaus\System\08huobi\demo_python-master\lowProfit\LTCLowProfit.db')
        self.cursor = self.cx.cursor()
        return func(self,*args,**kw)
        self.close()
    return init

class db_control():
    def __init__(self):
        pass

    @intailze
    def pragma(self,tableName):
        try:
            sql = 'PRAGMA table_info('+tableName+')'
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            self.cx.commit()
            self.cursor.close()
            self.cx.close()
            return result
        except BaseException as e:
            print u'Error:',e

    @intailze
    def creatTable(self,tableName,*args):
        sql = 'create table '
        sql += tableName
        field = ''
        for value in args:
            if value == args[-1]:
                field += value
            else:
                field += value+','
        field = '(' + field + ')' 
        sql += field
        try:
            self.cursor.execute(sql)
            self.cx.commit()
            print u'new table %s has been build'%tableName
            self.cursor.close()
            self.cx.close()
        except BaseException as e:
            print u'Error:',e

    @intailze
    def insert(self,tableName,*args):
        sql = 'insert into '+tableName+' values('
        field = ''
        for index in range(0,len(args)-1):
            if type(args[index]) != int or type(args[index]) != float :
                field += "'%s'"%args[index]+',' 
            else:
                field += '%s'%args[index]+','
        field += "'%s'"%args[len(args)-1]
        field = field + ')' 
        sql += field
        try:
            self.cursor.execute(sql)
            self.cx.commit()
            print u'new data %s has been insert'%args
            self.cursor.close()
            self.cx.close()
        except BaseException as e:
            print u'Error:',e

    @intailze
    def select(self,tableName,*args,**kw):
        sql = 'select '
        if args:
            for value in args:
                sql += value if value == args[-1] else value+','
            sql += 'from '+ tableName
        else:
            sql += '* from '+tableName
        if kw:
            for key in kw:
                sql += ' where %s'%key + '=' + '"%s"'%kw[key]
        result = self.cursor.execute(sql)
        rowlist = []
        for row in result:
            if len(row) == 0:
                return []
            rowlist.append(list(row))
        return rowlist
        
    @intailze
    def delete(self,tableName,**kw):
        sql = "DELETE from "+tableName +' where '
        if kw:
            print len(kw)
            if len(kw) == 1:
                for key in kw:
                    sql += key + '=' + ('%s' if type(kw[key]) == int else '"%s"')%kw[key] 
            else:
                for key in kw:
                    sql += key + '=' + ('%s' if type(kw[key]) == int else '"%s"')%kw[key] + ' and '
                sql = sql[:-4]
            try:   
                self.cursor.execute(sql)
                self.cx.commit()
                print u'delete success'
                self.cursor.close()
                self.cx.close()
            except:
                print u'delete fail'
        else:
            sql = 'drop table '+tableName
            try: 
                self.cursor.execute(sql)
                self.cx.commit()
                self.cursor.close()
                self.cx.close()
                print u'delete %s success'%tableName
            except:
                print u'delete %s fail'%tableName

    @intailze
    def update(self,tableName,updateRow,selectRow):
        sql = 'update '+tableName+' set '
        for key in updateRow:
            sql += key + '=' + ('%s' if type(updateRow[key]) == int else '"%s"')%updateRow[key] + ','
        sql = sql[:-1]
        sql += ' where '
        for key in selectRow:
            sql += key + '=' + ('%s' if type(selectRow[key]) == int else '"%s"')%selectRow[key] + ' and '
        sql = sql[:-4]
        print sql
        try:   
            self.cursor.execute(sql)
            self.cx.commit()
            print u'update success'
            return {'msg':'success'}
            self.cursor.close()
            self.cx.close()
        except BaseException as e:
            print u'update fail',e
            return {'msg':['fail',e]}

    @intailze
    def alert(self,tableName,updateRow):
        sql = 'ALTER TABLE '+tableName+' ADD COLUMN '
        for key in updateRow:
            sql = sql + key + ' '+ updateRow[key]
        print sql
        try:   
            self.cursor.execute(sql)
            self.cx.commit()
            print u'update success'
            return {'msg':'success'}
            self.cursor.close()
            self.cx.close()
        except BaseException as e:
            print u'update fail',e
            return {'msg':['fail',e]}

    def close(self):
        try:
            self.cursor.close()
            self.cx.close()
        except:
            print u'close Error'


if __name__ == '__main__':
    db = db_control()
    db.creatTable('BUYORDER','Time BLOB','Oid integer','OrderPrice BLOB','OrderMount BLOB','Status BLOB')  
    db.creatTable('SELLORDER','Time BLOB','Oid integer','OrderPrice BLOB','OrderMount BLOB','Status BLOB')  
    #db.insert('AllStrategy',0,'false','false')
    #db.delete('profitData',Profit=u'1150.87')
    # updateRow = {'PriceDict':'BLOB'}
    # d = db.alert('SETTING', updateRow)
    # print d
    #sqlRun = 'PRAGMA table_info([SETTING])'
    # d = db.pragma('SETTING')
    # print d
    # print db.select('SETTING',uid=0)
    #db.insert('user',0,0,'Moon','qiu','7ffd4f94-63d605e6-d5f400fb-a6ba0','d5d52f33-dcbd2167-5c6b7b0f-f5676')
