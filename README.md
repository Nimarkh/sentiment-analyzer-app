# 🧠 Sentiment Analyzer App

_A simple AI-powered web API that detects the sentiment (Positive or Negative) of any given text._

---

## 🚀 Overview

This project is a minimal yet powerful **Sentiment Analysis Web API** built with **FastAPI** and a **Naive Bayes classifier** trained on sample text data.

It takes a text input and predicts whether the sentiment is **Positive 😀** or **Negative 😞**.

---

## 🧩 Features

✅ REST API built with FastAPI

✅ Pre-trained machine learning model (Naive Bayes)

✅ Text preprocessing using CountVectorizer

✅ Interactive Swagger UI for testing

✅ Easy to extend or deploy

---

## 🛠️ Tech Stack

| Component           | Technology    |
| ------------------- | ------------- |
| Backend             | FastAPI       |
| Machine Learning    | scikit-learn  |
| Language            | Python        |
| Data Handling       | Pandas, Numpy |
| Model Serialization | joblib        |

---

## 📦 Installation & Setup

### 1️⃣ Clone this repository

```bash
git clone https://github.com/<your-username>/sentiment-analyzer-app.git
cd sentiment-analyzer-app
```

### 2️⃣ Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate      # (Windows: venv\Scripts\activate)
```

### 3️⃣ Install dependencies

```bash
pip install -r app/requirements.txt
```

### 4️⃣ Train model (optional)

You can retrain or modify the model in:

`notebooks/data_preprocessing.ipynb`

### 5️⃣ Run the Application

**Option A: API Only**
```bash
cd app
uvicorn main:app --reload
```
Then open your browser at: http://127.0.0.1:8000/docs

**Option B: Full Web App (Recommended)**
```bash
cd app
streamlit run ui_app.py
```
Then open your browser at: http://localhost:8501

---

## 🌐 Live Demo

### API Endpoint
Try the API live at:

👉 **https://sentiment-analyzer-app-puua.onrender.com/docs**

Interactive Swagger UI for testing the API endpoints.

### Web Application
Experience the full web application with a beautiful UI:

👉 **Streamlit UI** (Run locally: `streamlit run app/ui_app.py`)

![App Demo](docs/demo.png)

---

## 🧠 Example

**Request:**

```json
{
  "text": "I really love this movie!"
}
```

**Response:**

```json
{
  "text": "I really love this movie!",
  "sentiment": "Positive 😀"
}
```

---

## 🧰 Folder Structure

```
sentiment-analyzer-app/
│
├── app/
│   ├── main.py              # FastAPI backend
│   ├── model.py             # model helpers
│   ├── ui_app.py            # Streamlit UI
│   ├── requirements.txt     # dependencies
│   ├── sentiment_model.pkl  # trained model
│   └── vectorizer.pkl       # text vectorizer
│
├── notebooks/
│   └── data_preprocessing.ipynb  # training notebook
│
├── docs/
│   └── demo.png            # app screenshot
│
├── README.md
└── .gitignore
```

---

## 🖥️ Demo Screenshot

Add a screenshot or GIF of your API in action here (e.g., Swagger UI)

Example:

---

## 📄 License

MIT License © 2025 Your Name

---

## 🌟 Support

If you like this project, give it a ⭐ on GitHub!

---

## 🚀 Deployment (Optional)

You can deploy your API online for free using services like:

### 🔹 Method 1: Render.com

The easiest way for FastAPI.

1. Go to render.com and login with GitHub
2. Select "New Web Service"
3. Choose your repository
4. Settings:
   - **Build Command**: `pip install -r app/requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5. Click Deploy ✅

After a few minutes, you'll get a link like:

`https://sentiment-analyzer-app-puua.onrender.com/docs`

✅ **Live deployment:** https://sentiment-analyzer-app-puua.onrender.com

---

## 📈 Future Improvements

After the initial version is up, you can add these features one by one:

| Idea                 | Description                                     |
| -------------------- | ----------------------------------------------- |
| 🧠 Upgrade Model     | Use transformers like BERT with HuggingFace     |
| 🌐 User Interface    | Build a simple frontend with Streamlit or React |
| 🧪 Automated Testing | Add tests with pytest and GitHub Actions        |
| 🐳 Dockerize         | Create Dockerfile for easy project deployment   |
| 📊 Monitoring        | Log API logs with logging and ELK stack         |
