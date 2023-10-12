FROM  node:19 as build

RUN apt-get update || : && apt-get -y install python3-pip

ADD ./requirements.txt .

ADD ./main.py .

ADD ./frontend ./frontend

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .
 
WORKDIR /frontend

RUN npm install --force

RUN npm run build

WORKDIR /

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]

