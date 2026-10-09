
from src.rag.embeddings import embed_texts
from src.rag.vector_store import search_similar
from src.rag.embeddings import embed_texts


def retrieve(query: str, model, top_k: int = 5) -> list[dict]:
    """Find the most relevant chunks for a query."""
    # TODO: Embed the query
    embeddings = embed_texts([query], model)
    # TODO: Search for similar chunks
    similar = search_similar(embeddings, top_k=top_k)
    # TODO: Return the retrieved chunks
    return similar


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks and their sources into context."""
    formatted_chunks = []

    for chunk in chunks:
        source = chunk["source"]
        text = chunk["text"]

        formatted_chunk = f"Source: {source}\n{text}"
        formatted_chunks.append(formatted_chunk)

    return "\n\n".join(formatted_chunks)

def retrieve_context(query: str, model, top_k: int = 5) -> str:
    """Retrieve relevant chunks and return formatted context."""
    return format_context(retrieve(query, model, top_k))
