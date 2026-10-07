messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    }
]

# Функции напрямую связанные с messages
def memorize( who, data ):
    global messages
    if len(messages) > 10:
        del messages[1]
        del messages[1]

    if who == "user":
        messages.append({ "role": "user", "content": data })

    elif who == "model":
        messages.append({ "role": "assistant", "content": data })

    else:
        print(f"я не знаю никакого {who}, бака >-<")


def clear_mem():
    global messages
    messages = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    }
]



