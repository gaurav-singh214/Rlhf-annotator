import streamlit as st
import json
import uuid
from PIL import Image
from groq import Groq
from openai import OpenAI

st.set_page_config(page_title="AI Response Evaluation & Annotation System", layout="wide")

# ---------------------------
# Load & Save DB
# ---------------------------
DATA_FILE = "annotations.json"

try:
    with open(DATA_FILE, "r") as f:
        db = json.load(f)
except:
    db = []


def save_entry(entry):
    db.append(entry)
    with open(DATA_FILE, "w") as f:
        json.dump(db, f, indent=4)


# ---------------------------
# UI HEADER
# ---------------------------
st.title("🧠 AI Response Evaluation & Annotation System (RLHF-Based)")
st.write("Compare, auto-generate, detect hallucinations, evaluate images, and store feedback.")

# Unique reference key
if "ref_key" not in st.session_state:
    st.session_state.ref_key = str(uuid.uuid4())

st.sidebar.markdown(f"### Reference Key: `{st.session_state.ref_key}`")

# ---------------------------
# API Key Inputs
# ---------------------------
st.sidebar.subheader("🔑 API Keys")

groq_key = st.sidebar.text_input("Groq API Key", type="password")
openai_key = st.sidebar.text_input("OpenAI API Key (optional)", type="password")

if groq_key:
    groq_client = Groq(api_key=groq_key)
else:
    groq_client = None

if openai_key:
    openai_client = OpenAI(api_key=openai_key)
else:
    openai_client = None


# ---------------------------
# Available Models
# ---------------------------
groq_models = [
    "mixtral-8x7b-32768",
    "llama3-8b-8192",
    "llama3-70b-8192",
    "gemma-7b-it"
]

openai_models = [
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-3.5-turbo"
]


# ---------------------------
# Generate Response Function
# ---------------------------
def generate_groq_response(prompt, model):
    try:
        completion = groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return completion.choices[0].message["content"]

    except Exception as e:
        return f"[Groq Error] {e}"


def generate_openai_response(prompt, model):
    try:
        completion = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return completion.choices[0].message["content"]

    except Exception as e:
        return f"[OpenAI Error] {e}"


# ---------------------------
# TABS
# ---------------------------
text_tab, halluc_tab, img_tab = st.tabs([
    "📝 Text Response Comparison",
    "⚠️ Hallucination Annotation",
    "🖼️ Image Evaluation"
])


# ===================================================================
# 📝 TEXT COMPARISON TAB
# ===================================================================
with text_tab:
    st.header("📝 Compare AI Responses")

    prompt = st.text_area("Enter Prompt:")

    st.subheader("⚙ Model Selection")

    model_a = st.selectbox("Model for Response A (Groq)", groq_models)
    provider_b = st.selectbox("Model Provider for Response B", ["Groq", "OpenAI"])

    if provider_b == "Groq":
        model_b = st.selectbox("Groq Models", groq_models)
    else:
        model_b = st.selectbox("OpenAI Models", openai_models)

    # Text Areas
    col1, col2 = st.columns(2)
    with col1:
        resp_a = st.text_area("Response A", height=200)
    with col2:
        resp_b = st.text_area("Response B", height=200)

    # Generate Button
    if st.button("✨ Generate Responses Automatically"):
        if not groq_key:
            st.error("Groq API key required.")
        else:
            with st.spinner("Generating Response A..."):
                resp_a = generate_groq_response(prompt, model_a)

            if provider_b == "Groq":
                with st.spinner("Generating Response B (Groq)..."):
                    resp_b = generate_groq_response(prompt, model_b)
            else:
                if not openai_key:
                    st.error("OpenAI key required for GPT models.")
                else:
                    with st.spinner("Generating Response B (OpenAI)..."):
                        resp_b = generate_openai_response(prompt, model_b)

        # update text boxes
        st.session_state["resp_a"] = resp_a
        st.session_state["resp_b"] = resp_b

        st.success("Generated both responses!")

    # Comparison Fields
    correctness = st.radio("Correctness Winner", ["A", "B", "Both Equal"], horizontal=True)
    clarity = st.radio("Clarity Winner", ["A", "B", "Both Equal"], horizontal=True)
    reasoning = st.radio("Reasoning Winner", ["A", "B", "Both Equal"], horizontal=True)

    # Save Annotation
    if st.button("💾 Save Comparison Annotation"):
        entry = {
            "type": "text-comparison",
            "ref_key": st.session_state.ref_key,
            "prompt": prompt,
            "responseA": resp_a,
            "responseB": resp_b,
            "scores": {
                "correctness": correctness,
                "clarity": clarity,
                "reasoning": reasoning
            }
        }
        save_entry(entry)
        st.success("Saved annotation successfully!")


# ===================================================================
# ⚠ HALLUCINATION TAB
# ===================================================================
with halluc_tab:
    st.header("⚠️ Manual Hallucination Annotation")

    halluc_text = st.text_area("Paste AI Response:")

    wrong_fact = st.checkbox("Incorrect Fact")
    unsupported = st.checkbox("Unsupported Claim")
    numbers = st.checkbox("Made-up Numbers")
    safety = st.checkbox("Safety / Policy Violation")

    notes = st.text_area("Additional Notes:")

    if st.button("💾 Save Hallucination Annotation"):
        entry = {
            "type": "hallucination",
            "ref_key": st.session_state.ref_key,
            "response": halluc_text,
            "flags": {
                "incorrect_fact": wrong_fact,
                "unsupported_claim": unsupported,
                "made_up_numbers": numbers,
                "safety_violation": safety
            },
            "notes": notes
        }
        save_entry(entry)
        st.success("Hallucination annotation saved!")


# ===================================================================
# 🖼 IMAGE EVALUATION TAB
# ===================================================================
with img_tab:
    st.header("🖼 Image Classification Verification")

    uploaded = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    predicted_label = st.text_input("AI Predicted Label:")
    correct = st.radio("Is the prediction correct?", ["Yes", "No"])
    correct_label = None

    if correct == "No":
        correct_label = st.text_input("Enter Correct Label:")

    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="Uploaded Image", use_column_width=True)

    if st.button("💾 Save Image Evaluation"):
        entry = {
            "type": "image-eval",
            "ref_key": st.session_state.ref_key,
            "predicted_label": predicted_label,
            "is_correct": correct,
            "correct_label": correct_label,
        }
        save_entry(entry)
        st.success("Image evaluation saved!")

st.write("---")
st.write("All evaluations are saved in `annotations.json` locally.")
