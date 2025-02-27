import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from predict import predict_next_word
from firebase_utils import store_classified_data
from classify import classify_prompt
import asyncio

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Banking Prediction API", description="Text prediction and classified storage for banking")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class PromptInput(BaseModel):
    prompt: str
    user_id: str = "anonymous"  # Default for testing, required for private data

@app.post("/predict")
async def predict(input: PromptInput):
    try:
        if not input.prompt.strip():
            logger.error("Empty prompt received for prediction")
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        tokens = input.prompt.lower().split()
        if len(tokens) < 2:
            logger.warning(f"Prompt too short: {input.prompt}")
            raise HTTPException(status_code=400, detail="Prompt must have at least 2 words")
        
        next_word = predict_next_word(tokens)
        logger.info(f"Predicted next word for '{input.prompt}': {next_word}")
        return {"next_word": next_word}
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/store")
async def store(input: PromptInput):
    try:
        if not input.prompt.strip():
            logger.error("Empty prompt received for storage")
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        private_data, public_tokens = classify_prompt(input.prompt)
        asyncio.create_task(store_classified_data(input.user_id, private_data, public_tokens))
        logger.info(f"Queued storage for prompt: {input.prompt} (user: {input.user_id})")
        return {"status": "stored"}
    except Exception as e:
        logger.error(f"Storage error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Storage failed: {str(e)}")