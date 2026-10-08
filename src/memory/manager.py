from .storage import get_memories, clear_db, insert_data, get_facts_by_category, get_categories

def save_fact(content, category, importance):
    insert_data(content, category, importance)
    return True

def get_facts():
    return get_memories()

def get_category_fact(category):
    return get_facts_by_category(category)

def categories():
    return get_categories
