from fastapi import FastAPI

app = FastAPI()


@app.get("/lookup")
async def lookup(source_language: str, target_language: str, query: str):
    results = []

    return {"results": results}
