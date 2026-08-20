from services.mysql_connect import mysql_connect


def login_user(username,password):
    """用户登录接口。

        参数:
            username: 用户名。
            password: 密码。
        """
    db = mysql_connect()
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