# Sentiment Analyzer

A small sentiment analysis app with a FastAPI backend, an Angular UI, and a scikit-learn Naive Bayes model.

The app accepts a text input and returns a stable sentiment code, display label, and model confidence when available.

## Features

- FastAPI endpoints for sentiment prediction and health checks
- Angular frontend served by the backend after build
- Streamlit UI for quick local testing
- CountVectorizer text preprocessing
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

Open `http://localhost:4200`. The dev server proxies `/predict`, `/health`, and `/docs` to FastAPI.

To run the Streamlit version:

```bash
streamlit run backend/ui_app.py
```

## API Example

Request:

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
curl http://127.0.0.1:8000/health
```

## Project Structure

```text
sentiment-analyzer-app/
├── backend/
│   ├── main.py
│   ├── model.py
│   ├── requirements.txt
│   ├── sentiment_model.pkl
│   ├── vectorizer.pkl
│   ├── tests/
│   └── static/
├── src/
│   ├── app/
│   ├── index.html
│   └── styles.css
├── setup_model.py
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

Set `ALLOWED_ORIGINS` to a comma-separated list of browser origins that are allowed to call the API, for example:

```bash
ALLOWED_ORIGINS=https://sentiment-analyzer-app-puua.onrender.com
```

## Tests

Run backend tests:

```bash
pytest backend/tests
```

Run frontend tests:

```bash
npm test
```
