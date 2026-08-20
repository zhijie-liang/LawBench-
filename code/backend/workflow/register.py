from pymysql.err import IntegrityError

from services.mysql_connect import mysql_connect


def register_user(username: str, password: str):
    """注册接口。

        参数:
            username: 用户名。
            password: 密码。
        """
    db = mysql_connect()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (username, password))
        db.commit()
        return {"username": username, "password": password}
    except IntegrityError:
        db.rollback()
        return "用户名已存在，注册失败！"
    finally:
        cursor.close()
        db.close()