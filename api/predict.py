from firebase_utils import get_trigram_suggestion
import logging

logger = logging.getLogger(__name__)

def predict_next_word(tokens):
    try:
        if len(tokens) >= 2:
            trigram_suggestion = get_trigram_suggestion(tokens[-2:])
            if trigram_suggestion:
                logger.debug(f"Using trigram suggestion: {trigram_suggestion}")
                return trigram_suggestion
        return "to"  # Default banking fallback
    except Exception as e:
        logger.error(f"Prediction logic error: {str(e)}")
        return "to"