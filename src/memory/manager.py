from .storage import get_memories, clear_db, insert_data

def save_fact(content, category, importance):
    insert_data(content, category, importance)
    return True

def get_facts():
    return get_memories()
