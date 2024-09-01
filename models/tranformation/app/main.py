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
    
@app.get("/predicted_result")
async def printresult():
    return {"smiles": SMILES}
    
@app.post("/prediction")
async def predict_smiles(file: UploadFile = File(...)):
    """
    Accepts an image file and returns the predicted SMILES string.
    """
    # Validate file type
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Only PNG and JPEG are supported.")

    try:
        # Read file contents
        contents = await file.read()

        # Save the file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(contents)
            temp_file_path = temp_file.name

        # Predict SMILES using the DECIMER model
        smiles_prediction = predict_SMILES(temp_file_path)

        # Clean up the temporary file
        os.remove(temp_file_path)

        # Return the prediction
        return {"smiles": smiles_prediction}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during prediction: {str(e)}")


