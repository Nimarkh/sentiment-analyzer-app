from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os

app = FastAPI(title="Sentiment Analyzer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Set to False when using *
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Load model and vectorizer
model_path = os.path.join(os.path.dirname(__file__), "sentiment_model.pkl")
vectorizer_path = os.path.join(os.path.dirname(__file__), "vectorizer.pkl")

# Check if model files exist before loading
if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
    model = None
    vectorizer = None
else:
    try:
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
    except Exception as e:
        model = None
        vectorizer = None
        print(f"Error loading model: {e}")


class InputText(BaseModel):
    text: str


@app.post("/predict")
def predict_sentiment(data: InputText):
    if model is None or vectorizer is None:
        raise HTTPException(
            status_code=503, 
            detail="Model files not found. Please train the model first using the notebook."
        )
    text_vector = vectorizer.transform([data.text])
    prediction = model.predict(text_vector)[0]
    sentiment = "Positive 😀" if prediction == 1 else "Negative 😞"
    return {"text": data.text, "sentiment": sentiment}

# Serve Angular UI index.html
@app.get("/")
async def serve_index():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Sentiment Analyzer API</h1><p><a href='/docs'>API Docs</a></p>")

# Mount static files for Angular UI (JS, CSS, etc.) - must be last
app.mount("/", StaticFiles(directory="static", html=True), name="static")
