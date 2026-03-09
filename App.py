import streamlit as st
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from PIL import Image
import pytesseract

# -------- TESSERACT PATH --------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.set_page_config(page_title="AI Spam Detector", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
h1 {color:#6c63ff;}
.stButton>button{
background: linear-gradient(90deg,#6c63ff,#8e44ff);
color:white;
border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "intro1"

if "users" not in st.session_state:
    st.session_state.users = {"admin":"1234"}

if "logged" not in st.session_state:
    st.session_state.logged = False

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- INTRO PAGE 1 ----------------
if st.session_state.page == "intro1":

    st.title("AI Spam Detector")

    st.write("""
Welcome to **AI Spam Detector**

This system uses Machine Learning to detect:

• Spam messages  
• Phishing attacks  
• Scam links  
• Fraud messages
""")

    col1,col2 = st.columns(2)

    if col1.button("Next"):
        st.session_state.page="intro2"

    if col2.button("Skip"):
        st.session_state.page="login"

# ---------------- INTRO PAGE 2 ----------------
elif st.session_state.page == "intro2":

    st.title("How To Use")

    st.write("""
Steps:

1. Login to the system  
2. Enter a suspicious message  
3. AI analyzes the text  
4. View Risk Percentage  
5. Follow safety recommendation
""")

    col1,col2 = st.columns(2)

    if col1.button("Next"):
        st.session_state.page="login"

    if col2.button("Skip"):
        st.session_state.page="login"

# ---------------- LOGIN PAGE ----------------
elif st.session_state.page == "login":

    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Login"):

        if username in st.session_state.users and st.session_state.users[username]==password:

            st.session_state.logged=True
            st.session_state.page="app"

        else:
            st.error("Invalid Login")

    st.markdown("---")

    st.write("Not registered yet?")

    if st.button("Create Account"):
        st.session_state.page="register"

# ---------------- REGISTER PAGE ----------------
elif st.session_state.page == "register":

    st.title("Create Account")

    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password",type="password")

    if st.button("Register"):

        if new_user in st.session_state.users:

            st.warning("Username already exists")

        else:

            st.session_state.users[new_user]=new_pass
            st.success("Account created")

    if st.button("Back to Login"):
        st.session_state.page="login"

# ---------------- MAIN APP ----------------
elif st.session_state.page == "app":

    st.title("AI Spam Detector")

    model = pickle.load(open("model.pkl","rb"))
    vectorizer = pickle.load(open("vectorizer.pkl","rb"))

    tab1,tab2,tab3 = st.tabs(["Text Detection","Screenshot Detection","Dashboard"])

# ---------- TEXT DETECTION ----------
    with tab1:

        message = st.text_area("Enter message")

        if st.button("Analyze Message"):

            vector = vectorizer.transform([message])
            prediction = model.predict(vector)[0]
            prob = model.predict_proba(vector)[0][1]

            risk = round(prob*100,2)
            safe = 100-risk

            if prediction==1:

                result="Spam"
                st.error("Spam Message Detected")

                advice="""
Do NOT click unknown links  
Do NOT share OTP or bank details  
Block the sender  
Report message as spam
"""

            else:

                result="Safe"
                st.success("Message Looks Safe")

                advice="""
Verify unknown senders  
Avoid sharing sensitive information
"""

            st.subheader("Risk Score")

            st.progress(int(risk))
            st.write(f"Risk Percentage: {risk}%")

# ---------- WAVE GRAPH ----------
            x = np.linspace(0,10,100)

            risk_wave = np.sin(x)*(risk/100)
            safe_wave = np.cos(x)*(safe/100)

            fig,ax = plt.subplots()

            ax.plot(x,risk_wave,color="red",label="Risk")
            ax.plot(x,safe_wave,color="green",label="Safe")

            ax.legend()
            ax.set_title("Spam Risk vs Safety")

            st.pyplot(fig)

# ---------- LINK DETECTION ----------
            links = re.findall(r'https?://\S+|www\.\S+', message)

            if links:

                st.warning("Suspicious Links Found")

                for link in links:
                    st.write(link)

            st.subheader("AI Recommendation")
            st.info(advice)

            st.session_state.history.append({
                "Message":message,
                "Result":result,
                "Risk %":risk
            })

# ---------- SCREENSHOT DETECTION ----------
    with tab2:

        st.subheader("Upload Screenshot")

        uploaded = st.file_uploader("Upload image",type=["png","jpg","jpeg"])

        if uploaded is not None:

            image = Image.open(uploaded)

            st.image(image,caption="Uploaded Screenshot")

            text = pytesseract.image_to_string(image)

            st.write("Extracted Text:")
            st.write(text)

            vector = vectorizer.transform([text])
            prediction = model.predict(vector)[0]
            prob = model.predict_proba(vector)[0][1]

            risk = round(prob*100,2)

            if prediction==1:
                st.error("Spam Detected")
            else:
                st.success("Message Looks Safe")

# ---------- DASHBOARD ----------
    with tab3:

        st.subheader("Detection History")

        if st.session_state.history:

            df = pd.DataFrame(st.session_state.history)

            st.dataframe(df)

            scam_count = len(df[df["Result"]=="Spam"])
            safe_count = len(df[df["Result"]=="Safe"])

            labels=["Spam","Safe"]
            values=[scam_count,safe_count]

            fig = plt.figure()

            plt.bar(labels,values)

            plt.title("Detection Statistics")

            st.pyplot(fig)

        else:

            st.write("No messages analyzed yet")
