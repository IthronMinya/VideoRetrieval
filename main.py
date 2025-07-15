import asyncio
import ast
import datetime
import json
import logging
import mimetypes
import os
import time
from typing import Dict, List, Optional

import aiohttp
import jwt
import numpy as np
import orjson
import redis.asyncio as redis
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext


mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/json', '.mjs')
mimetypes.add_type('text/css', '.css')


# Load environment variables from .env file
load_dotenv()

# Constants
MAX_DISPLAY = 500
MAX_HISTORY = 10
JWT_ALGORITHM = "HS256"
REDIS_HOST = "redis"
REDIS_PORT = 6379
DEFAULT_JWT_EXPIRY_MINUTES = 15

# Environment configuration
SECRET_KEY = os.getenv("SECRET_KEY")
USER_PASSWORD = os.getenv("PASSWORD")
LOGINS_JSON = os.getenv("LOGINS")

# Configure FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static files
app.mount("/assets", StaticFiles(directory="public/assets"), name="static")

# Configure logging
logging.basicConfig(level=logging.INFO)


# JWT and password hashing configurations
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize user database
users_db = {}
usernames = [f"06prak{i}" for i in range(1, 10)]

# Populate the users_db dictionary
for username in usernames:
    users_db[username] = {
        "username": username,
        "password": pwd_context.hash(USER_PASSWORD)
    }

# Load logins from environment variable
logins = json.loads(LOGINS_JSON) if LOGINS_JSON else {}

# Initialize Redis client
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=False)

async def wait_for_redis(redis_client: redis.Redis, retries: int = 10, delay: int = 2) -> None:
    """Wait for Redis to become available."""
    for _ in range(retries):
        try:
            await redis_client.ping()
            return
        except Exception:
            print("Redis is loading... waiting to retry.")
            await asyncio.sleep(delay)
    raise Exception("Redis did not become ready in time.")


@app.on_event("startup")
async def startup() -> None:
    """FastAPI startup event handler."""
    await wait_for_redis(redis_client)


def user_key(username: str, field: str) -> str:
    """Generate Redis key for user-specific data."""
    return f"user:{username}:{field}"


def get_redis_keys(username: str) -> Dict[str, str]:
    """Get all Redis keys for a user."""
    return {
        "image_items": user_key(username, "image_items"),
        "limit_frames": user_key(username, "limit_frames"),
        "video_on_line": user_key(username, "video_on_line"),
        "scroll_position": user_key(username, "scroll_position"),
        "action_pointer": user_key(username, "action_pointer"),
    }


def normalizeVector(vector: List[float]) -> np.ndarray:
    """Normalize a vector to unit length."""
    vector = np.array(vector, dtype=float)
    norm = np.linalg.norm(vector)
    return vector / norm if norm else vector * 0


def normalizeMatrix(matrix: List[List[float]]) -> np.ndarray:
    """Normalize all vectors in a matrix to unit length."""
    return np.array([normalizeVector(row) for row in matrix])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=DEFAULT_JWT_EXPIRY_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def append_log(username: str, request: dict) -> None:
    """Append a log entry to a user's log file.
    
    Args:
        username: The username of the user.
        request: The request data to append to the log file.
    """
    filename = os.path.join("user_data", username, f"eventlog_{username}.json")

    if not os.path.exists(filename):  # if the file does not exist, create it
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
            json.dump(listObj, json_file, indent=4, separators=(',', ': '))
    except Exception as e:
        logging.error(f"An error occurred while appending to the log file: {str(e)}")
        raise e


async def create_event_log(username, timestamp, log):
    """Create an event log file for a user.
    
    Parameters:
    - username: The username of the user.
    - timestamp: The timestamp of the event.
    - log: The log to append to the event log file.
    """
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
    """Preprocess and create an event log file.
    
    Parameters:
    - username: The username of the user.
    - timestamp: The timestamp of the event.
    - query: The text query.
    - my_obj: The body of the request.
    - data: The data to append to the event log file.
    """
    if isinstance(my_obj, str):
        my_obj = json.loads(my_obj)
    events = [{'category': 'TEXT' if query in ['textQuery', 'temporalQuery', 'filter'] else 'IMAGE', 'value': my_obj['query'] if 'query' in my_obj else (my_obj['item_id'] if 'item_id' in my_obj else (my_obj['filters'] if 'filters' in my_obj else None))}]

    if query == 'filter':
        events[0]['type'] = 'metadata'

    if query == 'textQuery' and "position" in my_obj.keys():
        events[0]['position'] = my_obj['position']

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
    """Preprocess and create an event log file.
    
    Parameters:
    - username: The username of the user.
    - timestamp: The timestamp of the event.
    - log: The log to append to the event log file.
    """
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
    - req: The request object containing the parameters.
    '''
    params = await req.json()

    timings = {
        "T0_frontendStart": params.get("frontendStartTime"),
        "T1_backendReceived": time.time(),
    }

    if timings["T0_frontendStart"]:
        print(f"Waiting time: {(timings['T1_backendReceived'] - timings['T0_frontendStart']):.6f} secs")

    url = params['url'] if 'url' in params else None
    my_obj = params['body'] if 'body' in params else {}
    image_upload = params['image_upload'] if 'image_upload' in params else False
    sorted = params['sorted'] if 'sorted' in params else False
    dataset = params['dataset'] if 'dataset' in params else None
    username = params['username'] if 'username' in params else None
    is_reset = params['reset'] if 'reset' in params else False
    image_video_on_line = params['image_video_on_line'] if 'image_video_on_line' in params else False
    unique_video_frames = params['unique_video_frames'] if 'unique_video_frames' in params else False
    start = params['start'] if 'start' in params else 0

    if url is None or dataset is None or username is None:
        raise HTTPException(status_code=400, detail="Missing required parameters.")

    start_time = time.time()

    timings["T2_backendSendingToDataService"] = time.time()

    try:
        if image_upload:
            response = requests.post(url=url, headers={'Content-Type': 'application/json'}, data=my_obj)
            data = response.json()
        else:
            if isinstance(my_obj, str):
                my_obj = json.loads(my_obj)
            connector = aiohttp.TCPConnector(limit_per_host=100, force_close=False, ttl_dns_cache=30)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(url, json=my_obj) as response:
                    response.raise_for_status()

                    if response.status != 200:
                        text = await response.text()
                        logging.error(f"Error from service: {text}")
                        raise HTTPException(status_code=502, detail="Bad response from service")

                    # Read full body safely (even if large)
                    body = await response.read()

                    timings["T5_backendReceiveData"] = time.time()

                    try:
                        data = orjson.loads(body)
                    except Exception as e:
                        logging.error(f"Failed to parse service response: {e}")
                        logging.error(f"Raw response was: {body[:500]}")  # first 500 bytes
                        raise HTTPException(status_code=502, detail="Invalid response format from service")

    except Exception as e:
        logging.error(f"An error occurred while sending the request to the service: {str(e)}")
        raise HTTPException(status_code=400, detail=f"An error occurred while sending the request to the service: {str(e)}")

    if data == []:
        raise HTTPException(status_code=400, detail="Request didn't work...")

    timings["T5_backendReceiveJson"] = time.time()

    if not isinstance(data, (list, dict)):
        print(data)
        timings["T6_backendProcessingEnd"] = time.time()
        return {"timing": timings}

    execution_time = time.time() - start_time
    print(f'Getting data: {execution_time:.6f} secs')
    start_time = time.time()

    if len(data) > 100 or "getVideoFrames" in url:
       timings.update(data[-1])
       data = data[:-1]

    new_data = []

    if sorted:
        if dataset == 'LSC':
            data.sort(key=lambda x: (int(x.get('uri', '').split('/')[-1].split('_')[0]), int(x.get('uri', '').split('_')[1])))
        else:
            part = 1 if dataset in ['V3C'] else -1
            data.sort(key=lambda x: int(x.get('uri', '').split('/')[-1].split('.')[0].split('_')[part]))


    # Define Redis keys per user
    keys = get_redis_keys(username)

    if is_reset:
        await redis_client.delete(*keys.values())
        await redis_client.set(keys["action_pointer"], 0)
    else:
        current_action = await redis_client.get(keys["action_pointer"])
        current_action = int(current_action or 0)

        # Trim forward history if we've moved back and are adding a new step
        for field in ["image_items", "limit_frames", "video_on_line", "scroll_position"]:
            await redis_client.ltrim(keys[field], 0, current_action)

        await redis_client.set(keys["action_pointer"], current_action + 1 if current_action < 9 else 9)

    # Add new values to each list
    await redis_client.rpush(keys["image_items"], orjson.dumps(data))
    await redis_client.rpush(keys["limit_frames"], orjson.dumps(unique_video_frames))
    await redis_client.rpush(keys["video_on_line"], orjson.dumps(image_video_on_line))
    await redis_client.rpush(keys["scroll_position"], orjson.dumps(start))

    # Trim lists to max length
    for key in [keys["image_items"], keys["limit_frames"], keys["video_on_line"], keys["scroll_position"]]:
        await redis_client.ltrim(key, -MAX_HISTORY, -1)


    if 'getVideoFrames' in url and my_obj['k'] == -1:
        new_data = [{k: v for k, v in item.items() if k != 'features' and k != 'score'} for item in data]
    else:
        new_data = [{k: v for k, v in item.items() if k != 'features' and k != 'score'} for item in data[:MAX_DISPLAY]]

    execution_time = time.time() - start_time
    print(f'Processing data: {execution_time:.6f} secs')
    start_time = time.time()

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    query = url.split('/')[-2]
    load_obj = my_obj

    # get query value
    query_value = load_obj['query'] if 'query' in load_obj else (load_obj['item_id'] if 'item_id' in load_obj else (load_obj['filters'] if 'filters' in load_obj else None))
    # append second query if it's temporal text query
    if 'query2' in load_obj and load_obj['query2'] != "":
        query_value += '|' + load_obj['query2']

    asyncio.create_task(append_log(username, {'action': query, 'timestamp': timestamp, 'data_file': f"{timestamp}_{username}.json", 'value': query_value}))
    asyncio.create_task(preproccess_create_event_log(username, timestamp, query, my_obj, data))

    execution_time = time.time() - start_time
    print(f'Logging: {execution_time:.6f} secs')

    timings["T6_backendProcessingEnd"] = time.time()

    return {
        "data": new_data,
        "timing": timings
    }


@app.post("/updatePointer")
async def updatePointer(req: Request):
    '''
    Update the action pointer and history in Redis.
    
    Parameters:
    - req: The request object containing the parameters.
    '''
    request_args = await req.json()
    username = request_args.get('username')
    if not username:
        return {"error": "username required"}

    image_video_on_line = request_args.get('image_video_on_line', False)
    unique_video_frames = request_args.get('unique_video_frames', False)
    start = request_args.get('start', 0)

    image_video_on_line_new = request_args.get('image_video_on_line_new', False)
    unique_video_frames_new = request_args.get('unique_video_frames_new', False)

    # Redis keys
    keys = get_redis_keys(username)

    # Fetch current pointer
    pointer_raw = await redis_client.get(keys["action_pointer"])
    pointer = int(pointer_raw or 0)

    # Trim forward history if needed
    length = await redis_client.llen(keys["image_items"])
    if length > pointer + 1:
        for field in ["image_items", "limit_frames", "video_on_line", "scroll_position"]:
            await redis_client.ltrim(keys[field], 0, pointer)
        pointer += 1
        await redis_client.set(keys["action_pointer"], pointer)
    elif length > MAX_HISTORY:
        for field in ["image_items", "limit_frames", "video_on_line", "scroll_position"]:
            await redis_client.ltrim(keys[field], 1, -1)
        # pointer remains unchanged
    else:
        pointer += 1
        await redis_client.set(keys["action_pointer"], pointer)

    # Fetch previous item at pointer - 1
    item_raw = await redis_client.lindex(keys["image_items"], pointer - 1)
    item = orjson.loads(item_raw) if item_raw else {}

    # Append new items
    await redis_client.rpush(keys["image_items"], orjson.dumps(item))
    await redis_client.rpush(keys["limit_frames"], orjson.dumps(unique_video_frames_new))
    await redis_client.rpush(keys["video_on_line"], orjson.dumps(image_video_on_line_new))
    await redis_client.rpush(keys["scroll_position"], orjson.dumps(0))

    # Trim to max history
    for field in ["image_items", "limit_frames", "video_on_line", "scroll_position"]:
        await redis_client.ltrim(keys[field], -MAX_HISTORY, -1)

    # Overwrite the previous state with updated values
    if pointer > 0:
        await redis_client.lset(keys["limit_frames"], pointer - 1, orjson.dumps(unique_video_frames))
        await redis_client.lset(keys["video_on_line"], pointer - 1, orjson.dumps(image_video_on_line))
        await redis_client.lset(keys["scroll_position"], pointer - 1, orjson.dumps(start))

    return {"success": True}


@app.post("/bayes")
async def bayes(req: Request):
    '''
    Send request for the Bayesian update to data service and return the response.
    
    Parameters:
    - req: The request object containing the parameters.
    '''
    request_args = await req.json()

    timings = {
        "T0_frontendStart": request_args.get("frontendStartTime"),
        "T1_backendReceived": time.time(),
    }

    selected_images = request_args['selected_images'] if 'selected_images' in request_args else None
    username = request_args['username'] if 'username' in request_args else None
    k = request_args.get('k', 10000)
    dataset = request_args.get('dataset', '').upper()

    image_video_on_line = request_args['image_video_on_line'] if 'image_video_on_line' in request_args else False
    unique_video_frames = request_args['unique_video_frames'] if 'unique_video_frames' in request_args else False
    start = request_args['start'] if 'start' in request_args else 0

    if selected_images is None or username is None:
        raise HTTPException(status_code=400, detail="Missing required parameters.")

    # Redis keys
    prefix = f"user:{username}"
    image_items_key = f"{prefix}:image_items"
    action_pointer_key = f"{prefix}:action_pointer"

    # Get current pointer
    pointer_raw = await redis_client.get(action_pointer_key)
    if pointer_raw is None:
        logging.error(f"User {username} hasn't data from last query.")
        return "No images to compare. Please initialize them with a query!"

    pointer = int(pointer_raw)

    # Retrieve image item at current pointer
    item_raw = await redis_client.lindex(image_items_key, pointer)
    if item_raw is None:
        logging.error(f"No history at pointer {pointer} for user {username}.")
        return "No images to compare. Please initialize them with a query!"

    items = orjson.loads(item_raw)
    if not items or 'score' not in items[0]:
        return "No Score to compare images with. Please initialize them with a query!"

    ids = [ast.literal_eval(str(item['id'])) for item in items if 'id' in item]
    scores = [float(item['score']) for item in items if 'score' in item]

    max_rank = max([int(item['rank']) for item in items if item['id'] in selected_images]) + 5

    my_obj = {
        "selected_images": selected_images,
        "max_rank": max_rank,
        "scores": scores,
        "ids": ids,
        "k": k,
        "dataset": dataset,
    }

    try:
            connector = aiohttp.TCPConnector(limit=0, force_close=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post("http://vbs-backend-nginx-1:80/bayes", json=my_obj) as response:

                    if response.status != 200:
                        text = await response.text()
                        logging.error(f"Error from service: {text}")
                        raise HTTPException(status_code=502, detail="Bad response from service")

                    # Read full body safely (even if large)
                    body = await response.read()

                    try:
                        items = orjson.loads(body)
                    except Exception as e:
                        logging.error(f"Failed to parse service response: {e}")
                        logging.error(f"Raw response was: {body[:500]}")  # first 500 bytes
                        raise HTTPException(status_code=502, detail="Invalid response format from service")

    except Exception as e:
        logging.error(f"An error occurred while sending the request to the service: {str(e)}")
        raise HTTPException(status_code=400, detail=f"An error occurred while sending the request to the service: {str(e)}")

    timings["T5_backendReceiveJson"] = time.time()

    timings.update(items[-1])
    items = items[:-1]

    # Define Redis keys
    keys = get_redis_keys(username)

    # Get current action pointer
    pointer_raw = await redis_client.get(keys["action_pointer"])
    pointer = int(pointer_raw or 0)

    # Get current image_items length
    history_len = await redis_client.llen(keys["image_items"])

    # Trim forward history if needed
    if history_len > pointer + 1:
        for key in ["image_items", "limit_frames", "video_on_line", "scroll_position"]:
            await redis_client.ltrim(keys[key], 0, pointer)
        pointer += 1
        await redis_client.set(keys["action_pointer"], pointer)

    # Remove oldest entries if over 10
    elif history_len > 10:
        for key in ["image_items", "limit_frames", "video_on_line", "scroll_position"]:
            await redis_client.ltrim(key, 1, -1)
        # pointer stays the same
    else:
        pointer += 1
        await redis_client.set(keys["action_pointer"], pointer)

    # Append new state
    await redis_client.rpush(keys["image_items"], orjson.dumps(items))
    await redis_client.rpush(keys["limit_frames"], orjson.dumps(unique_video_frames))
    await redis_client.rpush(keys["video_on_line"], orjson.dumps(image_video_on_line))
    await redis_client.rpush(keys["scroll_position"], orjson.dumps(0))

    # Trim history to max 10
    for key in ["image_items", "limit_frames", "video_on_line", "scroll_position"]:
        await redis_client.ltrim(key, -10, -1)

    # Update previous state values (if not at the beginning)
    if pointer > 0:
        await redis_client.lset(keys["limit_frames"], pointer - 1, orjson.dumps(unique_video_frames))
        await redis_client.lset(keys["video_on_line"], pointer - 1, orjson.dumps(image_video_on_line))
        await redis_client.lset(keys["scroll_position"], pointer - 1, orjson.dumps(start))

    new_data = [{k: v for k, v in item.items() if k != "features"} for item in items[:MAX_DISPLAY]]

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    asyncio.create_task(append_log(username, {'action': 'bayes', 'timestamp': timestamp, 'data_file': f"{timestamp}_{username}.json"}))
    asyncio.create_task(preproccess_and_create_event_log(username, timestamp, {'timestamp': timestamp, 'events': [{'category': 'IMAGE', 'type': 'feedbackModel', 'value': 'framesId ' + " ".join(['_'.join(image) for image in selected_images])}], 'results': items}))

    timings["T6_backendProcessingEnd"] = time.time()

    return {
        "data": new_data,
        "timing": timings
    }


@app.post("/back")
async def back(req: Request):
    '''
    Go back to the previous query in the user's history.
    '''
    request_args = await req.json()
    username = request_args.get("username")
    if not username:
        return "Username is required."

    # Redis keys
    keys = get_redis_keys(username)

    pointer_raw = await redis_client.get(keys["action_pointer"])
    if pointer_raw is None:
        logging.error(f"User {username} hasn't data from last query.")
        return "No images to compare. Please initialize them with a query!"

    pointer = int(pointer_raw)
    if pointer == 0:
        logging.error(f"User {username} is already at the first query.")
        return "No previous query to go back to."

    pointer -= 1
    await redis_client.set(keys["action_pointer"], pointer)

    item_raw = await redis_client.lindex(keys["image_items"], pointer)
    items = orjson.loads(item_raw) if item_raw else []
    new_data = [{k: v for k, v in item.items() if k != "features"} for item in items[:MAX_DISPLAY]]

    limit_frames = orjson.loads(await redis_client.lindex(keys["limit_frames"], pointer) or b"[]")
    video_on_line = orjson.loads(await redis_client.lindex(keys["video_on_line"], pointer) or b"[]")
    scroll_position = orjson.loads(await redis_client.lindex(keys["scroll_position"], pointer) or b"0")

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    asyncio.create_task(append_log(username, {'action': 'back', 'timestamp': timestamp}))

    return {
        "data": new_data,
        "limit_frames": limit_frames,
        "video_on_line": video_on_line,
        "scroll_pos": scroll_position
    }


@app.post("/forward")
async def forward(req: Request):
    '''
    Go forward to the next query in the user's history.
    '''
    request_args = await req.json()
    username = request_args.get("username")
    if not username:
        return "Username is required."

    # Redis keys
    keys = get_redis_keys(username)

    pointer_raw = await redis_client.get(keys["action_pointer"])
    history_length = await redis_client.llen(keys["image_items"])
    if pointer_raw is None or history_length == 0:
        logging.error(f"User {username} hasn't data from last query.")
        return "No images to compare. Please initialize them with a query!"

    pointer = int(pointer_raw)
    if pointer >= history_length - 1:
        logging.error(f"User {username} is already at the last query.")
        return "No next query to go forward to."

    pointer += 1
    await redis_client.set(keys["action_pointer"], pointer)

    item_raw = await redis_client.lindex(keys["image_items"], pointer)
    items = orjson.loads(item_raw) if item_raw else []
    new_data = [{k: v for k, v in item.items() if k != "features"} for item in items[:MAX_DISPLAY]]

    limit_frames = orjson.loads(await redis_client.lindex(keys["limit_frames"], pointer) or b"[]")
    video_on_line = orjson.loads(await redis_client.lindex(keys["video_on_line"], pointer) or b"[]")
    scroll_position = orjson.loads(await redis_client.lindex(keys["scroll_position"], pointer) or b"0")

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    asyncio.create_task(append_log(username, {'action': 'forward', 'timestamp': timestamp}))

    return {
        "data": new_data,
        "limit_frames": limit_frames,
        "video_on_line": video_on_line,
        "scroll_pos": scroll_position
    }


@app.post("/get_filters")
async def get_filters(req: Request):
    '''
    Get filters for a specific dataset from the data service.
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
async def login(req: Request) -> JSONResponse:
    """Login a user and return an access token for DRES server.
    
    Args:
        req: The request object containing username and password.
        
    Returns:
        JSONResponse with access token.
        
    Raises:
        HTTPException: If authentication fails or parameters are missing.
    """
    request_args = await req.json()
    username = request_args.get('username')
    password = request_args.get('password')

    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing username or password.")

    user = users_db.get(username)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    return JSONResponse(content={"access_token": logins.get(username, "")})



## THE ORDER OF THESE ROUTES MATTERS... Do not place this first.
@app.get("/", response_class=FileResponse)
def main():
    return "public/index.html"
