# PraK - Video Retrieval System - Frontend

## Requirements: 
    - [Python 3.10+](https://www.python.org/downloads/)
    - [NodeJS](https://nodejs.org/en)
    - [Docker](https://www.docker.com/)

## Installation and Setup
1. Create Python virtual enviroment and install requirements.txt
   - when you restart your workspace you will need to activate it again, just run the second line
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
   > after that we activate it and install needed dependencies

2. Get all svelte packages and npm dependencies
```cmd
cd ./frontend
npm install --legacy-peer-deps
cd ../
```

3. Build svelte and run fastapi with uvicorn. The prepare statement builds the css from the material design theme
```cmd
cd ./frontend
npm run prepare
npm run build
```


Main Entry for webserver is the python main.py going into frontend/index.html and all components are created in frontend/src/App.svelte for the frontend


4. Main development route to work on the server / Backend is in the main directory, so not in /frontend using the uvicorn server. If you do changes in the frontend you need to rebuild with step 3. Then you can restart here.
```
cd ../
uvicorn main:app --reload
```


5. When developing in Svelte on the frontend, please use the dev server! Here the changes in the frontend are updated automatically. Be aware that here no backend functionality is available.
```cmd
npm run dev
```

6. Deployment: Building the project as a docker container (no development in it.) In the main directory execute:
```cmd
docker compose up --build
```

Then you can access the whole project at localhost:8000 or via the docker applicaton.


## Project Structure
- `main.py` - Python file containing the FastAPI server and the routes
- `frontend/src/` - Contains the svelte components
  - `App.svelte` - Main component of the frontend - contains functionality of the frontend
  - `Image.svelte` - Component for showing images
  - `ImageList.svelte` - Component for showing rows of images in the frontend
  - `VirtualListNew.svelte` - Component for the virtual list (handling scrolling and showing current visible part of image list)
  - `store.js` - Store of variables for the frontend
  - `app.css` - Main css file of the frontend
- `docker-compose.yml` - Docker compose file for building the project as a container