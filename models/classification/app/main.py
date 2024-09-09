import io
import os
import traceback
from datetime import datetime, timezone

import magic
from decimer_image_classifier.decimer_image_classifier import DecimerImageClassifier
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import RedirectResponse
from PIL import Image

from app.minio_manager.manager import MinIoManager

ROOT_PATH = "/cls/api"
DOCS_PATH = "/docs"

app = FastAPI(
    title="Honeycomb Classification Service", root_path=ROOT_PATH, docs_url=DOCS_PATH
)


@app.get("/")
async def root():
    return RedirectResponse(url="/about")


@app.get("/ping")
async def ping():
    return {"message": "OK"}


@app.get("/about")
async def about(request: Request):
    return {
        "service": "Honeycomb Classification Service",
        "version": "1.0.0",
        "raw_url": str(request.url),
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))

        decimer_image_classifier = DecimerImageClassifier()
        score = decimer_image_classifier.get_classifier_score(image)
        is_chem = decimer_image_classifier.is_chemical_structure(image)

        # Save the image to MinIO
        man = MinIoManager()
        mine = magic.Magic(mime=True)
        file.file.seek(0)
        content_type = mine.from_buffer(file.file.read(1024))
        file.file.seek(0)
        tags = {
            "content_type": content_type,
            "upload_time": datetime.now(timezone.utc).isoformat(),
            "is_chem": is_chem,
            "is_chem_score": score,
        }
        file_ext = os.path.splitext(file.filename)[1]
        filename = f"classification/{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}{file_ext}"
        minio_res = man.put_object_stream(filename, file.file, -1, tags)

    except Exception as e:
        traceback.print_exc()
        return {
            "status": "error",
            "info": "Failed to classify the image",
            "detail": str(e),
        }

    return {
        "status": "success",
        "filename": file.filename,
        "score": float(score),
        "is_chem": is_chem,
        "minio_res": minio_res,
    }
