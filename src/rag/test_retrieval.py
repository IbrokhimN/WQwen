from src.rag.vector_store import load_vector_store, close_vector_store
from src.rag.embeddings import load_embedding_model
from src.rag.retriever import retrieve

def main():
    index, connection = load_vector_store()
    model = load_embedding_model()

    try:
        query = "How does IluminOS handle network packets using smoltcp?"
        results = retrieve(query, model, top_k=5)

        for i, result in enumerate(results, start=1):
            print(f"\n--- Result {i} ---")
            print(f"Score: {result['score']:.4f}")
            print(f"Source: {result['source']}")
            print(result["text"])

    finally:
        close_vector_store()

if __name__ == "__main__":
    main()
