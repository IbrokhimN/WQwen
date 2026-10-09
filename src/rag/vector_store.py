
import sqlite3
from pathlib import Path

import faiss
import numpy as np


# BGE-M3 produces 1024-dimensional dense embeddings.
VECTOR_DIM = 1024

STORE_DIR = Path("data/vector_store")
INDEX_PATH = STORE_DIR / "index.faiss"
DB_PATH = STORE_DIR / "metadata.db"

index = None
connection = None


def _create_metadata_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            vector_id INTEGER PRIMARY KEY,
            chunk_id TEXT UNIQUE NOT NULL,
            document_id TEXT NOT NULL,
            source TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            text TEXT NOT NULL
        )
    """)
    conn.commit()


def create_vector_store():
    global index, connection

    STORE_DIR.mkdir(parents=True, exist_ok=True)

    if connection is not None:
        connection.close()

    connection = sqlite3.connect(DB_PATH)
    _create_metadata_table(connection)

    if INDEX_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
    else:
        index = faiss.IndexIDMap2(
            faiss.IndexFlatIP(VECTOR_DIM)
        )

    return index, connection


def load_vector_store():
    global index, connection

    STORE_DIR.mkdir(parents=True, exist_ok=True)

    if connection is not None:
        connection.close()

    connection = sqlite3.connect(DB_PATH)
    _create_metadata_table(connection)

    if INDEX_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
    else:
        index = faiss.IndexIDMap2(
            faiss.IndexFlatIP(VECTOR_DIM)
        )

    return index, connection


def add_chunks(chunks, embeddings):
    global index, connection

    if index is None or connection is None:
        raise RuntimeError(
            "Vector store is not initialized. "
            "Call create_vector_store() or load_vector_store() first."
        )

    if len(chunks) == 0:
        return []

    vectors = np.asarray(embeddings, dtype=np.float32)

    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)

    if vectors.shape != (len(chunks), VECTOR_DIM):
        raise ValueError(
            f"Expected embeddings shape ({len(chunks)}, {VECTOR_DIM}), "
            f"got {vectors.shape}."
        )

    vectors = np.ascontiguousarray(vectors)

    # Allocate unique integer IDs using the existing SQLite records.
    row = connection.execute(
        "SELECT COALESCE(MAX(vector_id), -1) + 1 FROM chunks"
    ).fetchone()

    start_id = row[0]
    vector_ids = np.arange(
        start_id,
        start_id + len(chunks),
        dtype=np.int64
    )

    metadata = []

    for vector_id, chunk in zip(vector_ids, chunks):
        metadata.append((
            int(vector_id),
            chunk["id"],
            chunk["document_id"],
            str(chunk["source"]),
            int(chunk["chunk_index"]),
            chunk["text"]
        ))

    # Insert metadata first. If this fails, FAISS remains unchanged.
    connection.executemany(
        """
        INSERT INTO chunks (
            vector_id,
            chunk_id,
            document_id,
            source,
            chunk_index,
            text
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        metadata
    )
    connection.commit()

    try:
        # Add vectors and their corresponding IDs to FAISS.
        index.add_with_ids(vectors, vector_ids)

        # Persist the updated index.
        save_vector_store()

    except Exception:
        # Roll back the in-memory index and metadata if adding or saving fails.
        index.remove_ids(vector_ids)

        connection.executemany(
            "DELETE FROM chunks WHERE vector_id = ?",
            [(int(vector_id),) for vector_id in vector_ids]
        )
        connection.commit()
        raise

    return vector_ids.tolist()


def search_similar(query_embedding, top_k=5):
    global index, connection

    if index is None or connection is None:
        raise RuntimeError(
            "Vector store is not initialized. "
            "Call create_vector_store() or load_vector_store() first."
        )

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    if index.ntotal == 0:
        return []

    query = np.asarray(query_embedding, dtype=np.float32)

    if query.ndim == 1:
        query = query.reshape(1, -1)

    if query.shape != (1, VECTOR_DIM):
        raise ValueError(
            f"Expected query shape (1, {VECTOR_DIM}), got {query.shape}."
        )

    query = np.ascontiguousarray(query)

    # Inner product gives cosine similarity when vectors are normalized.
    scores, vector_ids = index.search(
        query,
        min(top_k, index.ntotal)
    )

    results = []

    for score, vector_id in zip(scores[0], vector_ids[0]):
        # FAISS uses -1 when no matching vector exists.
        if vector_id == -1:
            continue

        row = connection.execute(
            """
            SELECT chunk_id, document_id, source, chunk_index, text
            FROM chunks
            WHERE vector_id = ?
            """,
            (int(vector_id),)
        ).fetchone()

        if row is None:
            continue

        results.append({
            "vector_id": int(vector_id),
            "chunk_id": row[0],
            "document_id": row[1],
            "source": row[2],
            "chunk_index": row[3],
            "text": row[4],
            "score": float(score)
        })

    return results


def save_vector_store():
    if index is None:
        raise RuntimeError(
            "Vector store is not initialized."
        )

    STORE_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))


def close_vector_store():
    global connection

    if connection is not None:
        connection.close()
        connection = None
