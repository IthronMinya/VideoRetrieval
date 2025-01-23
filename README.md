# PraK - Video Retrieval
PraK is a video retrieval system designed to allows users to search in video collections based on their content. This part of system is composed of a frontend and backend that communicate seamlessly using RESTful APIs. The frontend, built with Svelte, provides an intuitive user interface for performing various types of searches, including text, image, metadata, and temporal queries. Additionally, the frontend allows users to view the search results, visualize the search results, and provide feedback to improve the search results using Bayesian relevance feedback. The backend, developed with FastAPI, handles the communication with the data service, performs additional computations, and manages user authentication and session tracking. 

The data service, which is a another component of the PraK tool, is responsible for providing videos, images, and computing search results based on for example text and similarity queries. This component is hosted in a separate repository, which can be found [here](https://github.com/zuzavop/vbs-backend/tree/lsc2024).

The entire project is containerized using Docker, ensuring easy deployment and scalability. The frontend and backend are connected to the data service using a network, allowing them to communicate seamlessly. The project is designed to be easily extendable and customizable, allowing for the addition of new features and improvements.

The current version of the PraK tool is avvailable [here](http://acheron.ms.mff.cuni.cz:42033/).

## Functionality
### Backend
The backend provides the following features:
- **User Authentication**: Users can log in to the system using their credentials. The system supports multiple users for session tracking and keeping track of history. The system uses JWT tokens for authentication and authorization.
- **Bayesian Relevance Feedback**: Users can provide feedback on the search results using Bayesian relevance feedback. The system uses this feedback to improve the search results.
- **Session Logging**: The system tracks user sessions and logs user interactions to improve the search results, which can be used for further analysis and improvements. The logs are stored as JSON files and are stored in the `user_data` directory. In this version of tool only the search queries, bayes update and history movements are logged.
- **Data Service Communication**: The backend communicates with the data service to retrieve search results. The data service is responsible for providing the necessary data for the search operations. After the data service returns the search results, the backend processes the results and send only the necessary data (the feature vectors and scores are not send) to the frontend.
- **History**: The system keeps track of the user's search history and provides access to previous searches and results, allowing users to revisit previous searches and results.

### Frontend
The frontend is divided into two main parts: the search interface and the search results. The search interface or more precisely search bar allows users to perform various types of searches, including text, metadata, and temporal queries. And allows users to specify current used visualization or set current user. The search results display the search results in a user-friendly manner, allowing users to view the results, visualize the results, and provide feedback using Bayesian relevance feedback. The images are displayed in a scrollable list, and the user can view the images in full size, view the metadata, and view images from the same video. The frontend also provides a login interface for user authentication.

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
> You can access the project at localhost:8000 or via the Docker application. If you are developing only the frontend it's necessary to comment out the network part in the `docker-compose.yml` file. In the case that the data service is running on the same machine and you want to connect the data service and the backend using the docker network, you need to first create the network with the following command:
> ```cmd
> docker network create -d bridge vbs-backend_default
> ```
> Then you can run the project with the `docker compose up --build` command.

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
- `frontend/`: Contains the whole Svelte frontend project with all the components and assets.
  - `vite.config.js`: Configuration file for the Vite bundler. Contains the proxy settings for the backend. Defines the build output directory and the base URL for the frontend.
  - `package.json`: Contains the frontend dependencies and scripts for building and running the frontend.
  - `src/`: Contains the Svelte components, assets, and code for the frontend. The most important files are:
    - `App.svelte`: Main component that contains the [main layout](https://github.com/IthronMinya/VideoRetrieval/blob/lsc2024/frontend/src/App.svelte#L1393), [styles](https://github.com/IthronMinya/VideoRetrieval/blob/lsc2024/frontend/src/App.svelte#L1636) and most of the logic for the frontend. It calls the other components and manages the global state. The main functionality is [sending requests](https://github.com/IthronMinya/VideoRetrieval/blob/lsc2024/frontend/src/App.svelte#L654) to the backend, [communicating with the dres server](https://github.com/IthronMinya/VideoRetrieval/blob/lsc2024/frontend/src/App.svelte#L142) (server used in the competitions for handling submissions), [visualizations](https://github.com/IthronMinya/VideoRetrieval/blob/lsc2024/frontend/src/App.svelte#L369) and overall event handling.
    - `store.js`: Svelte store for global state management. Contains the user data and login status that is shared between components.
    - `Images.svelte`: Component for displaying a single image in the list. Contains the image and its metadata and sets functionality connected to the image like showing video, displaying metadata or images from the same video, etc.
    - `ImageList.svelte`: Component for displaying a list of images. Contains the images that suppost to be on one line. This component is used more like a container for the images.
    - `VirtualListNew.svelte`: Component for handling a list of images as a scrollable list. Managing the lines of images and their loading connected to the scroll position.
    - `Login.svelte`: Component for user login. Contains the login form and the logic for sending the login request to the backend.
  
- `main.py`: Main entry point for the FastAPI backend. Contains the API routes and the logic for handling the requests. The backend [communicates with the data service](https://github.com/IthronMinya/VideoRetrieval/blob/lsc2024/main.py#L347) to fetch the images. It also handles user authentication and authorization, [Bayesian relevance feedback](https://github.com/IthronMinya/VideoRetrieval/blob/lsc2024/main.py#L418) and saving logs that are frequently send from the frontend.
- `requirements.txt`: Contains the Python dependencies that are required for the backend.
- `Dockerfile`: Contains the Docker build instructions for the backend. It installs the Python dependencies and sets the entry point for the FastAPI server.
- `docker-compose.yml`: Contains the Docker compose configuration for the project. It builds the frontend and backend, runs them in containers with the necessary environment variables, and connects them to the network that the data service is running on in case that both containers are running on the same machine.
- `.env`: Contains the environment variables for the project. The secret key is used for JWT token generation, and the password and logins are used for user authentication.
