 AI Response Evaluation & Annotation System (RLHF-Based)

A lightweight tool designed to evaluate, compare, and annotate AI-generated outputs.

---

 Features

Text Response Comparison  
- Compare Response A vs Response B  
- Correctness, clarity, and reasoning scoring  
- Save annotations with a unique reference key  

### ✔ Hallucination Annotation  
- Flag incorrect facts  
- Unsupported claims  
- Fabricated numbers  
- Safety / policy violations  

 Image Evaluation  
- Upload image  
- Validate AI predicted label  
- Mark correct or wrong  
- Provide corrected label  

---

 Tech Stack  
- **Frontend:** Streamlit  
- **Backend:** Python  
- **Database:** JSON (local)  
- **Image Processing:** Pillow  

---

 Installation  

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

---

 Data Storage  
All annotations are stored in:

```
annotations.json
```

---

 License  
MIT License.
