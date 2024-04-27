import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/json', '.mjs')
mimetypes.add_type('text/css', '.css')

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


import os
import json

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


@app.get("/create_user_log")
async def rand(username: str):
    filename = "user_data/" + username + "/eventlog_" + username + ".json"
    
    if os.path.exists(filename):
        return "log already exists. No change required."
    else:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write("[]")
        return "successfully created logfile."
    

@app.get("/create_custom_log")
async def create_custom_log(username: str):
    filename = "user_data/" + username + "/customlog_" + username + ".json"
    
    if os.path.exists(filename):
        return "log already exists. No change required."
    else:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write("[]")
        return "successfully created custom logfile."


@app.get("/append_user_log")
async def append_user_log(req: Request):
    request_args = dict(req.query_params)
    filename = "user_data/" + request_args['username'] + "/eventlog_" + request_args['username'] + ".json"

    with open(filename, "r") as f:
        listObj = json.load(f)
    
    listObj.append(json.loads(request_args['req']))

    with open(filename, 'w') as json_file:
        json.dump(listObj, json_file, 
                            indent=4,  
                            separators=(',',': '))
        
    return "successfully Appended event to" + request_args['username'] + "' log file."


@app.post("/create_event_user_log")
async def create_event_user_log(req: Request):
    params = await req.json()

    #print(params['timestamp'])
    filename = "user_data/" + params['username'] + "/" + str(params['timestamp']) + "_" + params['username'] + ".json"

    if os.path.exists(filename):
        return "log already exists. No change required."
    else:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write("[]")
            
    with open(filename, "r") as f:
        listObj = json.load(f)
    
    listObj.append(params['log'])

    with open(filename, 'w') as json_file:
        json.dump(listObj, json_file, 
                            indent=4,  
                            separators=(',',': '))
        
    return "successfully Appended customs to" + params['username'] + "' log file."

@app.post("/append_custom_user_log")
async def append_custom_user_log(req: Request):
    params = await req.json()

    filename = "user_data/" + params['username'] + "/customlog_" + params['username'] + ".json"

    with open(filename, "r") as f:
        listObj = json.load(f)
    
    listObj.append(params['log'])

    with open(filename, 'w') as json_file:
        json.dump(listObj, json_file, 
                            indent=4,  
                            separators=(',',': '))
        
    return "successfully Appended customs to" + params['username'] + "' log file."

## THE ORDER OF THESE ROUTES MATTERS... Do not place this first.
@app.get("/", response_class=FileResponse)
def main():
    return "public/index.html"