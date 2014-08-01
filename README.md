xiaofanzhuo-PyServer
====================

新版小饭桌服务端 based on Python

1、利用Tornado搭建了HTTP服务端；

2、利用Torndb + MySQL实现了小饭桌数据库；

3、利用Ngnix搭建了图片和下载服务器；

4、且利用Ngnix的反向代理规避了Lobby AP对非80端口HTTP包的封堵；

5、单核512M内存ab压测性能为并发300-500；

6、Ngnix-file-torndb.py为批量处理菜品图品信息，包含图片宽高、批量命名、批量数据库更新；
