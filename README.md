# Sentiment Analyzer

A small sentiment analysis app with a FastAPI backend, an Angular UI, and a scikit-learn Naive Bayes model.

The app accepts a text input and returns a stable sentiment code, display label, and model confidence when available.

## Features

- FastAPI endpoints for sentiment prediction and health checks
- Versioned API under `/api/v1`
- Structured API errors and lightweight rate limiting
- Optional API key protection with `x-api-key`
- Model metadata and analytics endpoints
- Angular frontend served by the backend after build
- Frontend health indicator, confidence bar, dark mode, batch compare, reset, export, and recent analysis history
- Streamlit UI for quick local testing
- TfidfVectorizer text preprocessing
- Serialized model and vectorizer with `joblib`

## Tech Stack

| Part | Technology |
| --- | --- |
| Backend | FastAPI |
| Frontend | Angular, Streamlit |
| Model | scikit-learn |
| Language | Python, TypeScript |
| Serialization | joblib |

## Setup

Create a virtual environment and install the Python dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
```

Install the frontend dependencies:

```bash
npm install
```

## Running Locally

Train the sample model:

```bash
python setup_model.py
```

Build the Angular UI into `backend/static`:

```bash
npm run build
```

Run the API and serve the built frontend:

```bash
cd backend
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000`.

For frontend development, run Angular separately:

```bash
npm start
```

Open `http://localhost:4200`. The dev server proxies `/api`, `/predict`, `/health`, and `/docs` to FastAPI.

To run the Streamlit version:

```bash
streamlit run backend/ui_app.py
```

## API Example

Request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"I really love this movie!"}'
```

```json
{
  "text": "I really love this movie!"
}
```

Response:

```json
{
  "text": "I really love this movie!",
  "sentiment": "positive",
  "label": "Positive",
  "confidence": 0.91,
  "probabilities": {
    "positive": 0.91,
    "negative": 0.09
  }
}
```

Health check:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Model metadata:

```bash
curl http://127.0.0.1:8000/api/v1/model-info
```

Batch prediction:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"texts":["I love this app","This was frustrating"]}'
```

Analytics summary:

```bash
curl http://127.0.0.1:8000/api/v1/analytics
```

Error responses use a stable shape:

```json
{
  "error": {
    "code": "MODEL_NOT_READY",
    "message": "Model files not found. Train the model first with setup_model.py."
  }
}
```

## Project Structure

```text
sentiment-analyzer-app/
├── backend/
│   ├── main.py
│   ├── model.py
│   ├── settings.py
│   ├── requirements.txt
│   ├── sentiment_model.pkl
│   ├── vectorizer.pkl
│   ├── model_metadata.json
│   ├── tests/
│   └── static/
├── src/
│   ├── app/
│   ├── index.html
│   └── styles.css
├── setup_model.py
├── Dockerfile
├── angular.json
├── package.json
└── README.md
```

## Model

`setup_model.py` trains a small sample model with a reproducible split and saves the output files used by the backend.

```bash
python setup_model.py
```

## Deployment

The backend can be deployed as a standard FastAPI app. Make sure `backend/sentiment_model.pkl`, `backend/vectorizer.pkl`, and the Angular build files are present before deploying.

Useful environment variables:

- `ALLOWED_ORIGINS`: comma-separated browser origins that can call the API.
- `MAX_TEXT_LENGTH`: maximum request text length. Default: `5000`.
- `RATE_LIMIT_REQUESTS`: requests allowed per client window. Default: `30`.
- `RATE_LIMIT_WINDOW_SECONDS`: rate limit window size. Default: `60`.
- `MODEL_PATH` and `VECTORIZER_PATH`: override model artifact locations.
- `MODEL_METADATA_PATH`: override model metadata location.
- `API_KEY`: optional key required through the `x-api-key` header when set.
- `ANALYTICS_DB_PATH`: SQLite database path for local analytics.

Example:

```bash
ALLOWED_ORIGINS=https://sentiment-analyzer-app-puua.onrender.com
```

Docker:

```bash
docker build -t sentiment-analyzer-app .
docker run --rm -p 8000:8000 sentiment-analyzer-app
```

CI is configured in `.github/workflows/ci.yml` to run backend tests, frontend tests, and the Angular build on pushes and pull requests.

## Tests

Run backend tests:

```bash
pytest backend/tests
```

Run Python lint:

```bash
ruff check backend setup_model.py
```

Run frontend tests:

```bash
npm test
```

Format frontend and docs:

```bash
npm run format
```
