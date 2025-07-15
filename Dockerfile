# Multi-stage Dockerfile
# Stage 1: Build container
# Use the official Node.js 19 image as the build environment
FROM  node:19 as build

# Copy the frontend code into the container
COPY ./frontend ./frontend

# Set the working directory for the build stage
WORKDIR /frontend

# Install Node.js dependencies and build the frontend
RUN npm install --force && npm run build


# Stage 2: Production container
# Use the official Python 3.9 slim image as the base image for the production container
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Create and set the working directory in the container
WORKDIR /app

# Copy the static frontend files from the build container
COPY --from=build /public ./public

# Copy the requirements.txt and main.py into the production container
COPY ./requirements.txt ./requirements.txt
COPY ./main.py ./main.py

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

# Start the FastAPI application when the container is run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"] 
