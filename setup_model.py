import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

DATA = {
    "text": [
        "I love this movie",
        "This is amazing",
        "This is good",
        "This is very good",
        "I had a good experience",
        "The movie was good and enjoyable",
        "The service was good and fast",
        "I feel happy",
        "This made me happy",
        "The product is excellent",
        "Excellent work from the team",
        "The food was excellent",
        "What a great day",
        "This is a great product",
        "Great service and friendly staff",
        "The app is useful and easy to use",
        "Everything was smooth and pleasant",
        "I would recommend this to everyone",
        "The team did a fantastic job",
        "I enjoy watching this",
        "I hate this",
        "This was terrible",
        "This is bad",
        "This is very bad",
        "I had a bad experience",
        "The movie was bad and boring",
        "The service was bad and slow",
        "I feel disappointed",
        "This made me angry",
        "The product is awful",
        "Awful work from the team",
        "The food was awful",
        "What a terrible day",
        "This is a terrible product",
        "Terrible service and rude staff",
        "The app is confusing and useless",
        "Everything was frustrating and slow",
        "I would never recommend this",
        "The team did a poor job",
        "Worst experience ever",
        "The interface feels polished and reliable",
        "The update improved everything",
        "Support answered quickly and kindly",
        "The result was better than expected",
        "The checkout process was painless",
        "The interface feels broken and unreliable",
        "The update made everything worse",
        "Support ignored my request",
        "The result was worse than expected",
        "The checkout process was painful",
    ],
    "label": [
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        1, 1, 1, 1, 1,
        0, 0, 0, 0, 0,
    ],
}


def train() -> None:
    df = pd.DataFrame(DATA)
    x_train, x_test, y_train, y_test = train_test_split(
        df["text"],
        df["label"],
        test_size=0.25,
        random_state=10,
        stratify=df["label"],
    )

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
    x_train_vec = vectorizer.fit_transform(x_train)
    x_test_vec = vectorizer.transform(x_test)

    model = LogisticRegression(max_iter=1000, random_state=10)
    model.fit(x_train_vec, y_train)

    predictions = model.predict(x_test_vec)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(
        y_test,
        predictions,
        target_names=["negative", "positive"],
        output_dict=True,
        zero_division=0,
    )

    backend_dir = Path(__file__).resolve().parent / "backend"
    backend_dir.mkdir(exist_ok=True)

    model_path = backend_dir / "sentiment_model.pkl"
    vectorizer_path = backend_dir / "vectorizer.pkl"
    metadata_path = backend_dir / "model_metadata.json"

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    metadata = {
        "model_type": "LogisticRegression",
        "vectorizer": "TfidfVectorizer",
        "labels": {"0": "negative", "1": "positive"},
        "trained_at": datetime.now(UTC).isoformat(),
        "dataset_size": len(df),
        "train_size": len(x_train),
        "test_size": len(x_test),
        "accuracy": accuracy,
        "classification_report": report,
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Accuracy: {accuracy}")
    print(f"Model saved to: {model_path}")
    print(f"Vectorizer saved to: {vectorizer_path}")
    print(f"Metadata saved to: {metadata_path}")


if __name__ == "__main__":
    train()

