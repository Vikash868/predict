# Tokenization Server

A Vercel-hosted API for tokenizing text and storing tokens in Firebase.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set `FIREBASE_CREDENTIALS` environment variable with your Firebase service account JSON.
3. Run locally: `uvicorn api.main:app --reload`
4. Deploy to Vercel: `vercel --prod`

## Endpoint
- **POST /tokenize**: Tokenizes input text and stores it in Firebase.
  - Request: `{"text": "Hello world", "user_name": "Alice"}`
  - Response: `{"tokens": ["hello", "world"], "user_name": "Alice"}`
