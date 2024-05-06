import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/json', '.mjs')
mimetypes.add_type('text/css', '.css')

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import requests

import numpy as np
import os
import json
import logging

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

logging.basicConfig(level=logging.INFO)

image_items = {}
action_pointer = {}


def normalizeVector(vector):
    norm = np.linalg.norm(vector)
    return vector / norm if norm else vector * 0


def normalizeMatrix(matrix):
    return np.array([normalizeVector(row) for row in matrix])


@app.get("/create_user_log")
async def rand(username: str):
    try:
        filename = os.path.join("user_data", username, f"eventlog_{username}.json")
        
        if os.path.exists(filename):
            return "Log already exists. No change required."
        else:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as f:
                f.write("[]")
            return "Successfully created logfile."
    except Exception as e:
        logging.error(f"An error occurred while creating the log file: {str(e)}")
        return f"An error occurred: {str(e)}"


@app.get("/append_user_log")
async def append_user_log(req: Request):
    params = await req.json()
    username = params['username'] if 'username' in params else None
    if not username:
        raise HTTPException(status_code=400, detail="Missing username parameter")
    
    request = params.get['req'] if 'req' in params else None
    if not request:
        raise HTTPException(status_code=400, detail="Missing request parameter")

    filename = os.path.join("user_data", username, f"eventlog_{username}.json")
    
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="User log file not found.")

    try:
        with open(filename, "r") as f:
            listObj = json.load(f)
        
        listObj.append(json.loads(request))

        with open(filename, 'w') as json_file:
            json.dump(listObj, json_file, indent=4, separators=(',',': '))
    except Exception as e:
        logging.error(f"An error occurred while appending to the log file: {str(e)}")
        return f"An error occurred: {str(e)}"
        
    return f"Successfully appended event to {username}'s log file."


@app.post("/create_event_user_log")
async def create_event_user_log(req: Request):
    params = await req.json()
    username = params['username'] if 'username' in params else None
    if not username:
        raise HTTPException(status_code=400, detail="Missing username parameter")
    
    timestamp = str(params['timestamp']) if 'timestamp' in params else None
    if not timestamp:
        raise HTTPException(status_code=400, detail="Missing timestamp parameter")
    
    log = params.get('log')
    if not log:
        raise HTTPException(status_code=400, detail="Missing log parameter")
    
    filename = os.path.join("user_data", username, f"{timestamp}_{username}.json")

    if os.path.exists(filename):
        return "Log already exists. No change required."
    else:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write("[]")
            
    with open(filename, "r") as f:
        listObj = json.load(f)
    
    listObj.append(log)

    with open(filename, 'w') as json_file:
        json.dump(listObj, json_file, indent=4, separators=(',',': '))
        
    return f"Successfully appended customs to {username}'s log file."


@app.get("/get_user_log")
async def get_user_log(req: Request):
    params = await req.json()
    username = params['username'] if 'username' in params else None
    if not username:
        raise HTTPException(status_code=400, detail="Missing username parameter")
    
    filename = os.path.join("user_data", username, f"eventlog_{username}.json")

    with open(filename, "r") as f:
        listObj = json.load(f)
    
    return listObj


@app.post("/send_request_to_service")
async def send_request_to_service(req: Request):
    params = await req.json()
    url = params['url'] if 'url' in params else None
    my_obj = params['body'] if 'body' in params else {}
    image_upload = params['image_upload'] if 'image_upload' in params else False
    sorted = params['sorted'] if 'sorted' in params else False
    dataset = params['dataset'] if 'dataset' in params else None
    username = params['username'] if 'username' in params else None
    
    if url is None or dataset is None or username is None:
        raise HTTPException(status_code=400, detail="Missing required parameters.")

    if image_upload:
        response = requests.post(url=url, headers={'Content-Type': 'application/json'}, data=my_obj, verify=False)
    else:
        response = requests.post(url=url, data=my_obj, verify=False)
    
    data = response.json()
    
    new_data = []
    
    # TODO on server side
    if sorted:
        part = 1 if dataset == 'V3C' else -1
        data.sort(key=lambda x: int(x.get('uri', '').split('_')[part].split('.')[0]))
      
    if username not in image_items:
        image_items[username] = data
        action_pointer[username] = 0
    else:
        image_items[username].extend(data)
        action_pointer[username] = action_pointer[username] + 1
    
    new_data = [{k: v for k, v in item.items() if k != 'features' and k != 'score'} for item in data]

    return new_data


@app.post("/bayes") #TODO: used matrix multiplication instead of loop
async def bayes(req: Request):
    request_args = await req.json()
    selected_images = request_args['selected_images'] if 'selected_images' in request_args else None
    alpha = request_args['alpha'] if 'alpha' in request_args else None
    username = request_args['username'] if 'username' in request_args else None
    
    if selected_images is None or alpha is None or username is None:
        raise HTTPException(status_code=400, detail="Missing required parameters.")
    
    if 'score' not in image_items[username][action_pointer[username]][0]:
        return "No Score to compare images with. Please initialize them with a query!"

    DeepCopyImageItems = image_items[username][action_pointer[username]].copy()
    imageFeatureVectors = normalizeMatrix([item['features'] for item in image_items[username][action_pointer[username]]])

    items = image_items[username][action_pointer[username]].copy()
    max_rank = 200 # TODO: rewrite value for this variable

    topDisplay = items[:min(len(items), max_rank)]

    negativeExamples = [item['features'] for item in topDisplay if item['id'] not in selected_images]
    positiveExamples = [item['features'] for item in items if item['id'] in selected_images]

    positiveExamples = normalizeMatrix(positiveExamples)
    negativeExamples = normalizeMatrix(negativeExamples)

    for i, item in enumerate(items): # TODO: used matrix multiplication instead of loop
        featureVector = imageFeatureVectors[i]

        prod_positive = np.dot(positiveExamples, featureVector)
        prod_negative = np.dot(negativeExamples, featureVector)
        
        PF = np.sum(np.exp(- (1 - prod_positive) / alpha))
        NF = np.sum(np.exp(- (1 - prod_negative) / alpha))

        DeepCopyImageItems[i]['score'] *= PF / NF

    items = DeepCopyImageItems.copy()
    
    # Sort the array based on the second element
    items.sort(key=lambda x: x['score'], reverse=True)

    for i, item in enumerate(items):
        item['rank'] = i

    image_items[username].append(items)
    
    new_data = [{k: v for k, v in item.items() if k != 'features'} for item in items]
    
    return new_data


## THE ORDER OF THESE ROUTES MATTERS... Do not place this first.
@app.get("/", response_class=FileResponse)
def main():
    return "public/index.html"