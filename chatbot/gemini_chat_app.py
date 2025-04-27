import streamlit as st

# ✅ MUST be first Streamlit command
st.set_page_config(
    page_title="EcoPic Assistant",
   
    layout="centered"
)

from dotenv import load_dotenv
import os
import google.generativeai as genai

# ✅ Load environment variables
load_dotenv()

# ✅ Cache model loading
@st.cache_resource
def load_model():
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    return genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

model = load_model()

# ✅ Function to get Gemini response (with streaming)
def get_gemini_response(question):
    response = model.generate_content(question, stream=True)
    answer = ""
    for chunk in response:
        if chunk.text:
            answer += chunk.text
            yield answer

# ✅ Health suggestions
health_suggestions = [
    "How to cure fever?",
    "What are the symptoms of dengue?",
    "Home remedies for cold",
    "How to reduce body pain?",
    "What to do for a sore throat?",
    "Tips for healthy skin",
    "How to boost immunity?",
    "Is headache a sign of stress?",
    "Foods to eat during fever",
    "Natural remedies for cough",
    "How to cure asthma?"
]

# ✅ Initialize session state
if "user_query" not in st.session_state:
    st.session_state.user_query = ""
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ✅ Streamlit App UI
st.header("🩺 QueueCare Health Assistant")

# ✅ Text input (press Enter submits)
user_query = st.text_input(
    "Ask your health question:",
    value=st.session_state.user_query,
    placeholder="Start typing...",
    on_change=lambda: st.session_state.update(submitted=True)
)

# ✅ Show live suggestions
if user_query and not st.session_state.submitted:
    matches = [q for q in health_suggestions if user_query.lower() in q.lower()]
    if matches:
        st.markdown("*Suggestions:*")
        for match in matches:
            if st.button(match):
                st.session_state.user_query = match
                st.rerun()  # 🔥 Only rerun if user clicks a suggestion

submit = st.button("Ask")

# ✅ Handle submission (either Enter pressed OR Ask button clicked)
if (submit or st.session_state.submitted) and user_query:
    with st.spinner("Analyzing your health question..."):
        response_placeholder = st.empty()
        partial_response = ""
        for partial_text in get_gemini_response(user_query):
            partial_response = partial_text
            response_placeholder.markdown(partial_response)
    
    # ✅ After answering: clear input field, but DO NOT rerun the app
    st.session_state.user_query = ""
    st.session_state.submitted = False

elif (submit or st.session_state.submitted) and not user_query:
    st.warning("Please type your health question first.")
    st.session_state.submitted = False  # Reset submit flag
