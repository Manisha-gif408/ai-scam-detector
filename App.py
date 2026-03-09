import streamlit as st
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Scam Detector",
    page_icon="🛡",
    layout="wide"
)

# ---------------- CUSTOM UI COLORS ----------------
st.markdown("""
<style>

body {
background-color: #f7f8ff;
}

h1 {
color: #4b3fe4;
}

.stButton>button {
background-color: #4b3fe4;
color: white;
border-radius: 10px;
height: 3em;
width: 200px;
}

.stTextArea textarea {
background-color: #eef1ff;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD MODEL ----------------
model = pickle.load(open("model.pkl","rb"))
vectorizer = pickle.load(open("vectorizer.pkl","rb"))

# ---------------- SESSION STORAGE ----------------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- TITLE ----------------
st.title("🛡 AI Scam Message Detection System")

st.write(
"Detect scam, phishing, and spam messages using a Machine Learning model."
)

# ---------------- INPUT MESSAGE ----------------
message = st.text_area("Enter the message you want to analyze")

# ---------------- DETECTION ----------------
if st.button("Analyze Message"):

    vector = vectorizer.transform([message])
    prediction = model.predict(vector)[0]
    probability = model.predict_proba(vector)[0][1]

    risk_score = round(probability * 100, 2)
    safe_score = 100 - risk_score

    # ---------- RESULT ----------
    if prediction == 1:

        result = "Scam"

        st.error("🚨 Scam Message Detected")

        suggestion = """
        ⚠ Recommended Actions:
        • Do NOT click unknown links
        • Do NOT share OTP or bank details
        • Block the sender
        • Report the message as spam
        """

    else:

        result = "Safe"

        st.success("✅ Message Looks Safe")

        suggestion = """
        ✔ Recommended Actions:
        • Message appears safe
        • Still verify unknown links
        • Avoid sharing sensitive information
        """

    # ---------- RISK SCORE ----------
    st.subheader("Risk Score")

    st.progress(int(risk_score))

    st.write(f"Risk Percentage: **{risk_score}%**")

    # ---------- GRAPH ----------
    st.subheader("Safety Analysis Graph")

    labels = ["Risk", "Safe"]
    values = [risk_score, safe_score]

    fig = plt.figure()
    plt.bar(labels, values)
    plt.title("Message Safety Analysis")

    st.pyplot(fig)

    # ---------- LINK DETECTION ----------
    links = re.findall(r'https?://\S+|www\.\S+', message)

    if links:

        st.warning("⚠ Suspicious Links Found")

        for link in links:
            st.write(link)

    # ---------- AI SUGGESTION ----------
    st.subheader("AI Recommendation")

    st.info(suggestion)

    # ---------- SAVE HISTORY ----------
    st.session_state.history.append({
        "Message": message,
        "Result": result,
        "Risk %": risk_score
    })

# ---------------- DASHBOARD ----------------
st.subheader("Detection History")

if st.session_state.history:

    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df)

else:

    st.write("No messages analyzed yet")
