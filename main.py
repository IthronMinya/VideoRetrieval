import datetime
import mimetypes
import requests
import os
import json
import logging
import asyncio
import jwt

import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext


# Add custom mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/json', '.mjs')
mimetypes.add_type('text/css', '.css')


# Load environment variables from .env file
load_dotenv()

app = FastAPI()

origins = [ "*" ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files
app.mount("/assets", StaticFiles(directory="public/assets"), name="static")

# Configure logging
logging.basicConfig(level=logging.INFO)

# JWT and password hashing configurations
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Variables to store history of users actions
image_items = {}
action_pointer = {}
max_display = 500

# User database
users_db = {}
usernames = [f"06prak{i}" for i in range(1, 10)]
user_password = os.getenv("PASSWORD")

# Populate the users_db dictionary
for username in usernames:
    users_db[username] = {
        "username": username,
        "password": pwd_context.hash(user_password)
    }

# Load logins from environment variable
logins_json = os.getenv("LOGINS")
logins = json.loads(logins_json) if logins_json else {}

# Helper functions
def normalizeVector(vector):
    vector = np.array(vector, dtype=float)
    norm = np.linalg.norm(vector)
    return vector / norm if norm else vector * 0


def normalizeMatrix(matrix):
    return np.array([normalizeVector(row) for row in matrix])


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def send_request(url, my_obj, image_upload):
    headers = {'Content-Type': 'application/json'} if image_upload else {}
    try:
        response = requests.post(url=url, headers=headers, data=my_obj, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"An error occurred while sending the request to the service: {str(e)}")
        raise HTTPException(status_code=400, detail=f"An error occurred while sending the request to the service: {str(e)}")


async def append_log(username, request):
    # Append to the log file
    filename = os.path.join("user_data", username, f"eventlog_{username}.json")

    if not os.path.exists(filename): # if the file does not exist, create it
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
                f.write("[]")

    try:
        with open(filename, "r") as f:
            listObj = json.load(f)

        if isinstance(request, list):
            listObj.extend(request)  # allows appending multiple logs
        else:
            listObj.append(request)

        with open(filename, 'w') as json_file:
            json.dump(listObj, json_file, indent=4, separators=(',',': '))
    except Exception as e:
        logging.error(f"An error occurred while appending to the log file: {str(e)}")
        raise e
    
    
async def create_event_log(username, timestamp, log):
    # Create an event log file
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
    # Preprocess and create an event log file
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
    # Preprocess and create an event log file
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
    '''Create a log file for a user if it doesn't already exist.'''
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
    '''Append a log entry to a user's log file.'''
    params = await req.json()
    username = params['username'] if 'username' in params else None
    if not username:
        raise HTTPException(status_code=400, detail="Missing username parameter")

    request = params['log'] if 'log' in params else None
    if not request:
        raise HTTPException(status_code=400, detail="Missing log parameter")

    # provide timestamp if not one provided or batch log upload
    if not isinstance(request, list) and 'timestamp' not in request:
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
    '''Create an event log file for a user.'''
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
    '''Get the log file for a user.'''
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
    '''Send a request to a service and return the response.
    
    Parameters:
    - url: The URL of the service to send the request to.
    - body: The body of the request.
    - image_upload: Whether the request is an image upload request.
    - sorted: Whether the response should be sorted.
    - dataset: The dataset being used.
    - username: The username of the user making the request.
    - reset: Whether to reset the user's history.
    '''
    params = await req.json()
    
    url = params.get('url')
    my_obj = params.get('body', {})
    image_upload = params.get('image_upload', False)
    sorted = params.get('sorted', False)
    dataset = params.get('dataset')
    username = params.get('username')
    is_reset = params.get('reset', False)
    
    if url is None or dataset is None or username is None:
        raise HTTPException(status_code=400, detail="Missing required parameters.")

    data = await send_request(url, my_obj, image_upload)
    
    if not data:
        raise HTTPException(status_code=400, detail="Request didn't work...")
    
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
        
    if 'getVideoFrames' in url and json.loads(my_obj)['k'] == -1:
        new_data = [{k: v for k, v in item.items() if k != 'features' and k != 'score'} for item in data]
    else:
        new_data = [{k: v for k, v in item.items() if k != 'features' and k != 'score'} for item in data[:max_display]]
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    query = url.split('/')[-2]
    load_obj = json.loads(my_obj)
    
    query_value = load_obj['query'] if 'query' in load_obj else (load_obj['item_id'] if 'item_id' in load_obj else (load_obj['filters'] if 'filters' in load_obj else None))
    if 'query2' in load_obj and load_obj['query2'] != "":
        query_value += '|' + load_obj['query2']

    asyncio.create_task(append_log(username, {'action': query, 'timestamp': timestamp, 'data_file': f"{timestamp}_{username}.json", 'value': query_value}))
    asyncio.create_task(preproccess_create_event_log(username, timestamp, query, my_obj, data))

    return new_data, action_pointer[username]


@app.post("/bayes")
async def bayes(req: Request):
    '''Perform the Bayesian update on the images.
    
    Parameters:
    - selected_images: The selected images.
    - alpha: The alpha value.
    - username: The username of the user making the request.
    '''
    request_args = await req.json()
    
    selected_images = request_args.get('selected_images')
    alpha = request_args.get('alpha', 0.01)
    username = request_args.get('username')
    
    if selected_images is None or username is None:
        raise HTTPException(status_code=400, detail="Missing required parameters.")
    
    if username not in image_items:
        logging.error(f"User {username} hasn't data from last query.")
        return "No images to compare. Please initialize them with a query!"
    
    if 'score' not in image_items[username][action_pointer[username]][0]:
        return "No Score to compare images with. Please initialize them with a query!"
    
    if not isinstance(image_items[username][action_pointer[username]][0]['features'][0], int) or not isinstance(image_items[username][action_pointer[username]][0]['rank'], int):
        # Convert 'features' to array of int
        for item in image_items[username][action_pointer[username]]:
            item['features'] = np.array(item['features'], dtype=int)
            item['rank'] = int(item['rank'])
            item['score'] = float(item['score'])

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
    '''Go back to the previous query.
    
    Parameters:
    - username: The username of the user making the request.
    '''
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
    '''Go forward to the next query.
    
    Parameters:
    - username: The username of the user making the request.
    '''
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
    '''Get the filters for a dataset.
    
    Parameters:
    - dataset: The dataset to get the filters for.
    - server: The server to send the request to.
    '''
    request_args = await req.json()
    
    dataset = request_args['dataset'] if 'dataset' in request_args else None
    server = request_args['server'] if 'server' in request_args else "http://vbs-backend-data-layer-1:80"
    
    if dataset is None:
        raise HTTPException(status_code=400, detail="Missing required parameters.")
    
    try:
        response = requests.get(f"{server}/getFilters", params={'dataset': dataset})
    except Exception as e:
        logging.error(f"An error occurred while sending the request to the service: {str(e)}")
        raise HTTPException(status_code=400, detail=f"An error occurred while sending the request to the service: {str(e)}")
    
    filters = response.json()
    
    return filters['filters']


@app.post("/login")
async def login(req: Request):
    '''Login a user.
    
    Parameters:
    - username: The username of the user.
    - password: The password of the user.
    '''
    request_args = await req.json()
    username = request_args['username'] if 'username' in request_args else None
    password = request_args['password'] if 'password' in request_args else None

    if username is None or password is None:
        raise HTTPException(status_code=400, detail="Missing required parameters.")

    user = users_db.get(username)
    if username not in users_db and not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    return JSONResponse(content={"access_token": logins[username]})

## THE ORDER OF THESE ROUTES MATTERS... Do not place this first.
@app.get("/", response_class=FileResponse)
def main():
    return "public/index.html"