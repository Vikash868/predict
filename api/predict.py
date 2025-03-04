from .firebase_utils import get_trigram_suggestion
import logging

logger = logging.getLogger(__name__)

def predict_next_words(tokens, max_words=3):
    try:
        if len(tokens) < 1:
            return []  # No prediction for empty input
        
        predicted = []
        current_tokens = tokens[-2:] if len(tokens) >= 2 else tokens[:1]
        
        for _ in range(max_words):
            suggestion = get_trigram_suggestion(current_tokens)
            if not suggestion:
                logger.debug("No further trigram suggestion, stopping")
                break
            predicted.append(suggestion)
            current_tokens = current_tokens[1:] + [suggestion]
            
        if not predicted:
            logger.debug("No trigram suggestions available")
            return []  # Empty array if no prediction
            
        logger.debug(f"Predicted words: {predicted}")
        return predicted
    except Exception as e:
        logger.error(f"Prediction logic error: {str(e)}")
        return []
