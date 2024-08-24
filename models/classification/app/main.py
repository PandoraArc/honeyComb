import html
import io
import json
import os
import traceback
from datetime import datetime, timezone
from typing import Optional

import magic
from decimer_image_classifier.decimer_image_classifier import DecimerImageClassifier
from fastapi import FastAPI, File, Request, Response, UploadFile
from fastapi.responses import RedirectResponse
from PIL import Image
from starlette.responses import StreamingResponse

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


@app.get("/minio/{path_name:path}")
async def object_list(
    path_name: str, response: Response, resp_type: Optional[str] = "list"
):
    print("object_list")
    minio_man = MinIoManager()
    if resp_type == "list":
        res = minio_man.list_objects(path_name)
        arr = []
        for item_obj, tags in res:
            if tags is None:
                continue
            tags.pop("delete_key", None)
            tags.pop("view_key", None)
            tags.pop("update_key", None)
            arr.append({"object": item_obj, "tags": tags})
        return arr

    (temp_file, obj, tags) = minio_man.get_file_object(path_name)
    response = None
    if obj is not None:
        print("filename:", obj.object_name)
        print("content_type:", obj.content_type)
        fp = open(temp_file, mode="rb")
        mime = magic.Magic(mime=True)
        response = StreamingResponse(fp, media_type=mime.from_file(temp_file))
        filename_encoded = obj.object_name.encode("utf-8")
        escaped_filename = html.escape(
            os.path.basename(filename_encoded.decode("unicode-escape"))
        )
        response.headers["Content-Disposition"] = f"filename*=UTF-8''{escaped_filename}"

    return response


@app.post("/minio/{path_name:path}")
async def object_post(
    path_name: str, file: Optional[UploadFile], tags: Optional[str] = "{}"
):
    """
    Create/Update object
    :param path_name: filename ex /data/sheet3.csv
    :param response:
    :param token: access token
    :param file: upload file
    :param tags: json (key/value) for tags cannot be thai language ex {"project": "project name"}
    :return:
    """
    man = MinIoManager()
    print("object_post")
    print("path_name", path_name)
    old_tags = man.get_object_tags(path_name)
    if old_tags is None:
        old_tags = {}
    m_tags = {**old_tags, **json.loads(tags)}
    print("m_tags", m_tags)

    if file is not None:
        mime = magic.Magic(mime=True)
        file.file.seek(0)
        m_tags["content_type"] = mime.from_buffer(file.file.read(1024))
        file.file.seek(0)
        res = man.put_object_stream(path_name, file.file, -1, m_tags)
    else:
        res = man.set_object_tags(path_name, m_tags)

    return {"status": "success", "object": res, "tags": m_tags}


@app.post("/predict")
async def predict(picture: UploadFile = File(...)):
    try:
        image_bytes = await picture.read()
        image = Image.open(io.BytesIO(image_bytes))

        decimer_image_classifier = DecimerImageClassifier()
        score = decimer_image_classifier.get_classifier_score(image)
        is_chem = decimer_image_classifier.is_chemical_structure(image)

        # Save the image to MinIO
        man = MinIoManager()
        mine = magic.Magic(mime=True)
        picture.file.seek(0)
        content_type = mine.from_buffer(picture.file.read(1024))
        picture.file.seek(0)
        tags = {
            "content_type": content_type,
            "upload_time": datetime.now(timezone.utc).isoformat(),
            "is_chem": is_chem,
            "is_chem_score": score,
        }
        file_ext = os.path.splitext(picture.filename)[1]
        filename = f"classification/{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}{file_ext}"
        minio_res = man.put_object_stream(filename, picture.file, -1, tags)

    except Exception as e:
        traceback.print_exc()
        return {
            "status": "error",
            "info": "Failed to classify the image",
            "detail": str(e),
        }

    return {
        "status": "success",
        "filename": picture.filename,
        "score": float(score),
        "is_chem": is_chem,
        "minio_res": minio_res,
    }
