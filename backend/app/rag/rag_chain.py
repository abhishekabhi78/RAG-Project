
from app.retrieval.hybrid_search import hybrid_search
from app.rag.gemini_client import generate_answer


def run_rag(query: str, k: int = 5, filename: str = None):
    """
    Retrieve relevant document chunks and generate
    an answer using Gemini.
    """

    # Step 1: Retrieve relevant chunks
    results = hybrid_search(query, k=k, filename=filename)

    if not results:
        return {
            "query": query,
            "answer": "No relevant information found in uploaded documents.",
            "total_chunks": 0,
            "sources": []
        }

    # Step 2: Prepare context for Gemini
    context_parts = []

    for result in results:
        context_parts.append(
            f"""
            Source: {result.get('source')}
            Chunk: {result.get('chunk_index')}

            Content:
            {result.get('content', '')}
            """
        )

    context = "\n\n".join(context_parts)

    # Step 3: Generate answer using Gemini
    answer = generate_answer(
        question=query,
        context=context
    )

    # Step 4: Prepare source information
    sources = [
        {
            "source": result.get("source"),
            "chunk_index": result.get("chunk_index"),
            "rrf_score": result.get("rrf_score")
        }
        for result in results
    ]

    return {
        "query": query,
        "answer": answer,
        "total_chunks": len(results),
        "sources": sources
    }
