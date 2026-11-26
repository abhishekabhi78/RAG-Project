
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.upload import router as upload_router
from app.api.search import router as search_router
from app.api.hybrid import router as hybrid_router
from app.api.bm25 import router as bm25_router
from app.api.ask import router as ask_router

app = FastAPI(
    title="RAG Project API",
    description="Backend API for our RAG application",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://rag-project-mwldxilji-team-abhishek.vercel.app",
        "https://rag-project-i102pfcgq-team-abhishek.vercel.app",
        "https://rag-project-git-main-team-abhishek.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload API connection
app.include_router(
    upload_router, 
    prefix="/api", 
    tags=["Document Upload"]
)
app.include_router(
    search_router,
    prefix="/api",
    tags=["Document Search"]
)

app.include_router(
    bm25_router,
    prefix="/api",
    tags=["BM25 Search"]
)

app.include_router(
    hybrid_router,
    prefix="/api",
    tags=["Hybrid Search"]
)

app.include_router(
    ask_router,
    prefix="/api",
    tags=["RAG Question Answering"]
)

@app.get("/")
def home():
    return {
        "message": "Welcome to RAG Project Backend!"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.get("/api/message")
def get_message():
    return {
        "message": "Hello from FastAPI Backend!"
    }
