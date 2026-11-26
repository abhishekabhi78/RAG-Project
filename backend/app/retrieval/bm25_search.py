
from rank_bm25 import BM25Okapi

from app.retrieval.vector_store import client, COLLECTION_NAME



def search_bm25(query: str, k: int = 5, filename: str = None):
    """
    Search document chunks using BM25.
    Restrict results to the selected document when filename is provided.
    """

    if not client.collection_exists(COLLECTION_NAME):
        return []

    all_points = []
    offset = None

    while True:
        points, next_offset = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=1000,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )

        all_points.extend(points)

        if next_offset is None:
            break

        offset = next_offset

    documents = []

    for point in all_points:
        payload = point.payload or {}
        content = payload.get("page_content", "")
        metadata = payload.get("metadata", {})

        source = metadata.get("source")

        # Only include the selected PDF
        if filename and source != filename:
            continue

        if content.strip():
            documents.append({
                "content": content,
                "source": source,
                "chunk_index": metadata.get("chunk_index")
            })

    if not documents:
        return []

    tokenized_corpus = [
        doc["content"].lower().split()
        for doc in documents
    ]

    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()

    scores = bm25.get_scores(tokenized_query)

    # Ignore chunks that have no lexical relevance
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

