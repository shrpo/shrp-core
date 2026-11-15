from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict

from shrp_ai.core.engine import CoreEngine
from shrp_ai.core.interfaces import Request, Response


app = FastAPI(title="SHRP Core API", version="0.1.0")
core = CoreEngine()


class RequestModel(BaseModel):
    request_id: str
    module: str
    payload: Dict[str, Any]


@app.on_event("startup")
async def startup():
    await core.initialize()


@app.on_event("shutdown")
async def shutdown():
    await core.shutdown()


@app.get("/health")
async def health():
    return core.health()


@app.get("/v1/status")
async def status():
    return core.status()


@app.get("/v1/modules")
async def modules():
    return core.modules.list_modules()


@app.post("/v1/requests")
async def requests(req: RequestModel):
    r = Request(request_id=req.request_id, module=req.module, payload=req.payload)
    resp = await core.handle_request(r)
    return {"request_id": resp.request_id, "status": resp.status, "result": resp.result, "error": resp.error}
