import io
from PIL import Image
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import RedirectResponse

from decimer_image_classifier.decimer_image_classifier import DecimerImageClassifier

ROOT_PATH = "/cls/api"
DOCS_PATH = "/docs"

app = FastAPI(
    title="Honeycomb Classification Service",
    root_path=ROOT_PATH,
    docs_url=DOCS_PATH
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
        "raw_url": str(request.url)
    }


@app.post("/predict")
async def predict(picture: UploadFile = File(...)):
    try:
        image_bytes = await picture.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        decimer_image_classifier = DecimerImageClassifier()
        score = decimer_image_classifier.get_classifier_score(image)
        is_chem = decimer_image_classifier.is_chemical_structure(image)
    except Exception as e:
        return {
            "status": "error",
            "info": "Failed to classify the image",
            "detail": str(e)
        }
    
    return {
        "status": "success",
        "filename": picture.filename,
        "score": float(score),
        "is_chem": is_chem        
    }