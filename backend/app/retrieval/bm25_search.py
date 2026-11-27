
from rank_bm25 import BM25Okapi

from app.retrieval.vector_store import client, COLLECTION_NAME
from qdrant_client.http.models import Filter, FieldCondition, MatchValue


def search_bm25(query: str, k: int = 5, filename: str = None):
    """
    Search document chunks using BM25.
    Fetch only the selected document when filename is provided.
    """

    if not client.collection_exists(COLLECTION_NAME):
        return []

    documents = []
    offset = None
    batch_size = 100

    search_filter = None

    if filename:
        search_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.source",
                    match=MatchValue(value=filename)
                )
            ]
        )

    # Fetch documents in small batches
    while True:
        points, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=search_filter,
            limit=batch_size,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )

        for point in points:
            payload = point.payload or {}
            content = payload.get("page_content", "")
            metadata = payload.get("metadata", {})

            if content.strip():
                documents.append({
                    "content": content,
                    "source": metadata.get("source"),
                    "chunk_index": metadata.get("chunk_index")
                })

        if next_offset is None:
            break

        offset = next_offset

    if not documents:
        return []

    # Tokenize document chunks
    tokenized_corpus = [
        doc["content"].lower().split()
        for doc in documents
    ]

    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()

    scores = bm25.get_scores(tokenized_query)

    # Get top relevant chunks
    ranked_indices = sorted(
        [
            index for index, score in enumerate(scores)
            if score > 0
        ],
        key=lambda index: scores[index],
        reverse=True
    )[:k]

    results = []

    for index in ranked_indices:
        results.append({
            **documents[index],
            "score": float(scores[index])
        })

    return results
