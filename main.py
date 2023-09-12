import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/json', '.mjs')
mimetypes.add_type('text/css', '.css')

import uvicorn
import sys

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import random

app = FastAPI()

app.mount("/assets", StaticFiles(directory="public/assets"), name="static")

@app.get("/", response_class=FileResponse)
def main():
    return "public/index.html"

if __name__ == "__main__" and len(sys.argv) > 1:
    match sys.argv[1]:
        case 'dev' | "--dev" | "-d":
            print("dev")
            uvicorn.run("main:app", port=8002, reload=True)
        case _:
            uvicorn.run("main:app", port=8002)

@app.get("/rand")
async def hello():
   return random.randint(0, 100)