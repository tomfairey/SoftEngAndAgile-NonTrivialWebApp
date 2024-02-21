from typing import Annotated

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates

app = FastAPI()

origins = [
    "http://localhost:80",
    "localhost:80"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# templates = Jinja2Templates(directory="templates")

# async def read_root() -> dict:
#     return {"message": "Welcome to your todo list."}

@app.get("/", tags=["root"])
async def read_root(accept: Annotated[str | None, Header()] = "application/json"):
    if(accept == "application/json"):
        return JSONResponse(content={"message": "Welcome to your todo list."}, status_code=200)
    else:
        return HTMLResponse(content="<h1>Welcome to your todo list.</h1>", status_code=200)

app.mount("/", StaticFiles(directory="app/public"), name="public")