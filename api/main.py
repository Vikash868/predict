import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .predict import predict_next_words
from .firebase_utils import store_prompt_data
import asyncio
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Banking Prediction API", description="Text prediction and storage for banking")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class PromptInput(BaseModel):
    prompt: str

@app.get("/")
async def root():
    try:
        message = {
            "status": "OK",
            "message": "Welcome to the Banking Prediction API!",
            "endpoints": {
                "/predict": "POST - Predict the next words for a given prompt",
                "/store": "POST - Store a prompt in Firebase"
            },
            "firebase_configured": "FIREBASE_CREDENTIALS" in os.environ
        }
        logger.info("Root endpoint accessed")
        return message
    except Exception as e:
        logger.error(f"Root endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/predict")
async def predict(input: PromptInput):
    try:
        if not input.prompt.strip():
            logger.error("Empty prompt received for prediction")
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        tokens = input.prompt.lower().split()
        if len(tokens) < 1:
            logger.warning(f"Prompt too short: {input.prompt}")
            raise HTTPException(status_code=400, detail="Prompt must have at least 1 word")
        
        next_words = predict_next_words(tokens)
        logger.info(f"Predicted next words for '{input.prompt}': {next_words}")
        return {"next_words": next_words}
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/store")
async def store(input: PromptInput):
    try:
        if not input.prompt.strip():
            logger.error("Empty prompt received for storage")
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        asyncio.create_task(store_prompt_data(input.prompt))
        logger.info(f"Queued storage for prompt: {input.prompt}")
        return {"status": "stored"}
    except Exception as e:
        logger.error(f"Storage error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")