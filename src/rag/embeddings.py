from sentence_transformers import SentenceTransformer


def load_embedding_model():
    # лоадим модель
    model = SentenceTransformer("BAAI/bge-m3")
    return model

def embed_texts(texts, model):
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings
