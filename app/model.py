# model loading / prediction logic
import joblib
import os


def load_model():
    """Load the sentiment analysis model"""
    model_path = os.path.join(os.path.dirname(__file__), "sentiment_model.pkl")
    return joblib.load(model_path)


def load_vectorizer():
    """Load the text vectorizer"""
    vectorizer_path = os.path.join(os.path.dirname(__file__), "vectorizer.pkl")
    return joblib.load(vectorizer_path)


def predict_sentiment(text: str, model, vectorizer):
    """Predict sentiment for given text"""
    text_vector = vectorizer.transform([text])
    prediction = model.predict(text_vector)[0]
    return prediction
