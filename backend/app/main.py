import html
import magic
import json

from typing import Optional

import sqlite3

from fastapi import FastAPI, Request, HTTPException, Response, UploadFile, File, Request
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from app.minio_manager.manager import MinIoManager

ROOT_PATH = "/api"
DOCS_PATH = "/docs"

app = FastAPI(
    title="Honeycomb Service",
    root_path=ROOT_PATH,
    docs_url=DOCS_PATH,
)


@app.get("/")
async def root():
    return {"message": "root"}


@app.get("/ping")
async def ping():
    return {"message": "OK"}


@app.get("/about")
async def about(request: Request):
    return {"raw_url": str(request.url)}


@app.get("/session")
async def session_search(session_id: Optional[int] = None):
    try:
        sql = "SELECT * FROM session WHERE 1"
        if session_id:
            sql += f" AND id = {session_id}"
        
        conn = sqlite3.connect("./data/data.db")
        cursor = conn.cursor() 
        cursor.execute(sql)
        res = cursor.fetchall()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    return {"data": res}

class SessionIn(BaseModel):
    segmentation_path: Optional[str] = None
    classification_path: Optional[str] = None
    transformation_path: Optional[str] = None
    

@app.post("/session")
async def session_post(sessionIn: SessionIn):
    try:
        if all(v is None for v in sessionIn.model_dump().values()):
            raise HTTPException(status_code=400, detail="At least one path is required")
        
        sql = f"INSERT INTO session (segmentation_path, classification_path, transformation_path) VALUES ('{sessionIn.segmentation_path}', '{sessionIn.classification_path}', '{sessionIn.transformation_path}')"
        conn = sqlite3.connect("./data/data.db")
        cursor = conn.cursor()
        cursor.execute(sql)
        row_id = cursor.lastrowid
        conn.commit()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    return {"row_id": row_id}


@app.put("/session/{session_id}")
async def update_session(session_id: int, sessionIn: SessionIn):
    try:
        if all(v is None for v in sessionIn.model_dump().values()):
            raise HTTPException(status_code=400, detail="At least one path is required")
        
        sql = f"""
            UPDATE session
            SET
                segmentation_path = '{sessionIn.segmentation_path}',
                classification_path = '{sessionIn.classification_path}',
                transformation_path = '{sessionIn.transformation_path}'
            WHERE id = {session_id}
        """
        conn = sqlite3.connect("./data/data.db")
        cursor = conn.cursor()
        cursor.execute(sql)
        res = cursor.rowcount
        conn.commit()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
        
    return {"row_count": res}


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

