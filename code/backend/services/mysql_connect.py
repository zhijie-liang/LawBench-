import pymysql

def mysql_connect():
    db = pymysql.connect(host="47.99.120.222", user="lvjian",
                         password="123456", database="lvjian")
    return db