import html
import io
import json
import os
import traceback
from datetime import datetime, timezone
from typing import Optional

import magic
from decimer_segmentation import segment_chemical_structures
from fastapi import APIRouter, FastAPI, File, Request, Response, UploadFile
from fastapi.responses import RedirectResponse
from PIL import Image
from starlette.responses import StreamingResponse

from app.minio_manager.manager import MinIoManager

ROOT_PATH = "/seg/api"
DOCS_PATH = "/seg/api/docs"

app = FastAPI(
    title="Honeycomb Segmentation Service",
    docs_url=DOCS_PATH,
    openapi_url=ROOT_PATH + "/openapi.json",
)
router = APIRouter(prefix=ROOT_PATH)


@router.get("/")
async def root():
    return RedirectResponse(url="/about")


@router.get("/ping")
async def ping():
    return {"message": "OK"}


@router.get("/about")
async def about(request: Request):
    return {
        "service": "Honeycomb Segmentation Service",
        "version": "1.0.0",
        "raw_url": str(request.url),
    }


@router.post("/")
async def segmentation(file: UploadFile = File(...)):
    pass


app.include_router(router)
