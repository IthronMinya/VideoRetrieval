import datetime
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
import asyncio

app = FastAPI()

origins = [ "*" ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory="public/assets"), name="static")

logging.basicConfig(level=logging.INFO)

# variables to store history of users actions
image_items = {}
action_pointer = {}
max_display = 500

passwords = {f'06prak{str(i)}': 'Japan' for i in range(1, 10)}

logins = {"06prak1": "Y9S6HyLPahMR", "06prak2": "hCdc2ZSR5Uag", "06prak3": "Yr9u2V5WE3GK", "06prak4": "n62HaNrx9gWj", "06prak5": "uwB32zTQayY4", "06prak6": "VGJ8p5QWCPZX", "06prak7": "ak6sXPwve7E3", "06prak8": "J2RWD3F9Kqnr", "06prak9": "hJQ5K8ruemDy"}

def normalizeVector(vector):
    norm = np.linalg.norm(vector)
    return vector / norm if norm else vector * 0


def normalizeMatrix(matrix):
    return np.array([normalizeVector(row) for row in matrix])


async def append_log(username, request):
    filename = os.path.join("user_data", username, f"eventlog_{username}.json")
    
    if not os.path.exists(filename): # if the file does not exist, create it
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
                f.write("[]")

    try:
        with open(filename, "r") as f:
            listObj = json.load(f)
        
        listObj.append(request)

        with open(filename, 'w') as json_file:
            json.dump(listObj, json_file, indent=4, separators=(',',': '))
    except Exception as e:
        logging.error(f"An error occurred while appending to the log file: {str(e)}")
        raise e
    
    
async def create_event_log(username, timestamp, log):    
    filename = os.path.join("user_data", username, f"{timestamp}_{username}.json")

    if os.path.exists(filename): # if the file already exists, do not create a new one
        return
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write("[]")
            
    with open(filename, "r") as f:
        listObj = json.load(f)
    
    listObj.append(log)

    with open(filename, 'w') as json_file:
        json.dump(listObj, json_file, indent=4, separators=(',',': '))
        
        
async def preproccess_create_event_log(username, timestamp, query, my_obj, data):
    my_obj = json.loads(my_obj)
    events = [{'category': 'TEXT' if query in ['textQuery', 'temporalQuery', 'filter'] else 'IMAGE', 'value': my_obj['query'] if 'query' in my_obj else (my_obj['item_id'] if 'item_id' in my_obj else (my_obj['filters'] if 'filters' in my_obj else None))}]
    
    if query == 'filter':
        events[0]['type'] = 'metadata'
        
    if 'filters' in my_obj and my_obj['filters'] and query != 'filter':
        events.append({'category': 'TEXT', 'type': 'metadata', 'value': my_obj['filters']})
        
    log = {
        'timestamp': timestamp, 
        'events': events, 
        'results': [
            {
                **{k: v for k, v in item.items() if k != 'features' and k != 'label' and k != 'time' and k != 'uri' and k != 'id'},
                'item': item['id'][0],
                'frame': item['id'][1]
            } 
            for item in data
        ]
    }

    await create_event_log(username, timestamp, log)
    

async def preproccess_and_create_event_log(username, timestamp, log):
    log['results'] = [
        {
            **{k: v for k, v in item.items() if k != 'features' and k != 'label' and k != 'time' and k != 'uri' and k != 'id'},
            'item': item['id'][0],
            'frame': item['id'][1]
        } 
        for item in log['results']
    ]

    await create_event_log(username, timestamp, log)


@app.post("/create_user_log")
async def create_user_log(req: Request):
    try:
        params = await req.json()
        username = params['username'] if 'username' in params else None
        if not username:
            raise HTTPException(status_code=400, detail="Missing username parameter")
        
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


@app.post("/append_user_log")
async def append_user_log(req: Request):
    params = await req.json()
    username = params['username'] if 'username' in params else None
    if not username:
        raise HTTPException(status_code=400, detail="Missing username parameter")
    
    request = params['log'] if 'log' in params else None
    if not request:
        raise HTTPException(status_code=400, detail="Missing log parameter")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    request['timestamp'] = timestamp

    try:
        asyncio.create_task(append_log(username, request))
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
    
    timestamp = params.get('timestamp') if 'timestamp' in params else datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    log = params.get('log')
    if not log:
        raise HTTPException(status_code=400, detail="Missing log parameter")
    
    asyncio.create_task(create_event_log(username, timestamp, log))
        
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
    is_reset = params['reset'] if 'reset' in params else False
    
    if url is None or dataset is None or username is None:
        raise HTTPException(status_code=400, detail="Missing required parameters.")

    try:
        if image_upload:
            response = requests.post(url=url, headers={'Content-Type': 'application/json'}, data=my_obj, verify=False)
        else:
            response = requests.post(url=url, data=my_obj, verify=False)
            
        data = response.json()
    except Exception as e:
        logging.error(f"An error occurred while sending the request to the service: {str(e)}")
        raise HTTPException(status_code=400, detail=f"An error occurred while sending the request to the service: {str(e)}")
    
    new_data = []
    
    if sorted:
        if dataset == 'LSC':
            data.sort(key=lambda x: (int(x.get('uri', '').split('/')[-1].split('_')[0]), int(x.get('uri', '').split('_')[1])))
        else:
            part = 1 if dataset in ['V3C'] else -1
            data.sort(key=lambda x: int(x.get('uri', '').split('/')[-1].split('.')[0].split('_')[part]))
    
    if username not in image_items or is_reset:
        image_items[username] = [data]
        action_pointer[username] = 0
    else:
        if len(image_items[username]) > action_pointer[username] + 1:
            image_items[username] = image_items[username][:action_pointer[username] + 1]
            action_pointer[username] += 1
        elif len(image_items[username]) > 10:
            image_items[username] = image_items[username][1:]
        else:
            action_pointer[username] += 1

        image_items[username].append(data)
    
    new_data = [{k: v for k, v in item.items() if k != 'features' and k != 'score'} for item in data[:max_display]]
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    query = url.split('/')[-2]
    load_obj = json.loads(my_obj)
    asyncio.create_task(append_log(username, {'action': query, 'timestamp': timestamp, 'data_file': f"{timestamp}_{username}.json", 'value': load_obj['query'] if 'query' in load_obj else (load_obj['item_id'] if 'item_id' in load_obj else (load_obj['filters'] if 'filters' in load_obj else None))}))
    asyncio.create_task(preproccess_create_event_log(username, timestamp, query, my_obj, data))

    return new_data, action_pointer[username]


@app.post("/bayes")
async def bayes(req: Request):
    request_args = await req.json()
    selected_images = request_args['selected_images'] if 'selected_images' in request_args else None
    alpha = 0.01
    username = request_args['username'] if 'username' in request_args else None
    
    if selected_images is None or username is None:
        raise HTTPException(status_code=400, detail="Missing required parameters.")
    
    if username not in image_items:
        logging.error(f"User {username} hasn't data from last query.")
        return "No images to compare. Please initialize them with a query!"
    
    if 'score' not in image_items[username][action_pointer[username]][0]:
        return "No Score to compare images with. Please initialize them with a query!"

    DeepCopyImageItems = image_items[username][action_pointer[username]].copy()
    imageFeatureVectors = normalizeMatrix([item['features'] for item in image_items[username][action_pointer[username]]])

    items = image_items[username][action_pointer[username]].copy()
    max_rank = max([item['rank'] for item in items if item['id'] in selected_images]) + 5

    topDisplay = items[:min(len(items), max_rank)]

    negativeExamples = [item['features'] for item in topDisplay if item['id'] not in selected_images]
    positiveExamples = [item['features'] for item in items if item['id'] in selected_images]

    positiveExamples = normalizeMatrix(positiveExamples)
    negativeExamples = normalizeMatrix(negativeExamples)

    # Calculate products
    prod_positive = positiveExamples @ imageFeatureVectors.T
    prod_negative = negativeExamples @ imageFeatureVectors.T

    # Calculate PF and NF
    PF = np.sum(np.exp(- (1 - prod_positive) / alpha), axis=0)
    NF = np.sum(np.exp(- (1 - prod_negative) / alpha), axis=0)

    # Update scores
    for i, item in enumerate(DeepCopyImageItems):
        item['score'] *= PF[i] / NF[i]

    items = DeepCopyImageItems.copy()
    
    # Sort the array based on the second element
    items.sort(key=lambda x: x['score'], reverse=True)

    for i, item in enumerate(items):
        item['rank'] = i

    if len(image_items[username]) > action_pointer[username] + 1:
        image_items[username] = image_items[username][:action_pointer[username] + 1]
        action_pointer[username] += 1
    elif len(image_items[username]) > 10:
        image_items[username] = image_items[username][1:]
    else:
        action_pointer[username] += 1
    image_items[username].append(items)
    
    new_data = [{k: v for k, v in item.items() if k != 'features'} for item in items[:max_display]]
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    asyncio.create_task(append_log(username, {'action': 'bayes', 'timestamp': timestamp, 'data_file': f"{timestamp}_{username}.json"}))
    asyncio.create_task(preproccess_and_create_event_log(username, timestamp, {'timestamp': timestamp, 'events': [{'category': 'IMAGE', 'type': 'feedbackModel', 'value': 'framesId ' + " ".join(['_'.join(image) for image in selected_images])}], 'results': items}))
    
    return new_data


@app.post("/back")
async def back(req: Request):
    request_args = await req.json()
    username = request_args['username'] if 'username' in request_args else None
    
    if username not in image_items:
        logging.error(f"User {username} hasn't data from last query.")
        return "No images to compare. Please initialize them with a query!"
    
    if action_pointer[username] == 0:
        logging.error(f"User {username} is already at the first query.")
        return "No previous query to go back to."
    
    action_pointer[username] = action_pointer[username] - 1
    new_data = [{k: v for k, v in item.items() if k != 'features'} for item in image_items[username][action_pointer[username]][:max_display]]
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    asyncio.create_task(append_log(username, {'action': 'back', 'timestamp': timestamp}))
    
    return new_data, action_pointer[username]


@app.post("/forward")
async def forward(req: Request):
    request_args = await req.json()
    username = request_args['username'] if 'username' in request_args else None
    
    if username not in image_items:
        logging.error(f"User {username} hasn't data from last query.")
        return "No images to compare. Please initialize them with a query!"
    
    if action_pointer[username] == len(image_items[username]) - 1:
        logging.error(f"User {username} is already at the last query.")
        return "No next query to go forward to."
    
    action_pointer[username] = action_pointer[username] + 1
    new_data = [{k: v for k, v in item.items() if k != 'features'} for item in image_items[username][action_pointer[username]][:max_display]]
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    asyncio.create_task(append_log(username, {'action': 'forward', 'timestamp': timestamp}))
    
    return new_data, action_pointer[username]


@app.post("/get_filters")
async def get_filters(req: Request):
    request_args = await req.json()
    dataset = request_args['dataset'] if 'dataset' in request_args else None
    
    if dataset is None:
        raise HTTPException(status_code=400, detail="Missing required parameters.")
    
    try:
        response = requests.get(f"http://vbs-backend-data-layer-1:80/getFilters", params={'dataset': dataset})
    except Exception as e:
        logging.error(f"An error occurred while sending the request to the service: {str(e)}")
        raise HTTPException(status_code=400, detail=f"An error occurred while sending the request to the service: {str(e)}")
    
    filters = response.json()
    
    return filters['filters']


@app.post("/login")
async def login(req: Request):
    request_args = await req.json()
    username = request_args['username'] if 'username' in request_args else None
    password = request_args['password'] if 'password' in request_args else None
    
    if username is None or password is None:
        raise HTTPException(status_code=400, detail="Missing required parameters.")
    
    if username not in passwords or passwords[username] != password:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    return logins[username]
    


## THE ORDER OF THESE ROUTES MATTERS... Do not place this first.
@app.get("/", response_class=FileResponse)
def main():
    return "public/index.html"
