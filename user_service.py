import pymysql
from pymysql.err import IntegrityError

def register_user(username, password):
    db = pymysql.connect(host="localhost", user="lvjian",
        password="123456", database="lvjian")
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (username, password))
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False
    finally:
        cursor.close()
        db.close()


def login_user(username, password):
    db = pymysql.connect(host="localhost", user="lvjian",
        password="123456", database="lvjian")
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()
        if row is None:
            return {"message": "用户名错误"}
        if row[2] != password:
            return {"message": "密码错误"}
        return {"message": "登录成功"}
    finally:
        cursor.close()
        db.close()
