import os
import time
from typing import Annotated

from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .modules.router import router as ApplicationRouter
from .modules.errors import exceptionToHTTPResponse

app = FastAPI(prefix = None)

origins = [
    "http://localhost",
    "localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.exception_handler(Exception)
async def validation_exception_handler(request, exception):
    return exceptionToHTTPResponse(exception)

@app.get("/", tags=["root"])
async def read_root(accept: Annotated[str | None, Header()] = "application/json"):
    if(accept == "application/json"):
        return JSONResponse(content={"message": "Welcome to your the API."}, status_code=200)
    else:
        return HTMLResponse(content="<h1>Welcome to the API", status_code=200)

app.include_router(ApplicationRouter)

app.mount("/", StaticFiles(directory="app/public"), name="public")
