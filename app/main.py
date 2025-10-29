from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import os

app = FastAPI(title="Sentiment Analyzer API")

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


@app.get("/")
def home():
    return {"message": "Welcome to Sentiment Analyzer API"}


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
