"""
Helper script to train and save the model
Run this from the project root directory
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import joblib
import os

# Simple training data
data = {
    'text': [
        'I love this movie',
        'This is amazing!',
        'I hate this',
        'This was terrible',
        'I enjoy watching this',
        'This is bad',
        'What a great day',
        'Worst experience ever'
    ],
    'label': [1, 1, 0, 0, 1, 0, 1, 0]  # 1=positive, 0=negative
}

df = pd.DataFrame(data)

# Split data
X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.25)

# Convert text to vectors
vectorizer = CountVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train model
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# Evaluate
preds = model.predict(X_test_vec)
print(f"Accuracy: {accuracy_score(y_test, preds)}")

# Save model and vectorizer to app folder
app_dir = 'app'
os.makedirs(app_dir, exist_ok=True)

model_path = os.path.join(app_dir, 'sentiment_model.pkl')
vectorizer_path = os.path.join(app_dir, 'vectorizer.pkl')

joblib.dump(model, model_path)
joblib.dump(vectorizer, vectorizer_path)

print(f"✅ Model saved to: {model_path}")
print(f"✅ Vectorizer saved to: {vectorizer_path}")

