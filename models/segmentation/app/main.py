import io
import os
import tempfile
from datetime import datetime, timezone
from typing import Optional

import magic
from decimer_segmentation import segment_chemical_structures
from fastapi import APIRouter, FastAPI, File, Request, UploadFile, HTTPException
from fastapi.responses import RedirectResponse
from pdf2image import convert_from_path
import numpy as np
from PIL import Image

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
    return RedirectResponse(url=f"{ROOT_PATH}/about")


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


@router.post("/predict")
async def segmentation(file: UploadFile = File(...)):
    
    if file.content_type == 'application/pdf':
        images = convert_from_path(file.file)
        image = images[0]
    elif file.content_type == 'image/png':
        image = Image.open(io.BytesIO(await file.read()))
    else:
        return "Unsupported file type"
    
    try:
        image_array = np.array(image)        
        segments = segment_chemical_structures(
            image_array,
            expand=True,
            visualization=False,
        )
        # collect the original image and the segmented image
        response = {
            "original": None,
            "segments": [],
        }
        man = MinIoManager()
        mine = magic.Magic(mime=True)
        file.file.seek(0)
        content_type = mine.from_buffer(file.file.read(1024))
        file.file.seek(0)  
        tags = {
            "content_type": content_type,
            "created": datetime.now(timezone.utc).isoformat(),
        }
        file_ext = os.path.splitext(file.filename)[1]
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
        filename = f"segmentation/{timestamp}{file_ext}"
        response['original'] = man.put_object_stream(filename, file.file, -1, tags)
        
        for i, segment in enumerate(segments):
            segment_image = Image.fromarray(segment)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                segment_image.save(temp_file, format="PNG")
                temp_file.seek(0)
                tags = {
                    "content_type": 'image/png',
                    "created": datetime.now(timezone.utc).isoformat(),
                }
                filename = f"segmentation/{timestamp}_segment_{i}.png"
                res = man.put_object_stream(filename, temp_file, -1, tags)
                response['segments'].append(res)
                    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing image: {e}",
        )
    
    return response
    


app.include_router(router)
