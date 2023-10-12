import mimetypes
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/json', '.mjs')
mimetypes.add_type('text/css', '.css')

import uvicorn
import sys

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import random

import requests

import open_clip
import torch

import numpy as np
import numpy.typing as npt
from typing import List

from threading import Lock

from PIL import Image

class ScoreManager:
    def __init__(self, length):
        self.scores = np.zeros(length, dtype=np.float64)
        self.lock = Lock()

    def from_array(self, scores: npt.ArrayLike):
        self.scores = scores
        self.lock = Lock()

    def change_score(self, id: int, score: np.float64):
        with self.lock:
            self.scores[id] = score

    def normalize_scores(self):
        with self.lock:
            if np.max(self.scores) != 0.0:
                self.scores /= np.max(self.scores)

    def get_scores(self) -> List[np.float64]:
        with self.lock:
            return list(self.scores)
        
    def get_score(self, id: int) -> np.float64:
        with self.lock:
            return self.scores[id]

app = FastAPI()

# TODO initialize with real length of score vector
score_manager = ScoreManager(5)

model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')

tokenizer = open_clip.get_tokenizer('ViT-B-32')

# TODO load image feature vectors from server
image_feature_vectors = np.zeros((5, 512), dtype=np.float64)

app.mount("/assets", StaticFiles(directory="public/assets"), name="static")

@app.get("/", response_class=FileResponse)
def main():
    return "public/index.html"

#if __name__ == "__main__":
#    uvicorn.run("main:app", port=8002, reload=True)

def cosine_sim(f1, f2):

    dot_products = np.dot(f1, f2)
    
    return dot_products

@app.get("/rand")
async def hello():
   return random.randint(0, 100)

@app.get("/search_clip_text")
async def search_clip_text(text: str):

    text = tokenizer([text])

    with torch.no_grad():
        text_features = model.encode_text(text)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        text_features = text_features[0]

    score_manager.from_array(cosine_sim(text_features, image_feature_vectors.T).astype(np.float64)) 

    return score_manager.get_scores()

@app.get("/search_clip_image")
async def search_clip_image(image_id: int):
    
    print(image_id)

    # TODO get full size image from server
    img = Image.new('RGB', (512, 512))

    img = preprocess(img).unsqueeze(0)

    with torch.no_grad():
        image_features = model.encode_image(img)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        image_features = image_features[0]

    score_manager.from_array(cosine_sim(image_features, image_feature_vectors.T).astype(np.float64))

    return score_manager.get_scores()

@app.get("/send_results")
async def send_result(image_id: int):

    my_obj = {'team': "VBS", 'item': image_id}

    print(image_id)

    x = requests.get(url="https://siret.ms.mff.cuni.cz/lokoc/VBSEval/EndPoint.php", params=my_obj, verify=False)

    print(x.text)

@app.post("/bayes_update")
async def bayes_update(selected_ids: List[int], top_display: List[int]):

    negative_examples = image_feature_vectors[[item for item in top_display if item not in selected_ids]]
    positive_examples = image_feature_vectors[selected_ids]

    alpha = 0.1

    # compute bayes update
    for i, feature_vector in enumerate(image_feature_vectors):

        PF = np.sum(np.exp(- (1 - cosine_sim(feature_vector, positive_examples.T)) / alpha))
        NF = np.sum(np.exp(- (1 - cosine_sim(feature_vector, negative_examples.T)) / alpha))

        score_manager.change_score(i, score_manager.get_score(i) * PF / NF)

    score_manager.normalize_scores()

    print(score_manager.get_scores())

    return score_manager.get_scores()