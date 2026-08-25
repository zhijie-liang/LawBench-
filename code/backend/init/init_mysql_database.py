"""初始化数据库，创建 users 和 documents 表。"""
import pymysql

db = pymysql.connect(
    host="47.99.120.222", user="lvjian",
    password="123456", database="lvjian"
)

print("MySQL连接成功")

cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
 id INT PRIMARY KEY AUTO_INCREMENT,
 username VARCHAR(50) UNIQUE NOT NULL,
 password VARCHAR(100) NOT NULL
);
""")
db.commit()
cursor.close()

cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS documents(
 id INT PRIMARY KEY AUTO_INCREMENT,
 title VARCHAR(200) NOT NULL,
 content TEXT NOT NULL,
 doc_type VARCHAR(50),
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
db.commit()
cursor.close()

print("创建成功")

db.close()