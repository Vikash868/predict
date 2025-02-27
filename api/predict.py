import torch
from transformers import DistilBertTokenizer, DistilBertForMaskedLM
from firebase_utils import get_trigram_suggestion
import logging

logger = logging.getLogger(__name__)

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = DistilBertForMaskedLM.from_pretrained("distilbert-base-uncased")
model.eval()

def predict_next_word(tokens):
    try:
        if len(tokens) >= 2:
            trigram_suggestion = get_trigram_suggestion(tokens[-2:])
            if trigram_suggestion:
                logger.debug(f"Using trigram suggestion: {trigram_suggestion}")
                return trigram_suggestion

        prompt = " ".join(tokens) + " [MASK]"
        inputs = tokenizer(prompt, return_tensors="pt")
        mask_idx = inputs["input_ids"][0].tolist().index(tokenizer.mask_token_id)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits[0, mask_idx]
            predicted_token_id = torch.argmax(logits).item()
            next_word = tokenizer.decode(predicted_token_id)
            logger.debug(f"DistilBERT prediction: {next_word}")
            return next_word
    except Exception as e:
        logger.error(f"Prediction logic error: {str(e)}")
        return "to"  # Banking-specific fallback