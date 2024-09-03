import html
import io
import json
import os
import sys
import traceback
import tempfile
from datetime import datetime, timezone
from typing import Optional

import magic
from fastapi import APIRouter, FastAPI, File, Request, UploadFile, HTTPException
from fastapi.responses import RedirectResponse
import numpy as np
from PIL import Image


sys.path.append('/home/app/')
from DECIMER import predict_SMILES


ROOT_PATH = "/trans/api"

DOCS_PATH = "/docs"



image_path = "example_data/DECIMER_test_1.png"
SMILES = predict_SMILES(image_path)
print(SMILES)

app = FastAPI(
    title="Honeycomb Transformation Service", root_path=ROOT_PATH, docs_url=DOCS_PATH
)



@app.get("/")
async def root():
    return RedirectResponse(url=f"{ROOT_PATH}/about")


@app.get("/ping")
async def ping():
    return {"message": "OK"}


@app.get("/about")
async def about(request: Request):
    return {
        "service": "Honeycomb Transformation Service",
        "version": "1.0.0",
        "raw_url": str(request.url),
    }
    


