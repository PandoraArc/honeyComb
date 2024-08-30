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
    
    image_bytes = await file.read()
    smile = predict_SMILES(io.BytesIO(image_bytes))
    
    
    return {"smile": smile}


app.include_router(router)