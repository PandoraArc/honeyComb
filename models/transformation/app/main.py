import html
import io
import json
import os
import traceback
import tempfile
from datetime import datetime, timezone
from typing import Optional

import magic
from decimer_transformation import predict_SMILES
from fastapi import APIRouter, FastAPI, File, Request, UploadFile, HTTPException
from fastapi.responses import RedirectResponse
import numpy as np
from PIL import Image
from starlette.responses import StreamingResponse

from app.minio_manager.manager import MinIoManager

ROOT_PATH = "/trans/api"
DOCS_PATH = "/trans/api/docs"

app = FastAPI(
    title="Honeycomb Transformation Service",
    docs_url=DOCS_PATH,
    openapi_url=ROOT_PATH + "/openapi.json",
)
router = APIRouter(prefix=ROOT_PATH)


@router.get("/")
async def root():
    return RedirectResponse(url=f"{ROOT_PATH}/about")


@router.get("/ping")
async def ping():
    return {"message": "OK"}


@router.get("/about")
async def about(request: Request):
    return {
        "service": "Honeycomb Transformation Service",
        "version": "1.0.0",
        "raw_url": str(request.url),
    }
    
@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    
    try:
        image_bytes = await file.read()
        smiles = predict_SMILES(io.BytesIO(image_bytes))
                
        man = MinIoManager()
        mine = magic.Magic(mime=True)
        file.file.seek(0)
        content_type = mine.from_buffer(file.file.read(1024))
        file.file.seek(0)
        tags = {
            "content_type": content_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "SMILES": smiles
        }
        file_ext = os.path.splitext(file.filename)[1]
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
        filename = f"transformation/{timestamp}{file_ext}"
        res = man.put_object_stream(filename, file.file, -1, tags)
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error processing image: {e}")
    
    
    return res


app.include_router(router)