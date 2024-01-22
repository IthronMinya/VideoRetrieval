import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/json', '.mjs')
mimetypes.add_type('text/css', '.css')

#import uvicorn
#import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import random

import requests

#import open_clip
#import torch

import numpy as np

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory="public/assets"), name="static")

@app.get("/", response_class=FileResponse)
def main():
    return "public/index.html"

@app.get("/rand")
async def hello():
   return random.randint(0, 100)

@app.get("/send_results")
async def send_result(image_id: int):

    my_obj = {'team': "VBS", 'item': image_id}

    print(image_id)

    x = requests.get(url="https://siret.ms.mff.cuni.cz/lokoc/VBSEval/EndPoint.php", params=my_obj, verify=False)

    print(x.text)