from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from ..services.ai_service import ai_service
from .auth import get_current_user_dependency

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user_dependency)
):
    try:
        content = await file.read()
        result = ai_service.add_document_to_knowledge_base(
            file_content=content,
            filename=file.filename,
            metadata={"uploaded_by": current_user.email}
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query")
async def query_ai(
    request: dict,
    current_user = Depends(get_current_user_dependency)
):
    try:
        question = request.get("question")
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        result = ai_service.query_with_context(question)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents(
    current_user = Depends(get_current_user_dependency)
):
    sources = [doc["filename"] for doc in ai_service.documents]
    return JSONResponse(content={
        "total": len(ai_service.documents),
        "sources": sources
    })