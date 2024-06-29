from fastapi import FastAPI

ROOT_PATH = "/api"
DOCS_PATH = "/docs"

app = FastAPI(
    title="Honeycomb Service",
    root_path=ROOT_PATH,
    docs_url=DOCS_PATH,
)


@app.get("/")
async def root():
    return {"message": "OK"}
