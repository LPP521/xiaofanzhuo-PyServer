#! /usr/bin/
#encoding:utf8
   
"""批量调整照片大小 
"""  
__author__ ='BOBO'  
__email__ = 'tonywang1988'   
VERSION = "Photo Resizer v1.0"  
   
import os  
import sys  
import time  
import glob  
from PIL import Image  

import torndb
import tornado.escape

import json
import urllib
   
database_name = "xiaofanzhuo"
table_menulist_old = "Lmenulistings"
table_menulist = "menulistings"

column_id = "_id"
column_shop_id = "ShopID"   
   
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

menulist_create = "create table if not exists " + table_menulist + " ("+ column_id + " integer primary key NOT NULL auto_increment"   
 
def sql_create(cre, dict):
    '''
    for mySQL, sql: create tables
    '''
    sql = cre
    for (k,v) in  dict.items():
        sql = sql +", " + k + " " + v
    sql = sql + ");"
    return sql

def torndb_create():
    menu_create=sql_create(menulist_create, menulist_column)  
    conn = torndb.Connection('localhost', database_name, user='admin', password='byadmin', charset='utf8')
    conn.execute(menu_create) 
    conn.close()
     
#fields: For App SQLite;
#location: MySQL WHERE KEY
def torndb_repace(_id, shop_id, food, url, w, h):

    #从老数据库读
    menu_select = 'SELECT * FROM ' + table_menulist_old + ' WHERE ShopID = %s AND Food = %s'
    
    #插入新数据库
    keys = [key for key, value in menulist_column.items()]
    columns = ',' .join(keys) 
    menu_insert ='INSERT INTO ' + table_menulist+' (' + columns + ') VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

    conn = torndb.Connection('localhost', database_name, user='admin', password='byadmin', charset='utf8')
    row = conn.get(menu_select, _id, food)   
    conn.close();
    
    if row:
        
        dic = menulist_column
        dic["ShopID"] = shop_id
        dic["Food"] = row["Food"]
        dic["FoodPrice"] = row["FoodPrice"]
        dic["Category"] = row["Category"]
        dic["IsRecommend"] = row["IsRecommend"]
        dic["IsSpec"] = row["IsSpec"]
        dic["FoodImgUrl"] = url
        dic["Width"] = w
        dic["Height"] = h
        dic["ThumbUrl"] = row["ThumbUrl"]
        dic["img_thumb_width"] = row["img_thumb_width"]
        dic["img_thumb_higth"] = row["img_thumb_higth"]
    
        print dic
        
        values = [[value for key, value in dic.items()]]
        conn = torndb.Connection('localhost', database_name, user='admin', password='byadmin', charset='utf8')
        conn.insertmany(menu_insert, values)
        conn.close();
   
class PicResizer:  
    """根据指定的目录，对该目录下的所有照片进行大小调整 
    """  
   
    def __init__(self, picpath, bakpath):  
        '''''初始化参数'''  
        self.picpath = picpath  
        self.bakpath = bakpath  
   
        logfile = bakpath + "/log" + time.strftime("%Y%m%d%H%M") + ".txt"  
        self.log = open(logfile, "a")  
   
    def pic_walker(self, path):  
        '''''获取指定目录下的所有JPG照片，不递归深入查找'''  
        target = []  
        for files in glob.glob(path + "/*.jpg"):  
            filepath,filename = os.path.split(files)  # todo: mark  
            target.append(filename)  
   
        return target  
   
    def check_folder(self, subFolderName):  
        '''''检查目标文件夹是否存在，不存在则创建之'''  
   
        foldername = self.bakpath + '/' + subFolderName  
        print foldername  
   
        if not os.path.isdir(foldername):  
            os.mkdir(foldername)  
   
        #return 0  
        return foldername  
   
    def pic_info(self, img):  
        '''''获取照片的尺寸'''  
        w, h = img.size  
        #print w,h
        return w, h, 0  # 横版照片  
#         if  w>h:  
#             return w, h, 0  # 横版照片  
#         else:  
#             return w, h, 1  # 竖版照片     
   
    def comp_num(self, x, y):  
        '''''比较两个实数 
        如果是用直接比较话会出现经典的整数除得0问题 
        '''  
   
        x = float(x)  
        y = float(y)  
        return float(x/y)  
   
    def pic_resize(self, picname, p_w, p_h):  
        '''''根据设定的尺寸，对指定照片进行像素调整'''  
   
        # 获取指定照片的规格，一般是1024,768  
        img = Image.open(picname)  
        w, h, isVertical = self.pic_info(img)  
        return w,h
   
        # 判断照片横竖，为竖版的话对调w,h  
#         if isVertical:  
#             p_w, p_h = p_h, p_w  
#    
#         # 如果照片调整比例合适，直接输出  
#         if self.comp_num(p_h, p_w) == self.comp_num(h, w):  
#             target = img.resize(  
#                                 (int(p_w), int(p_h)),  
#                                 Image.ANTIALIAS  # hack: 参数呐！高保真必备！  
#                                )  
#             # ANTIALIAS: a high-quality downsampling filter  
#             # BILINEAR: linear interpolation in a 2x2 environment  
#             # BICUBIC: cubic spline interpolation in a 4x4 environment  
#    
#             return target  
   
        # 比例不合适就需要对照片进行计算，保证输出照片的正中位置  
        # 算法灵感来源于ColorStrom  
        if self.comp_num(p_h, p_w) > self.comp_num(h, w):  
            # 240/320 > 360/576 偏高照片的处理  
   
            # 以高为基准先调整照片大小  
            p_w_n = p_h * self.comp_num(w,h)  # 根据新高按比例设置新宽  
            temp_img = img.resize(  
                                  (int(p_w_n), int(p_h)),  
                                  Image.ANTIALIAS  
                                 )  
   
            # 获取中间选定大小区域  
            c = (p_w_n - p_w)/2  # 边条大小  
            box = (c, 0, c+p_w, p_h)  # 选定容器  
            box = tuple(map(int, box))  # 转换成crop需要的int形参数  
            target = temp_img.crop(box)  
   
            return target  
   
        else:  
            # 偏宽的照片  
   
            # 以宽为基准先调整照片大小  
            p_h_n = p_w * self.comp_num(h, w)  # 根据新宽按比例设置新高  
            temp_img = img.resize(  
                                  (int(p_w), int(p_h_n)),  
                                  Image.ANTIALIAS  
                                 )  
   
            # 获取新图像  
            c = (p_h_n - p_h)/2  
            box = (0, c, p_w, c+p_h)  
            box = tuple(map(int, box))  
            target = temp_img.crop(box)  
   
            return target    
   
    def run_auto(self, *args):  
        '''''运行调整照片尺寸进程 
        接纳规格列表，每个规格为一个tuple 
        '''  
   
        #_id = raw_input("type your _id:")
        #shop_id = raw_input("type your shopID:")
        #shop_name = raw_input("type your shopName:")
        _id = "1"
        shop_id = "01064381316"
        shop_name = "大公鸡"
   
        # 获取所有图片列表  
        imglist = self.pic_walker(self.picpath)  
        print imglist
   
        list = []
        
        # 处理照片  
        for img in imglist:  
            imgfile = self.picpath + "/" + img  # 完整照片名称  
            url = "http://182.92.155.100/images/" + urllib.quote(shop_name) +"/" + urllib.quote(img)
            print '"' + url + '"' + ','
#             print url
#             food = img.split('.')[0] #得到菜品名
#             w, h = 0, 0 
#             #得到菜品照片的宽高
#             width,height = self.pic_resize(imgfile, int(w), int(h))  
#             print width,height
#             torndb_repace(_id, shop_id, food, url, width, height)
            
            
            #try:  
                #for std in args:                    
                    # 定义目标文件  
                    #opfile = self.check_folder(str(w)+"x"+str(h)) + "/" + img  
                    #print opfile
                    #tempimg = self.pic_resize(imgfile, int(w), int(h))  
                    #tempimg.save(opfile, 'jpeg')  
    
                #self.log.write(str(img) + "\tOK\n")  
            #except: 
                #self.log.write(str(img) + "\tErr\n")  
   
        print "Done."  
   
   
   
def main():  
    '''''主函数'''  
   
    reload(sys)
    sys.setdefaultencoding('utf-8')
   
    torndb_create()
    picpath = "/var/www/images/大公鸡"
    #picpath = bakpath = raw_input("type your photo's path:")
    # 修改源照片文件夹路径  
    #picpath = "/home/bobo/Pictures"  
    # 修改为你的目标路径  
    bakpath = "/var/www/data"
   
    # 实例一个进程并运行  
    resizer = PicResizer(picpath, bakpath)  
    resizer.run_auto((320, 240),(240,200))  
   
   
if __name__ == "__main__":  
    sys.exit(main())  
