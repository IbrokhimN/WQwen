
from src.rag.ingestion import parse_knowledge, dictify, is_format_supported
from src.rag.chunking import load_tokenizer, create_chunks
from src.rag.embeddings import load_embedding_model, embed_texts
from src.rag.vector_store import (
    create_vector_store,
    add_chunks,
    close_vector_store,
)


def index_knowledge() -> None:
    file_paths = parse_knowledge()

    documents = []

    for path in file_paths:
        if is_format_supported(str(path)):
            document = dictify(path)

            if document is not None:
                documents.append(document)

    if not documents:
        print("никакой формат не поддерживается ня :3")
        return
    # загружаем все
    tokenizer = load_tokenizer()
    embedding_model = load_embedding_model()
    create_vector_store()

    try:
        all_chunks = []

        for document in documents:
            all_chunks.extend(create_chunks(document, tokenizer))

        if not all_chunks:
            print("чанки создать не получилось ня :3")
            return

        texts = [chunk["text"] for chunk in all_chunks]

        embeddings = embed_texts(texts, embedding_model)

        add_chunks(all_chunks, embeddings)

        print(
                f"индексация завершена ня :3 "
            f"{len(documents)} документов, "
            f"{len(all_chunks)} чанков."
        )

    finally:
        close_vector_store()


if __name__ == "__main__":
    index_knowledge()
