import streamlit as st
import joblib
import numpy as np
import random
import time

st.set_page_config(
    page_title="Text Emotion Classifier", 
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource(show_spinner="Loading emotion detection model...")
def load_model():
    model = joblib.load('final_text_classifier.pkl')
    vectorizer = joblib.load('tfidf_vectorizer.pkl')
    return model, vectorizer

# Load the model - the spinner is handled by the decorator
model, vectorizer = load_model()

emoji_mapping = {
    0: "😢",
    1: "😠", 
    2: "😍",
    3: "😲",
    4: "😨",
    5: "😊"
}

emotion_names = {
    0: "Sadness",
    1: "Anger", 
    2: "Love",
    3: "Surprise",
    4: "Fear",
    5: "Joy"
}

if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'show_emojis' not in st.session_state:
    st.session_state.show_emojis = False

st.title("Text Emotion Classifier")
st.write("Enter text to analyze its emotional sentiment and receive a classification with confidence metrics.")

# About This App section
st.sidebar.header("About This Application")
st.sidebar.write("""
This sophisticated emotion classification system leverages advanced machine learning algorithms 
trained on extensive textual datasets to accurately identify and categorize emotional content 
across six primary emotional states: sadness, anger, love, surprise, fear, and joy.
""")

user_input = st.text_area("Enter your text here:", value=st.session_state.user_input, height=100)

st.sidebar.header("Options")
show_details = st.sidebar.checkbox("Show detailed analysis")

st.sidebar.header("Try these examples")
examples = [
    "I'm so happy today!",
    "This makes me really angry",
    "I love this so much",
    "That surprised me"
]

for example in examples:
    if st.sidebar.button(example):
        st.session_state.user_input = example
        st.rerun()

st.sidebar.header("Or upload a text file")
uploaded_file = st.sidebar.file_uploader("Drag and drop file here", type="txt")
if uploaded_file is not None:
    try:
        text = str(uploaded_file.read(), "utf-8")
        st.session_state.user_input = text
        st.rerun()
    except:
        st.sidebar.error("Error reading file.")

if st.button("Analyze Emotion"):
    if user_input:
        # Set flag to show emojis
        st.session_state.show_emojis = True
        
        # Show processing spinner
        with st.spinner('Analyzing emotions...'):
            # Process the text
            text_tfidf = vectorizer.transform([user_input])
            prediction = model.predict(text_tfidf)
            predicted_class = prediction[0]
            emoji = emoji_mapping.get(predicted_class, "❓")
            emotion_name = emotion_names.get(predicted_class, "Unknown")
        
        # Create a placeholder for the falling emojis
        emoji_placeholder = st.empty()
        
        # Display falling emojis for 3 seconds
        start_time = time.time()
        while time.time() - start_time < 3:
            # Create random emojis falling from the top
            emoji_html = ""
            for _ in range(15):
                random_emoji = random.choice(list(emoji_mapping.values()))
                left_position = random.randint(5, 95)
                animation_duration = random.uniform(2, 5)
                emoji_html += f'<div class="emoji-fall" style="left: {left_position}%; animation-duration: {animation_duration}s;">{random_emoji}</div>'
            
            emoji_placeholder.markdown(emoji_html, unsafe_allow_html=True)
            time.sleep(0.1)
        
        # Clear the emojis
        emoji_placeholder.empty()
        st.session_state.show_emojis = False
        
        # Show the results
        st.success(f"Predicted Emotion: {emotion_name} {emoji}")
        
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(text_tfidf)[0]
            st.subheader("Confidence Scores:")
            
            st.bar_chart({emotion_names[i]: probabilities[i] for i in range(len(probabilities))})
            
            if show_details:
                st.write("Detailed confidence scores:")
                for i, prob in enumerate(probabilities):
                    st.write(f"{emoji_mapping.get(i, '❓')} {emotion_names.get(i, 'Unknown')}: {prob:.2%}")
    else:
        st.warning("Please enter some text first!")

st.markdown("---")
st.caption("Built with Streamlit and scikit-learn")