import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase with error handling
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
    db = None  # Fallback to None, handled in functions

async def store_classified_data(user_id, private_data, public_tokens):
    try:
        if not db:
            logger.warning("Firebase not initialized, skipping storage")
            return

        # Store private data (unencrypted)
        if private_data:
            user_ref = db.collection("private_users").document(user_id)
            user_ref.set(private_data, merge=True)
            logger.debug(f"Stored private data for user {user_id}: {private_data}")

        # Store public trigrams
        if len(public_tokens) >= 3:
            batch = db.batch()
            for i in range(len(public_tokens) - 2):
                key = f"{public_tokens[i]}_{public_tokens[i+1]}"
                trigram_ref = db.collection("public_trigrams").document(key)
                batch.set(trigram_ref, {
                    "first": public_tokens[i],
                    "second": public_tokens[i+1],
                    "third": public_tokens[i+2],
                    "count": firestore.Increment(1)
                }, merge=True)
            batch.commit()
            logger.info(f"Stored public trigrams for tokens: {public_tokens[:5]}...")
    except Exception as e:
        logger.error(f"Firebase store error: {str(e)}")

def get_trigram_suggestion(last_two_words):
    try:
        if not db:
            logger.warning("Firebase not initialized, returning None")
            return None
        key = f"{last_two_words[0]}_{last_two_words[1]}"
        trigram = db.collection("public_trigrams").document(key).get()
        if trigram.exists:
            return trigram.to_dict()["third"]
        return None
    except Exception as e:
        logger.error(f"Firebase lookup error: {str(e)}")
        return None