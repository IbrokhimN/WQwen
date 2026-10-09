from transformers import AutoTokenizer


# Размер чанка и перекрытие измеряются в токенах
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50

# Путь к локально скачанному токенизатору Qwen
TOKENIZER_NAME = "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4"

tokenizer = None

def load_tokenizer():
    """
    Загружает токенизатор Qwen из локальной директории.
    Нужен для преобразования текста в token IDs и обратно.
    """
    global tokenizer
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)
    return tokenizer


def tokenize_text(text, tokenizer):
    """
    Преобразует текст в последовательность token IDs.
    Эти ID используются для разбиения текста по размеру в токенах.
    """
    return tokenizer(text)["input_ids"]


def decode_tokens(token_ids, tokenizer):
    """
    Преобразует последовательность token IDs обратно в текст.
    Используется для получения текстового содержимого каждого чанка.
    """
    decodet_text = tokenizer.decode(token_ids, skip_special_tokens = True)
    return decodet_text

def split_text(text, tokenizer, chunk_size=CHUNK_SIZE,
               overlap=CHUNK_OVERLAP):
    """
    Делит текст на чанки заданного размера с перекрытием.

    Каждый чанк должен содержать не более chunk_size токенов.
    overlap токенов повторяется между соседними чанками,
    чтобы уменьшить потерю контекста на границах.

    Возвращает список текстовых чанков.
    """
    token_ids = tokenize_text(text, tokenizer)
    chunks = []
    pointer = 0
    length = len(token_ids)
    if length == 0:
        return chunks
    while pointer < length:
        chunks.append(decode_tokens(token_ids[pointer:pointer+chunk_size], tokenizer))
        pointer += chunk_size - overlap

    return chunks

def create_chunks(document, tokenizer):
    """
    Принимает документ из ingestion pipeline и разбивает его на чанки.

    Возвращает список словарей с чанками и метаданными.
    """
    text = document["text"]
    document_id = document["id"]
    source = document["source"]

    text_chunks = split_text(text, tokenizer)
    chunks = []

    for index, chunk_text in enumerate(text_chunks):
        chunks.append({
            "id": f"{document_id}_chunk{index}",
            "document_id": document_id,
            "source": str(source),
            "chunk_index": index,
            "text": chunk_text
        })

    return chunks
