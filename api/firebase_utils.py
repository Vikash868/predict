import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    if "FIREBASE_CREDENTIALS" not in os.environ:
        logger.error("FIREBASE_CREDENTIALS environment variable not set")
        raise ValueError("FIREBASE_CREDENTIALS not set")
    cred = credentials.Certificate(json.loads(os.getenv("FIREBASE_CREDENTIALS")))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    logger.info("Firebase initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {str(e)}")
    db = None

async def store_prompt_data(prompt):
    try:
        if not db:
            logger.warning("Firebase not initialized, skipping storage")
            return

        prompt_id = datetime.now().isoformat().replace(":", "-")
        prompt_ref = db.collection("prompts").document(prompt_id)
        prompt_ref.set({
            "prompt": prompt,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        logger.info(f"Stored prompt: {prompt}")

        tokens = prompt.lower().split()
        if len(tokens) >= 3:
            batch = db.batch()
            for i in range(len(tokens) - 2):
                key = f"{tokens[i]}_{tokens[i+1]}"
                trigram_ref = db.collection("prompts_trigrams").document(key)
                batch.set(trigram_ref, {
                    "first": tokens[i],
                    "second": tokens[i+1],
                    "third": tokens[i+2],
                    "count": firestore.Increment(1)
                }, merge=True)
            batch.commit()
            logger.info(f"Stored trigrams for prompt: {prompt[:50]}...")
    except Exception as e:
        logger.error(f"Firebase store error: {str(e)}")

def get_trigram_suggestion(last_two_words):
    try:
        if not db:
            logger.warning("Firebase not initialized, returning None")
            return None
        key = f"{last_two_words[0]}_{last_two_words[1]}"
        trigram = db.collection("prompts_trigrams").document(key).get()
        if trigram.exists:
            return trigram.to_dict()["third"]
        return None
    except Exception as e:
        logger.error(f"Firebase lookup error: {str(e)}")
        return None