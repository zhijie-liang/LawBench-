import pymysql
from pymysql.err import IntegrityError

def extract_text(file_bytes, content_type):
    if content_type != "text/plain":
        return "暂只支持TXT文件"
    return file_bytes.decode("utf-8")

def document_save(title, content, doc_type):
    db = pymysql.connect(host="localhost", user="lvjian",
                         password="123456", database="lvjian")
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO documents(title, content, doc_type) VALUES(%s,%s,%s)",
        (title, content, doc_type))
    db.commit()
    cursor.close()
    db.close()

def upload_documents(file_name, content, file_type):
    db = pymysql.connect(host="localhost", user="lvjian",
                         password="123456", database="lvjian")
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO documents(title, file_name, content, file_type) VALUES(%s,%s,%s,%s)",
        (file_name, file_name, content, file_type))
    db.commit()
    cursor.close()
    db.close()

def search_documents(keyword):
    db = pymysql.connect(host="localhost", user="lvjian",
                         password="123456", database="lvjian")
    cursor = db.cursor()
    try:
        pattern = f"%{keyword}%"
        cursor.execute("""
        SELECT title,content,doc_type
        FROM documents
        WHERE title LIKE %s
           OR content LIKE %s
           OR doc_type LIKE %s
        LIMIT 3
        """, (pattern,pattern,pattern))
        rows = cursor.fetchall()
        if rows:
            return rows
        else:
            return "没有检索到"
    finally:
        cursor.close()
        db.close()


def load_documents():
    db = pymysql.connect(host="localhost", user="lvjian",
                         password="123456", database="lvjian")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM documents")
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return rows


def clear_documents():
    db = pymysql.connect(host="localhost", user="lvjian",
                         password="123456", database="lvjian")