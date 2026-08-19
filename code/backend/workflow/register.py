import pymysql

def register_user(username: str, password: str):
    db = pymysql.connect(
        host="localhost", user="lvjian",
        password="123456", database="lvjian"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users(username,password) VALUES(%s,%s)",
        (username, password))
    db.commit()
    db.close()


def login_user(username: str, password: str):
    db = pymysql.connect(
        host="localhost", user="lvjian",
        password="123456", database="lvjian"
    )
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users(username,password) VALUES(%s,%s)",
        (username, password))
    db.commit()
    db.close()