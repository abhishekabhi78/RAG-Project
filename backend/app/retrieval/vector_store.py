import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue
)

from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from langchain_community.embeddings import FastEmbedEmbeddings
from qdrant_client.http.models import PayloadSchemaType


# Qdrant Cloud / Local database
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if QDRANT_URL and QDRANT_API_KEY:
    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY
    )
else:
    client = QdrantClient(path="./qdrant_db")

# Embedding model
embeddings = FastEmbedEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)

COLLECTION_NAME = "rag_documents"


def store_chunks(chunks: list[str], filename: str):
    """
    Store document chunks in Qdrant vector database.
    """

    documents = [
        Document(
            page_content=chunk,
            metadata={
                "source": filename,
                "chunk_index": index
            }
        )
        for index, chunk in enumerate(chunks)
    ]

    # Create collection if it does not exist
    if not client.collection_exists(COLLECTION_NAME):

        vector_size = len(
            embeddings.embed_query("Test embedding")
        )

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
    
        # Create keyword index for filename filtering
    client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="metadata.source",
        field_schema=PayloadSchemaType.KEYWORD,
        wait=True
    )
    # Connect to Qdrant collection
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )

    # Save document chunks
    vector_store.add_documents(documents)

    return len(documents)



def search_chunks(query: str, k: int = 5, filename: str = None):
    """
    Search relevant chunks in Qdrant.
    Restrict search to the selected document when filename is provided.
    """

    if not client.collection_exists(COLLECTION_NAME):
        return []

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )

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

    results = vector_store.similarity_search_with_score(
        query,
        k=k,
        filter=search_filter
    )

    search_results = []

    for document, score in results:
        search_results.append({
            "content": document.page_content,
            "source": document.metadata.get("source"),
            "chunk_index": document.metadata.get("chunk_index"),
            "score": float(score)
        })

    return search_results


