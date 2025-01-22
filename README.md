# PraK - Video Retrieval
This project is a video retrieval system that allows users to search in video collections based on their content. The system communicates with a data service that provides videos, and images and computes the search results (text and similarity queries, etc.). The system is built with a frontend and backend that communicate with each other using RESTful APIs. The frontend is built with Svelte and the backend with FastAPI. The project is containerized with Docker for easy deployment.

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
   Create a Python virtual environment and install the required dependencies
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
   > The main entry for the web server is `main.py`. The frontend entry point is `frontend/index.html`, and all components are created in `frontend/src/App.svelte`.

### Development
To build and run the project as a Docker container, execute the following command in the main directory:
```cmd
docker compose up --build
```
> You can access the project at localhost:8000 or via the Docker application. If you are developing only the frontend it's necessary to comment out the network part in the `docker-compose.yml` file.

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

## Project Structure
The project is divided into several directories and files, each serving a specific purpose. Below is a description of the most important parts of the project structure:
- `frontend/`: Contains the whole Svelte frontend project.
  - `vite.config.js`: Configuration file for the Vite bundler. Contains the proxy settings for the backend.
  - `package.json`: Contains the frontend dependencies and scripts.
  - `src/`: Contains the Svelte components, assets, and code for the frontend.
    - `App.svelte`: Main component that contains the main layout and most of the logic for the frontend.
    - `store.js`: Svelte store for global state management. Contains the user data and login status that is shared between components.
    - `Images.svelte`: Component for displaying a single image in the list. Contains the image and its metadata. And sets functionality connected to the image like showing video, displaying metadata or images from the same video, etc.
    - `ImageList.svelte`: Component for displaying a list of images. Contains the list of images and the logic for fetching more images when the user scrolls to the bottom of the list.
    - `Login.svelte`: Component for user login. Contains the login form and the logic for sending the login request to the backend.
    - `VirtualListNew.svelte`: Component for handling a list of images as a scrollable list. Managing the lines of images and their loading connected to the scroll position.
- `main.py`: Main entry point for the FastAPI backend. Contains the API routes and the logic for handling the requests. The backend communicates with the data service to fetch the images and videos. It also handles user authentication and authorization and Bayes updates.
- `requirements.txt`: Contains the Python dependencies. These are installed in the Python virtual environment.
- `Dockerfile`: Contains the Docker build instructions for the backend.
- `docker-compose.yml`: Contains the Docker compose configuration for the project. It builds the frontend and backend, runs them in containers with the necessary environment variables, and connects them to the network that the data service is running on.
- `.env`: Contains the environment variables for the project. The secret key is used for JWT token generation, and the password and logins are used for user authentication.
