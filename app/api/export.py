from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..core.database import get_db
from ..services.export_service import ExportService
from .auth import get_current_user_dependency

router = APIRouter(prefix="/export", tags=["export"])

class ExportRequest(BaseModel):
    data: list
    columns: list
    title: str = "Report"

@router.post("/excel")
def export_excel(
    request: ExportRequest,
    current_user = Depends(get_current_user_dependency)
):
    """Export data to Excel"""
    excel_file = ExportService.export_to_excel(
        data=request.data,
        columns=request.columns,
        filename=f"{request.title}.xlsx"
    )
    
    if not excel_file:
        raise HTTPException(status_code=400, detail="No data to export")
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={request.title}.xlsx"}
    )

@router.post("/pdf")
def export_pdf(
    request: ExportRequest,
    current_user = Depends(get_current_user_dependency)
):
    """Export data to PDF"""
    pdf_file = ExportService.export_to_pdf(
        data=request.data,
        columns=request.columns,
        title=request.title
    )
    
    if not pdf_file:
        raise HTTPException(status_code=400, detail="No data to export")
    
    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={request.title}.pdf"}
    )