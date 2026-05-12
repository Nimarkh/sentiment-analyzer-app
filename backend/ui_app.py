import streamlit as st

from model import ModelNotAvailableError, predict_sentiment

try:
    predict_sentiment("health check")
    model_loaded = True
except ModelNotAvailableError as e:
    st.error(f"Error loading model: {e}")
    model_loaded = False

st.set_page_config(
    page_title="Sentiment Analyzer",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("Sentiment Analyzer")
st.write("Enter a sentence or paragraph to classify its sentiment as positive or negative.")

with st.sidebar:
    st.header("About")
    st.write("This app uses a **Naive Bayes classifier** trained on sample text data to predict sentiment.")
    st.write("**How it works:**")
    st.write("1. Enter your text")
    st.write("2. Click Analyze Sentiment")
    st.write("3. Review the prediction")

    st.header("Technical Details")
    st.write("- **Backend:** FastAPI")
    st.write("- **Frontend:** Streamlit")
    st.write("- **ML Model:** scikit-learn")
    st.write("- **Vectorization:** CountVectorizer")

if not model_loaded:
    st.error("Model files not found. Please train and save the model first.")
    st.stop()

st.subheader("Enter your text")
user_input = st.text_area(
    "Type or paste your text below:",
    height=150,
    placeholder="Example: I love this movie! It's amazing..."
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("Analyze Sentiment", type="primary", use_container_width=True)

if analyze_button:
    if user_input.strip() == "":
        st.warning("Please enter some text first.")
    else:
        with st.spinner("Analyzing sentiment..."):
            try:
                prediction = predict_sentiment(user_input)
                sentiment = prediction["label"]
                confidence = prediction["confidence"]
                probabilities = prediction["probabilities"]

                confidence_percent = f"{confidence * 100:.1f}%" if confidence is not None else "N/A"

                st.success(f"**Predicted Sentiment:** {sentiment}")
                st.info(f"**Confidence:** {confidence_percent}")

                if probabilities is not None:
                    st.subheader("Probability Breakdown")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Positive", f"{probabilities['positive'] * 100:.1f}%")
                    with col2:
                        st.metric("Negative", f"{probabilities['negative'] * 100:.1f}%")

                    st.progress(confidence or 0)

            except Exception as e:
                st.error(f"Error during analysis: {e}")

st.markdown("---")
st.caption("Built with FastAPI, Streamlit, and scikit-learn.")

with st.expander("Example texts"):
    st.write("**Positive examples:**")
    st.write("- I love this movie!")
    st.write("- This is amazing!")
    st.write("- What a great day!")

    st.write("**Negative examples:**")
    st.write("- I hate this")
    st.write("- This was terrible")
    st.write("- Worst experience ever")
