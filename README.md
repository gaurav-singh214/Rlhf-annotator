import streamlit as st
import json
from PIL import Image
import uuid

st.set_page_config(page_title="AI Response Evaluation & Annotation System", layout="wide")

# Storage file
DATA_FILE = "annotations.json"

# Load saved annotations
try:
    with open(DATA_FILE, "r") as f:
        db = json.load(f)
except:
    db = []

# Save annotation object
def save_entry(entry):
    db.append(entry)
    with open(DATA_FILE, "w") as f:
        json.dump(db, f, indent=4)

# Title
st.title(" AI Response Evaluation & Annotation System (RLHF-Based)")
st.write("Compare, rank, detect hallucinations, evaluate images, and store feedback.")

# Unique reference key
if "ref_key" not in st.session_state:
    st.session_state.ref_key = str(uuid.uuid4())

st.sidebar.markdown(f"### Reference Key: `{st.session_state.ref_key}`")

# Tabs
text_tab, halluc_tab, img_tab = st.tabs([
    " Text Response Comparison",
    " Hallucination Annotation",
    " Image Evaluation"
])

# =============== TEXT COMPARISON ==================
with text_tab:
    st.header(" Compare AI Responses")

    prompt = st.text_area("Enter Prompt:")
    col1, col2 = st.columns(2)
    with col1:
        resp_a = st.text_area("Response A", height=200)
    with col2:
        resp_b = st.text_area("Response B", height=200)

    correctness = st.radio("Which response is more correct?", ["A", "B", "Both Equal"], horizontal=True)
    clarity = st.radio("Clarity Winner", ["A", "B", "Both Equal"], horizontal=True)
    reasoning = st.radio("Reasoning Quality Winner", ["A", "B", "Both Equal"], horizontal=True)

    if st.button("Save Comparison Annotation"):
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

# =============== HALLUCINATION MODULE ==================
with halluc_tab:
    st.header("Manual Hallucination Annotation")

    halluc_text = st.text_area("Paste AI Response:")

    wrong_fact = st.checkbox("Incorrect Fact")
    unsupported = st.checkbox("Unsupported Claim")
    numbers = st.checkbox("Made-up Numbers")
    safety = st.checkbox("Safety / Policy Violation")

    notes = st.text_area("Additional Notes:")

    if st.button("Save Hallucination Annotation"):
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

# =============== IMAGE EVALUATION ==================
with img_tab:
    st.header("Image Classification Verification")

    uploaded = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    predicted_label = st.text_input("AI Predicted Label:")
    correct = st.radio("Is the prediction correct?", ["Yes", "No"])
    correct_label = None

    if correct == "No":
        correct_label = st.text_input("Enter Correct Label:")

    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="Uploaded Image", use_column_width=True)

    if st.button("Save Image Evaluation"):
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
st.write("All evaluations are stored locally in `annotations.json`.")
