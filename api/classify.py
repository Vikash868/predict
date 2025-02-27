import re
import logging

logger = logging.getLogger(__name__)

def classify_prompt(prompt):
    try:
        tokens = prompt.lower().split()
        private_data = {}
        public_tokens = tokens.copy()

        # Identify sensitive data (basic regex for names and numbers)
        name_pattern = r"^[a-z]+ [a-z]+$"  # e.g., "John Doe"
        number_pattern = r"^\d{6,}$"       # e.g., "1234567890"

        for i, token in enumerate(tokens):
            if re.match(name_pattern, " ".join(tokens[i:i+2]) if i+1 < len(tokens) else ""):
                name = " ".join(tokens[i:i+2])
                private_data["name"] = name
                public_tokens[i:i+2] = ["[NAME]"]  # Replace in public data
            elif re.match(number_pattern, token):
                private_data["number"] = token
                public_tokens[i] = "[NUMBER]"

        logger.debug(f"Classified - Private: {private_data}, Public: {public_tokens}")
        return private_data, public_tokens
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        return {}, tokens  # Default to all public on error