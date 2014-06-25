#!/usr/bin/python
#coding=utf-8
'''
Created on 2014/6/24

@author: hongxiaolong

xiaofanzhuo imported from tornado/torndb module in Python 2.7.3.

Copyright (c) 2001-2014 Python Software Foundation; All Rights Reserved.

'''

import time
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import torndb
import tornado.escape
from tornado.options import define, options

define("port", default=15000, help="run on the given port", type=int)

#Android版本号
version_code_user = "1"
version_code_business = "1"

#Android升级信息
update_message = "小饭桌: 升级程序库，修复某些BUG!!"

database_name = "xiaofanzhuo"
table_customerlist="customerinfos"
table_businesslist = "businesslistings"
table_menulist = "menulistings"

column_id = "_id"
column_shop_id = "ShopID"

customerlist_colunm = {"ShopID":"char(11)  CHARACTER SET utf8 COLLATE utf8_general_ci",
                       "user_name":"varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci not null",
                       "password":"varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci not null",
                       "reg_phone":"char(11)  CHARACTER SET utf8 COLLATE utf8_general_ci not null",
                       "reg_time":"varchar(40) not null",
                       "last_login_time":"varchar(40)",
                       "business_name":"varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci",
                       "business_add":"varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci",
                       "business_phone":"char(11) CHARACTER SET utf8 COLLATE utf8_general_ci",
                       "inviter":"varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci",
                       "invited":"int default 0"}

menulist_column = {"ShopID":"char(11)  CHARACTER SET utf8 COLLATE utf8_general_ci not null",
            "Food":"varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci not null", 
            "FoodPrice":"float default 0", 
            "Category":"varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci not null",
            "IsRecommend":"int default 0", 
            "IsSpec":"int default 0", 
            "FoodImgUrl":"varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci not null",
            "Width":"int default 0", 
            "Height":"int default 0", 
            "ThumbUrl":"varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci", 
            "img_thumb_width":"int default 0", 
            "img_thumb_higth":"int default 0"}

businesslist_column = {"ShopID":"char(11)  CHARACTER SET utf8 COLLATE utf8_general_ci not null",
            "ShopName":"varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci not null", 
            "BusyState":"int default 0", 
            "ShopImgUrl":"varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci not null", 
            "ShopInfo":"varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci not null", 
            "ShopSite":"varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci not null",
            "ShopLocation":"varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci not null",
            "PhoneNum":"char(11)  CHARACTER SET utf8 COLLATE utf8_general_ci not null", 
            "SendFoodOut":"int default 0", 
            "NumofPeopleWant2Eat":"int default 0", 
            "PraiseNum":"int default 0",
            "ShopAverPrice":"float default 0", 
            "TasteScore":"float default 0", 
            "ServiceScore":"float default 0", 
            "EnvScore":"float default 0",
            "ShopTag":"varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci not null", 
            "Other1":"text", 
            "Other2":"text", 
            "Other3":"text", 
            "ShopMenu":"text",
            "ShopMap":"varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci"}

customerlist_create = "create table if not exists " + table_customerlist + " ("+ column_id + " integer primary key NOT NULL auto_increment"
businesslist_create = "create table if not exists " + table_businesslist + " ("+ column_id + " integer primary key NOT NULL auto_increment"
menulist_create = "create table if not exists " + table_menulist + " ("+ column_id + " integer primary key NOT NULL auto_increment"

#{"url":"http://192.168.1.115:8080/xxx.apk","versionCode":2,"updateMessage":"版本更新信息"}
def update_version():
    dic = {}
    dic["url"] = "http://182.92.155.100/download/xiaofanzhuo.apk"
    dic["versionCode"] = version_code_user
    dic["updateMessage"] = update_message
    dic_json = tornado.escape.json.dumps(dic, encoding="UTF-8", ensure_ascii=False) 
    return dic_json

def sql_create(cre, dict):
    '''
    for mySQL, sql: create tables
    '''
    sql = cre
    for (k,v) in  dict.items():
        sql = sql +", " + k + " " + v
    sql = sql + ");"
    return sql

#MySQL 用户表、商家表
def torndb_create():
    customer_create=sql_create(customerlist_create, customerlist_colunm)
    business_create=sql_create(businesslist_create, businesslist_column)
    
    conn = torndb.Connection('localhost', database_name, user='admin', password='byadmin', charset='utf8')
    conn.execute(customer_create) 
    conn.execute(business_create) 
    conn.close()

#登录
def torndb_login(user_name, password):
    
    login_select = 'SELECT * FROM '+ table_customerlist +' WHERE user_name = %s'
    login_update= 'update ' + table_customerlist + ' set last_login_time=%s where user_name=%s'
    
    conn = torndb.Connection('localhost', database_name, user='admin', password='byadmin', charset='utf8')
    dic = conn.get(login_select, user_name)

    if dic:
        #登录校验
        if dic["user_name"] == user_name:
            if dic["password"] == password:
                current_time_str = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                conn.execute(login_update, current_time_str, user_name) 
                
                dic["last_login_time"] = current_time_str   #登录成功
                dic_json = tornado.escape.json.dumps(dic, encoding="UTF-8", ensure_ascii=False) 
                conn.close()
                return dic_json 
            else:
                dic = {}
                dic["user_name"] = user_name
                dic["password"] = None #密码错误
                dic_json = tornado.escape.json.dumps(dic, encoding="UTF-8", ensure_ascii=False) 
                conn.close()
                return dic_json 
    
    dic = {}
    dic["user_name"] = None #账号不存在
    dic["password"] = None            
    dic_json = tornado.escape.json.dumps(dic, encoding="UTF-8", ensure_ascii=False) 
    
    conn.close()
    return dic_json 

#用户注册
def torndb_register(user_name, password, inviter):
    
    keys = [key for key, value in customerlist_colunm.items()]
    columns = ',' .join(keys) 
    register_insert ='INSERT INTO ' + table_customerlist+' (' + columns + ') VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    register_select = 'SELECT * FROM ' + table_customerlist +' WHERE user_name = %s'
    register_update= 'update ' + table_customerlist + ' set invited=%s where user_name=%s'

    current_time_str = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    dic = {"ShopID" : None, "user_name" : user_name, "password" : password, "reg_phone" : user_name, "reg_time" : current_time_str,
                "last_login_time" : current_time_str, "business_name" : None, "business_add" : None, "business_phone" : None,
                "inviter" : inviter, "invited" : "0"}
    values = [[value for key, value in dic.items()]]
    
    conn = torndb.Connection('localhost', database_name, user='admin', password='byadmin', charset='utf8')
    
    #账户已存在
    user_row = conn.get(register_select, user_name)
    if user_row:
        conn.close()
        dic["user_name"] = None #账号已存在，即插入不成功
        dic_json = tornado.escape.json.dumps(dic, encoding="UTF-8", ensure_ascii=False) 
        return dic_json
    
    conn.insertmany(register_insert, values)
    if inviter and inviter != "":
        inviter_row = conn.get(register_select, inviter)
        if inviter_row:
            conn.execute(register_update, inviter_row["invited"] + 1, inviter if inviter != ""  else None) 
    conn.close()
    
    dic_json = tornado.escape.json.dumps(dic, encoding="UTF-8", ensure_ascii=False) 
    return dic_json
    
#fields: For App SQLite;
#location: MySQL WHERE KEY
def torndb_query_businesslistings(fields, location):
    
    business_select = 'SELECT * FROM ' + table_businesslist + ' WHERE ShopLocation = %s'
    
    dic_json = {}
    conn = torndb.Connection('localhost', database_name, user='admin', password='byadmin', charset='utf8')
    dic_json["businesslistings" + fields] = conn.query(business_select, location)     
    conn.close();
    
    if not dic_json["businesslistings" + fields]: 
        return None
    
    json_obj = tornado.escape.json.dumps(dic_json, encoding="UTF-8", ensure_ascii=False) 
    return json_obj

#商家菜单表查询
def torndb_query_menulistings(shop_id):
    
    menu_select = 'SELECT * FROM ' + table_menulist + shop_id
    
    dic_json = {}
    conn = torndb.Connection('localhost', database_name, user='admin', password='byadmin', charset='utf8')
    datas = conn.query(menu_select)
    dic_json["menulistings" + shop_id] = datas if datas else None
    conn.close();
    
    if not dic_json["menulistings" + shop_id]: 
        return None
    
    json_obj = tornado.escape.json.dumps(dic_json, encoding="UTF-8", ensure_ascii=False) 
    return json_obj

#点赞
def update_praise(uid, is_true):
    business_select = 'SELECT * FROM ' + table_businesslist + ' WHERE ShopID = %s'
    business_update= 'update ' + table_businesslist + ' set PraiseNum=%s where ShopID=%s'
    conn = torndb.Connection('localhost', database_name, user='admin', password='byadmin', charset='utf8')
    dic = conn.get(business_select, uid)
    conn.execute(business_update, dic["PraiseNum"] + 1 if is_true else dic["PraiseNum"] - 1, uid) 
    conn.close();
    
        
class UserHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, input):      
        #根据区域筛选，返回该区域所有饭店信息
        #GetShopListByLocation____DASHANZI
        if input.split("____")[0] == "GetShopListByLocation":
            fields = input.split("____")[1]
            location = None
            if fields ==   "DASHANZI" :
                location = "大山子"
            elif fields ==   "WANGJING":
                location = "望京"
            elif fields ==   "798":
                location = "798"
            else:
                raise tornado.web.HTTPError(403)
            json_obj = torndb_query_businesslistings(fields, location)
            self.write(json_obj if json_obj else "")
            self.finish()
            
        #GetMenuListByID____shop_id
        if input.split("____")[0] == "GetMenuListByID":
            shop_id = input.split("____")[1]
            json_obj = torndb_query_menulistings(shop_id)
            self.write(json_obj if json_obj else "")
            self.finish()
            
        #点赞、取消赞
        #GetShopByID____id____PRAISE、GetShopByID____id____UNPRAISE
        if input.split("____")[0] == "GetShopByID":
            status = input.split("____")[2]
            if status == "PRAISE":
                update_praise(input.split("____")[1], True)
                self.finish()
            elif status == "UNPRAISE":
                update_praise(input.split("____")[1], False)
                self.finish()
        
        #有效订单
        #GetOrderFromUser____user____ShopID____totalPrice____orderTime
        if input.split("____")[0] == "GetOrderFromUser":
            user_name = input.split("____")[1]
            shop_id = input.split("____")[2]
            total_price = input.split("____")[3]
            order_time = input.split("____")[4]
            self.write(input)
            self.finish()
        raise tornado.web.HTTPError(403)
   
class BusinessHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, input):      
        self.write("Data: "  + input)    
        self.finish()    
        
class UpdateHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self, input):      
        if input == "userapk":
            json_update = update_version()
            self.write(json_update if json_update else "")
            self.finish()
        raise tornado.web.HTTPError(403)
    
    
class LoginHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, input): 
        #Login____user_name____password
        if input.split("____")[0] == "Login":
            user_name = input.split("____")[1]
            password = input.split("____")[2]
            json_obj = torndb_login(user_name, password)
            self.write(json_obj if json_obj else "")
            self.finish()
        #Register____user_name____password____inviter
        elif input.split("____")[0] == "Register":
            user_name = input.split("____")[1]
            password = input.split("____")[2]
            inviter = input.split("____")[3]
            json_obj = torndb_register(user_name, password, inviter)
            self.write(json_obj if json_obj else "")
            self.finish()
        raise tornado.web.HTTPError(403)

if __name__ == "__main__":
    #for PyMySQL
    torndb_create()
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/xiaofanzhuo/login/(\w+)", LoginHandler),
            (r"/xiaofanzhuo/user/(\w+)", UserHandler),
            (r"/xiaofanzhuo/business/(\w+)", BusinessHandler),
            (r"/xiaofanzhuo/update/android/(\w+)", UpdateHandler),
        ]
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
