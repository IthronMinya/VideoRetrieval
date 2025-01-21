# PraK - Video Retrieval
This project is a video retrieval system that allows users to search in video collection based on their content. The system communicates with a data service that provides videos, images and compute the search results (text and similarity queries, etc.). The system is built with a frontend and backend that communicate with each other using RESTful APIs. The frontend is built with Svelte and the backend with FastAPI. The project is containerized with Docker for easy deployment.

## Requirements: 
 - [Python 3.10+](https://www.python.org/downloads/)
 - [NodeJS](https://nodejs.org/en)
 - [Docker](https://www.docker.com/)

## Project setup instructions
Follow these steps to setup the project on your local machine:
1. Clone the Repository
   ```cmd
   git clone https://github.com/IthronMinya/VideoRetrieval.git
   ```

2. Set Up Python Virtual Environment
   Create a Python virtual enviroment and install the required dependencies
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
   > Note: You will need to activate the virtual environment each time you restart your workspace.
   
3. Create `.env` File 
   Create a `.env` file in the main directory and add the following content:
   ```env
   SECRET_KEY=your_secret_key
   VITE_SECRET_KEY=your_secret_key
   PASSWORD=your_password
   LOGINS=your_logins
   ```
   > The secret key is used for JWT token generation. You can generate one [here](https://randomkeygen.com/)

4. Install Svelte Packages and NPM Dependencies
   Navigate to the [frontend](./frontend/) directory and install the necessary packages
   ```cmd
   cd ./frontend
   npm install --legacy-peer-deps
   cd ../
   ```

5. Build Svelte and Run FastAPI
   Build the Svelte project and run the FastAPI server with Uvicorn. The `prepare` script builds the CSS from the Material Design theme.
   ```cmd
   cd ./frontend
   npm run prepare
   npm run build
   cd ../
   uvicorn main:app --reload
   ```
   > Main entry for the web server is `main.py`. The frontend entry point is `frontend/index.html`, and all components are created in `frontend/src/App.svelte`.

### Development
To build and run the project as a Docker container, execute the following command in the main directory:
```cmd
docker compose up --build
```
> You can access the project at localhost:8000 or via the Docker application.

#### Backend Development
For backend development, use the Uvicorn server in the main directory.

```cmd
uvicorn main:app --reload
```
> If you make changes to the frontend, rebuild it using step 5, then restart the backend server.

#### Frontend Development
For frontend development, use the Svelte dev server. This server updates changes in the frontend automatically. Note that backend functionality is not available in this mode.

```cmd
cd ./frontend
npm run dev
```
