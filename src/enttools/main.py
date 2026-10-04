from fastapi import FastAPI, HTTPException
from enttools.mcp import InputError, call, list_tools

app = FastAPI()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/tools")
def tools():
    return list_tools()


@app.post("/call")
def post_call(body: dict):
    try:
        return call(body.get("name"), body.get("arguments"))
    except InputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
