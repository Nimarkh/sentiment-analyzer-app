from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import joblib

data = {
    'text': [
        'I love this movie',
        'This is amazing!',
        'This is good',
        'This is very good',
        'I had a good experience',
        'The movie was good and enjoyable',
        'The service was good and fast',
        'I feel happy',
        'This made me happy',
        'The product is excellent',
        'Excellent work from the team',
        'The food was excellent',
        'What a great day',
        'This is a great product',
        'Great service and friendly staff',
        'The app is useful and easy to use',
        'Everything was smooth and pleasant',
        'I would recommend this to everyone',
        'The team did a fantastic job',
        'I enjoy watching this',
        'I hate this',
        'This was terrible',
        'This is bad',
        'This is very bad',
        'I had a bad experience',
        'The movie was bad and boring',
        'The service was bad and slow',
        'I feel disappointed',
        'This made me angry',
        'The product is awful',
        'Awful work from the team',
        'The food was awful',
        'What a terrible day',
        'This is a terrible product',
        'Terrible service and rude staff',
        'The app is confusing and useless',
        'Everything was frustrating and slow',
        'I would never recommend this',
        'The team did a poor job',
        'Worst experience ever'
    ],
    'label': [
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ]
}
        'This is bad',
        'What a great day',
        'Worst experience ever',
        'The service was excellent',
        'I am very happy with this',
        'This product works perfectly',
        'The food tasted wonderful',
        'I would recommend this to everyone',
        'The team did a fantastic job',
        'This made my day better',
        'Everything was smooth and pleasant',
        'The app is useful and easy to use',
        'I feel disappointed',
        'The service was awful',
        'This product broke immediately',
        'The food tasted horrible',
        'I would never recommend this',
        'The team did a poor job',
        'This ruined my day',
        'Everything was frustrating and slow',
        'The app is confusing and useless'
    ],
    'label': [
        1, 1, 0, 0, 1, 0, 1, 0,
        1, 1, 1, 1, 1, 1, 1, 1, 1,
        0, 0, 0, 0, 0, 0, 0, 0, 0,
    ]
}

df = pd.DataFrame(data)

X_train, X_test, y_train, y_test = train_test_split(
    df['text'],
    df['label'],
    test_size=0.25,
    random_state=42,
    stratify=df['label'],
)

vectorizer = CountVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

model = MultinomialNB()
model.fit(X_train_vec, y_train)

preds = model.predict(X_test_vec)
print(f"Accuracy: {accuracy_score(y_test, preds)}")

backend_dir = Path(__file__).resolve().parent / 'backend'
backend_dir.mkdir(exist_ok=True)

model_path = backend_dir / 'sentiment_model.pkl'
vectorizer_path = backend_dir / 'vectorizer.pkl'

joblib.dump(model, model_path)
joblib.dump(vectorizer, vectorizer_path)

print(f"Model saved to: {model_path}")
print(f"Vectorizer saved to: {vectorizer_path}")

