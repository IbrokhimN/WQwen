import sqlite3
import os
import time

# for clearer testing
# from pprint import pprint

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

def get_distinct_column(data_type):
    match data_type:
        case "id":
            data = database.execute("SELECT DISTINCT id FROM memory")
            return data.fetchall()

        case "content":
            data = database.execute("SELECT DISTINCT content FROM memory")
            return data.fetchall()

        case "category":
            data = database.execute("SELECT DISTINCT category FROM memory")
            data = data.fetchall()
            # форматируем tupple в list
            category = []
            for i in data:
                category.append(i[0])
            return category

        case "importance":
            data = database.execute("SELECT DISTINCT importance FROM memory")
            return data.fetchall()

        case "created_at":
            data = database.execute("SELECT DISTINCT created_at FROM memory")
            return data.fetchall()

        case _:
            return f"не знаю я никакого {data_type}, бака >-<"

def get_categories():
    return get_distinct_column("category")

def get_facts_by_category(category):
    data = database.execute("SELECT * FROM memory WHERE category = ? ", (category,))
    return data.fetchall()


# insert_data("User is building WQwen, a local AI assistant", "projects", 0.95)
# insert_data("User is building IluminOS, a 64-bit educational Rust OS", "projects", 0.9)
# insert_data("User is working on Volmap, an event-focused map platform", "projects", 0.85)

# insert_data("User enjoys working with Rust", "programming", 0.8)
# insert_data("User is interested in CUDA and GPU optimization", "programming", 0.9)
# insert_data("User is interested in low-level systems and Linux internals", "programming", 0.85)

# insert_data("User uses Linux as their main development environment", "environment", 0.8)
# insert_data("User uses Neovim for development", "environment", 0.75)

# insert_data("User prefers concise and direct explanations", "preferences", 0.9)
# insert_data("User prefers conceptual guidance instead of ready-made code when learning", "preferences", 0.9)

# pprint(get_memories())
# print("####### ПРОЕКТЫ #######")
# pprint(get_facts_by_category("projects"))

# print("####### ПРОГРАММИРОВАНИЕ #######")
# pprint(get_facts_by_category("programming"))

# print("####### ENVIROMENT #######")
# pprint(get_facts_by_category("environment"))

print(get_categories())
