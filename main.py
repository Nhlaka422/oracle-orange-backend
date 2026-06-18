from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import queries, dashboard, auth, export, documents

app = FastAPI(
    title="Oracle Orange - AI Business Analyst",
    description="Natural Language to SQL with AI-powered insights",
    version="1.0.0"
)

# CORS middleware - FIXED
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["authentication"])
app.include_router(queries.router, prefix="/api", tags=["queries"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(export.router, prefix="/api", tags=["export"])
app.include_router(documents.router, prefix="/api", tags=["documents"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Oracle Orange - AI Business Analyst",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "Backend is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)