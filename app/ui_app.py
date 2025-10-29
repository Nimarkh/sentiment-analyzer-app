import streamlit as st
import joblib
import os

# Load model and vectorizer
model_path = os.path.join(os.path.dirname(__file__), "sentiment_model.pkl")
vectorizer_path = os.path.join(os.path.dirname(__file__), "vectorizer.pkl")

try:
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    model_loaded = True
except Exception as e:
    st.error(f"Error loading model: {e}")
    model_loaded = False

# Page configuration
st.set_page_config(
    page_title="AI Sentiment Analyzer", 
    page_icon="🧠", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# Main title and description
st.title("🧠 Sentiment Analyzer App")
st.write("Detect the sentiment (Positive or Negative) of your text using AI 🤖")

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.write("This app uses a **Naive Bayes classifier** trained on sample text data to predict sentiment.")
    st.write("**How it works:**")
    st.write("1. Enter your text")
    st.write("2. Click 'Analyze Sentiment'")
    st.write("3. Get instant results!")
    
    st.header("🔧 Technical Details")
    st.write("- **Backend:** FastAPI")
    st.write("- **Frontend:** Streamlit")
    st.write("- **ML Model:** scikit-learn")
    st.write("- **Vectorization:** CountVectorizer")

# Main content area
if not model_loaded:
    st.error("❌ Model files not found. Please ensure the model is trained and saved.")
    st.stop()

# User input
st.subheader("✍️ Enter your text here:")
user_input = st.text_area(
    "Type or paste your text below:", 
    height=150,
    placeholder="Example: I love this movie! It's amazing..."
)

# Analyze button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("🔍 Analyze Sentiment", type="primary", use_container_width=True)

# Analysis logic
if analyze_button:
    if user_input.strip() == "":
        st.warning("⚠️ Please enter some text first.")
    else:
        with st.spinner("Analyzing sentiment..."):
            try:
                # Transform text to vector
                text_vector = vectorizer.transform([user_input])
                
                # Make prediction
                prediction = model.predict(text_vector)[0]
                
                # Get prediction probability
                probabilities = model.predict_proba(text_vector)[0]
                confidence = max(probabilities) * 100
                
                # Display results
                if prediction == 1:
                    sentiment = "😊 Positive"
                    color = "green"
                else:
                    sentiment = "😞 Negative"
                    color = "red"
                
                # Show result
                st.success(f"**Predicted Sentiment:** {sentiment}")
                st.info(f"**Confidence:** {confidence:.1f}%")
                
                # Show probability breakdown
                st.subheader("📊 Probability Breakdown")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Positive", f"{probabilities[1]*100:.1f}%")
                with col2:
                    st.metric("Negative", f"{probabilities[0]*100:.1f}%")
                
                # Progress bar for confidence
                st.progress(probabilities[1] if prediction == 1 else probabilities[0])
                
            except Exception as e:
                st.error(f"Error during analysis: {e}")

# Footer
st.markdown("---")
st.caption("Made with ❤️ using FastAPI, Streamlit, and scikit-learn.")

# Example texts
with st.expander("💡 Try these examples"):
    st.write("**Positive examples:**")
    st.write("- I love this movie!")
    st.write("- This is amazing!")
    st.write("- What a great day!")
    
    st.write("**Negative examples:**")
    st.write("- I hate this")
    st.write("- This was terrible")
    st.write("- Worst experience ever")
