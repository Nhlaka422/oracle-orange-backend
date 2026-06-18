from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..services.nlp_service import NL2SQLService

router = APIRouter()
nl2sql = NL2SQLService()

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    success: bool
    sql: str = None
    data: list = None
    columns: list = None
    row_count: int = None
    insight: str = None
    error: str = None

@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Convert natural language question to SQL and return results"""
    
    # Step 1: Generate SQL
    sql_result = nl2sql.generate_sql(request.question)
    
    if not sql_result["success"]:
        return QueryResponse(
            success=False,
            error=sql_result["error"]
        )
    
    sql_query = sql_result["sql"]
    
    # Step 2: Execute SQL
    exec_result = nl2sql.execute_sql(sql_query)
    
    if not exec_result["success"]:
        return QueryResponse(
            success=False,
            error=exec_result["error"],
            sql=sql_query
        )
    
    # Step 3: Generate insight
    insight = nl2sql.generate_insight(
        request.question, 
        sql_query, 
        exec_result["data"]
    )
    
    return QueryResponse(
        success=True,
        sql=sql_query,
        data=exec_result["data"],
        columns=exec_result["columns"],
        row_count=exec_result["row_count"],
        insight=insight
    )

@router.get("/sample-queries")
async def get_sample_queries():
    """Return sample questions users can ask"""
    return {
        "queries": [
            "Show me total revenue by month for 2024",
            "What are our top 5 selling products?",
            "Which customers are our biggest spenders?",
            "Show me sales by region and customer segment",
            "What's the average order value by month?",
            "Which employees have the highest performance scores?",
            "What's the profit margin by product category?",
            "Show me revenue trends for the last 6 months",
            "Which products have the highest profit margins?",
            "What's the customer acquisition trend by month?"
        ]
    }