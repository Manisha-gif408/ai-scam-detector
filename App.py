import streamlit as st
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

st.set_page_config(page_title="AI Spam Detector", layout="wide")

# ---------- STYLE ----------
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

# ---------- SESSION STATES ----------
if "page" not in st.session_state:
    st.session_state.page = "intro1"

if "users" not in st.session_state:
    st.session_state.users = {"admin":"1234"}

if "logged" not in st.session_state:
    st.session_state.logged = False

if "history" not in st.session_state:
    st.session_state.history = []

# ---------- INTRO SCREEN 1 ----------
if st.session_state.page == "intro1":

    st.title("AI Spam Detector")

    st.write("""
Welcome to **AI Spam Detector**

This system uses Machine Learning to detect:

• Spam messages  
• Phishing attempts  
• Scam links  
• Fraud messages
""")

    col1,col2 = st.columns(2)

    with col1:
        if st.button("Next"):
            st.session_state.page="intro2"

    with col2:
        if st.button("Skip"):
            st.session_state.page="login"

# ---------- INTRO SCREEN 2 ----------
elif st.session_state.page == "intro2":

    st.title("How It Works")

    st.write("""
Steps to use the system:

1. Login to the system  
2. Enter a suspicious message  
3. AI analyzes the message  
4. View **Risk Percentage**
5. Follow **Safety Recommendations**
""")

    col1,col2 = st.columns(2)

    with col1:
        if st.button("Next"):
            st.session_state.page="login"

    with col2:
        if st.button("Skip"):
            st.session_state.page="login"

# ---------- LOGIN PAGE ----------
elif st.session_state.page == "login":

    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Login"):

        if username in st.session_state.users and st.session_state.users[username]==password:

            st.session_state.logged=True
            st.session_state.page="app"
            st.success("Login Successful")

        else:
            st.error("Invalid login")

# ---------- MAIN APP ----------
elif st.session_state.page == "app":

    st.title("AI Spam Detector")

    model = pickle.load(open("model.pkl","rb"))
    vectorizer = pickle.load(open("vectorizer.pkl","rb"))

    message = st.text_area("Enter message to analyze")

    if st.button("Analyze Message"):

        vector = vectorizer.transform([message])
        prediction = model.predict(vector)[0]
        probability = model.predict_proba(vector)[0][1]

        risk = round(probability*100,2)
        safe = 100-risk

        # ---------- RESULT ----------
        if prediction == 1:

            result="Spam"
            st.error("Spam Message Detected")

            suggestion="""
Do NOT click suspicious links  
Do NOT share OTP or bank details  
Block the sender  
Report as spam
"""

        else:

            result="Safe"
            st.success("Message Looks Safe")

            suggestion="""
Still verify unknown links  
Avoid sharing personal information
"""

        st.subheader("Risk Score")
        st.progress(int(risk))
        st.write(f"Risk Percentage: {risk}%")

        # ---------- WAVE GRAPH ----------
        st.subheader("Risk Analysis Wave")

        x = np.linspace(0,10,100)

        risk_wave = np.sin(x) * (risk/100)
        safe_wave = np.cos(x) * (safe/100)

        fig, ax = plt.subplots()

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

        # ---------- SUGGESTION ----------
        st.subheader("AI Recommendation")

        st.info(suggestion)

        st.session_state.history.append({
            "Message":message,
            "Result":result,
            "Risk %":risk
        })

    # ---------- HISTORY ----------
    st.subheader("Detection History")

    if st.session_state.history:

        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df)

    else:
        st.write("No messages analyzed yet")
