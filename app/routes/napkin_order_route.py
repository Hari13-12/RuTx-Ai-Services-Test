from fastapi import APIRouter, status, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.services.napkin_order_service import process_invoice
import logging
from typing import Dict, Any
from app.core.deps import get_current_user

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/napkin_order", tags=["Orders"], dependencies=[Depends(get_current_user)])


async def validate_file(file: UploadFile) -> UploadFile:
    """Validate the uploaded file before processing.
    
    Args:
        file: The uploaded file
        
    Returns:
        The validated file
        
    Raises:
        HTTPException: If the file is invalid
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
        
    if not file.filename:
        raise HTTPException(status_code=400, detail="File has no name")
        
    content_type = file.content_type or ""
    if not content_type.startswith("image/") and not content_type == "application/pdf":
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {content_type}. Only images and PDFs are supported."
        )
        
    return file


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def parse_invoice(file: UploadFile = Depends(validate_file)):
    """Process an invoice image and extract structured data.
    
    Args:
        file: The uploaded invoice file
        
    Returns:
        Structured invoice data
    """
    logger.info(f"Received file for processing: {file.filename}")
    
    try:
        result = await process_invoice(file)
        
        if "error" in result:
            logger.error(f"Error processing invoice: {result['error']}")
            raise HTTPException(status_code=422, detail=result["error"])
            
        return {"extracted_data": result}
        
    except Exception as e:
        logger.exception(f"Unexpected error processing invoice: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during invoice processing")