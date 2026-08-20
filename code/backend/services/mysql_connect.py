import pymysql

def mysql_connect():
    db = pymysql.connect(host="localhost", user="lvjian",
                         password="123456", database="lvjian")
    return db