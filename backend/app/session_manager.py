import sqlite3
from pydantic import BaseModel
from typing import Optional
from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    Request,
    Response,
    UploadFile,
    File
)

class SessionIn(BaseModel):
    segmentation_path: Optional[str] = None
    classification_path: Optional[str] = None
    clasification_data: Optional[str] = None
    transformation_path: Optional[str] = None
    transformation_data: Optional[str] = None


class SessionManager:
    
    def __init__(self, path=None):
        self.path = "./data/data.db"
        if path:
            self.path = path

    
    def get_session(self, session_id=None) -> dict:
        conn = sqlite3.connect(self.path)
        try:
            sql = "SELECT * FROM session WHERE 1"
            if session_id:
                sql += f" AND id = {session_id}"

            cursor = conn.cursor()
            cursor.execute(sql)
            res = cursor.fetchall()

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()

        return {"data": res}


    def create_session(self, sessionIn: SessionIn) -> dict:
        conn = sqlite3.connect(self.path)
        try:
            sql = f"""
            INSERT INTO session (segmentation_path, classification_path, classification_data, transformation_path, transformation_data) 
            VALUES ('{sessionIn.segmentation_path}', '{sessionIn.classification_path}',  '{sessionIn.clasification_data}', '{sessionIn.transformation_path}', '{sessionIn.transformation_data}')
            """
            cursor = conn.cursor()
            cursor.execute(sql)
            row_id = cursor.lastrowid
            conn.commit()

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()

        return {"row_id": row_id}
    
    def update_session(self, session_id: str, sessionIn: SessionIn) -> dict:
        conn = sqlite3.connect(self.path)
        try:
            if all(v is None for v in sessionIn.model_dump().values()):
                raise HTTPException(status_code=400, detail="At least one path is required")

            sql = f"""
                UPDATE session
                SET
                    segmentation_path = '{sessionIn.segmentation_path}',
                    classification_path = '{sessionIn.classification_path}',
                    classification_data = '{sessionIn.clasification_data}',
                    transformation_path = '{sessionIn.transformation_path}',
                    transformation_data = '{sessionIn.transformation_data}'
                WHERE id = {session_id}
            """

            cursor = conn.cursor()
            cursor.execute(sql)
            res = cursor.rowcount
            conn.commit()

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            conn.close()
    
        return {"row_count": res}