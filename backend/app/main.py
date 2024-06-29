from fastapi import FastAPI, Request

ROOT_PATH = "/api/"
DOCS_PATH = "/docs/"

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
