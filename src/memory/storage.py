import sqlite3
import os
import time

dir_path = os.path.join(os.path.dirname(__file__), "data")
database_path = dir_path + "/memory.db"

try:
    os.mkdir(dir_path)
except FileExistsError:
    # ничего не делаем
    pass

database = sqlite3.connect(database_path)
database.execute("CREATE TABLE IF NOT EXISTS memory(id INTEGER PRIMARY KEY AUTOINCREMENT, content, category, importance, created_at)")

def insert_data(content, category, importance):
    data = [ content, category, importance, time.time() ]
    database.execute("INSERT INTO memory (content, category, importance, created_at) VALUES(?, ?, ?, ?)", data)
    database.commit()


def get_memories():
    try:
        data = database.execute("SELECT * FROM memory")
        print(type(data))
        return data.fetchall()
    except sqlite3.OperationalError:
        return "Возникла ошибка ня! Нету такой таблицы, бака >-< "

    else:
        return "Я не знаю в чем проблема ня! Разбирайся сам бака! >-<"

def clear_db():
    database.execute("DROP TABLE IF EXISTS memory")
    database.commit()

# def get_categories():
#    data = database.execute("SELECT DISTINCT category FROM memory")


# insert_data("User loves Rust language", "programming", 0.8)
# print(get_memories())
# clear_db()
# print(get_memories())
