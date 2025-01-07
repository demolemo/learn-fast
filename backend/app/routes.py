from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from .services.summary_service import process_media_file

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save the file temporarily and process it
        summary = await process_media_file(file)
        return JSONResponse(content={"summary": summary})
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        ) 