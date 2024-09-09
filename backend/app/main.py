import html
import json
import httpx
import os
from typing import Optional

import logging

import magic
from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    Request,
    Response,
    UploadFile,
    File
)
from starlette.responses import StreamingResponse

from app.minio_manager.manager import MinIoManager
from app.session_manager import SessionIn, SessionManager

ROOT_PATH = "/api"
DOCS_PATH = "/docs"

app = FastAPI(
    title="Honeycomb Service",
    root_path=ROOT_PATH,
    docs_url=DOCS_PATH,
)

logger = logging.getLogger(__name__)

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
        man =  SessionManager()
        res = man.get_session(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return res

@app.post("/session")
async def session_post(sessionIn: SessionIn):
    try:
        man = SessionManager()
        res = man.create_session(sessionIn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return res


@app.put("/session/{session_id}")
async def update_session(session_id: int, sessionIn: SessionIn):
    try:
        man = SessionManager()
        res = man.update_session(session_id, sessionIn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return res


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


async def process_file(session_id: str,
                       file_content: bytes, 
                       filename: str, 
                       content_type: str):
    obj = {
        "segmentation_path": None,
        "classification_path": None,
        "clasification_data": None,
        "transformation_path": None,
        "transformation_data": None
    }    
    
    step = "segmentation"
    try:
        minio_man = MinIoManager()
        sess_man = SessionManager()
        
        # segmentation
        logger.info(f"Segmenting the image - session_id: {session_id}")
        files = {"file": (filename, file_content, content_type)}

        async with httpx.AsyncClient(timeout=300) as client:
            seg_res = await client.post("http://seg:80/seg/api/predict", files=files)
            seg_res = seg_res.json()
        
        seg_paths = [s.get('_object_name') for s in seg_res['segments']]
        logger.info("Segmentation successful")
        obj['segmentation_path'] = ",".join(seg_paths)
        sess_man.update_session(session_id, SessionIn(**obj))
        
        # classification
        logger.info(f"Classifying the image - session_id: {session_id} - segment_count: {len(seg_res['segments'])}")
        is_chems = []
        smiles = []
        cls_paths = []
        trans_paths = []
        
        async with httpx.AsyncClient(timeout=300) as client:
            for path in seg_paths:
                step = "classification"
                picture = minio_man.get_object_content(path, decode=False)
                cls_res = await client.post("http://cls:80/cls/api/predict", files={"file": picture})
                cls_res = cls_res.json()
                
                is_chem = cls_res.get('is_chem')
                is_chems.append(str(is_chem))
                cls_paths.append(cls_res.get('minio_res', {}).get('_object_name'))
                
                if is_chem:
                    step = "transformation"
                    logger.info(f"Transforming the image - session_id: {session_id} - segment_path: {path}")
                    trans_res = await client.post("http://trans:80/trans/api/predict", files={"file": picture})
                    trans_res = trans_res.json()
                    smiles.append(trans_res.get('SMILES'))
                    trans_paths.append(trans_res.get('minio_res', {}).get('_object_name')) 
                else:
                    logger.info(f"Chemical structure not detected - session_id: {session_id} - segment_path: {path}")
                    smiles.append("N/A")
                    trans_paths.append("N/A")
        
        logger.info(f"Updating session - session_id: {session_id}")
        obj['classification_path'] = ",".join(cls_paths)
        obj["clasification_data"] = ",".join(is_chems)
        obj['transformation_path'] = ",".join(trans_paths)
        obj["transformation_data"] = ",".join(smiles)
        sess_man.update_session(session_id, SessionIn(**obj))
        
        logger.info(f"Processing complete - session_id: {session_id}")
    except Exception as e:
        logger.error(f"Error in {step}: {str(e)}")


@app.post("/predict")
async def predict(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        file_content = await file.read() 
        filename = file.filename 
        content_type = file.content_type
        
        sess_man = SessionManager()
        session = sess_man.create_session(SessionIn())
        session_id = session.get('row_id')
        
        if session_id is None:
            raise HTTPException(status_code=500, detail="Failed to create a session")
        
        # Add the file processing task to run in the background
        background_tasks.add_task(process_file, session_id, file_content, filename, content_type)
        
        return {
            "status": "success",
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))