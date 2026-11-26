
from app.retrieval.vector_store import search_chunks
from app.retrieval.bm25_search import search_bm25


def hybrid_search(query: str, k: int = 5, filename: str = None):
    """
    Combine Dense Search and BM25 Search using RRF.
    Search only within the selected document when filename is provided.
    """

    dense_results = search_chunks(query, k=k, filename=filename)
    bm25_results = search_bm25(query, k=k, filename=filename)

    combined = {}

    # Add Dense Search results
    for rank, result in enumerate(dense_results, start=1):
        key = (result.get("source"), result.get("chunk_index"))

        if key not in combined:
            combined[key] = {**result, "rrf_score": 0.0}

        combined[key]["rrf_score"] += 1 / (60 + rank)

    # Add BM25 Search results
    for rank, result in enumerate(bm25_results, start=1):
        key = (result.get("source"), result.get("chunk_index"))

        if key not in combined:
            combined[key] = {**result, "rrf_score": 0.0}

        combined[key]["rrf_score"] += 1 / (60 + rank)

    results = sorted(
        combined.values(),
        key=lambda item: item["rrf_score"],
        reverse=True
    )

    return results[:k]
