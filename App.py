import streamlit as st
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="AI Scam Detector", page_icon="🛡", layout="wide")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
body {
background-color:#0f172a;
color:white;
}

h1{
color:#7c6cff;
}

.stButton>button{
background: linear-gradient(90deg,#4f46e5,#9333ea);
color:white;
border-radius:10px;
height:3em;
width:200px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD MODEL ----------------
model = pickle.load(open("model.pkl","rb"))
vectorizer = pickle.load(open("vectorizer.pkl","rb"))

# ---------------- SESSION ----------------
if "users" not in st.session_state:
    st.session_state.users = {}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- MENU ----------------
menu = ["Login","Register"]
choice = st.sidebar.selectbox("Menu",menu)

# ---------------- REGISTER ----------------
if choice == "Register":

    st.title("📝 Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Register"):

        if username in st.session_state.users:
            st.warning("User already exists")

        else:
            st.session_state.users[username] = password
            st.success("Account Created")

# ---------------- LOGIN ----------------
if choice == "Login":

    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Login"):

        if username in st.session_state.users and st.session_state.users[username]==password:

            st.session_state.logged_in=True
            st.success("Login Successful")

        else:

            st.error("Invalid credentials")

# ---------------- MAIN APP ----------------
if st.session_state.logged_in:

    st.title("🛡 AI Scam Message Detection System")

    message = st.text_area("Enter message to analyze")

    if st.button("Analyze Message"):

        vector = vectorizer.transform([message])
        prediction = model.predict(vector)[0]
        probability = model.predict_proba(vector)[0][1]

        risk = round(probability*100,2)
        safe = 100-risk

        if prediction == 1:

            result="Scam"

            st.error("🚨 Scam Message Detected")

            advice="""
⚠ What you should do:
• Do NOT click suspicious links
• Do NOT share OTP or bank info
• Block sender
• Report message
"""

        else:

            result="Safe"

            st.success("✅ Message Looks Safe")

            advice="""
✔ Recommended:
• Verify unknown senders
• Avoid sharing sensitive data
"""

        st.subheader("Risk Score")

        st.progress(int(risk))
        st.write(f"Risk Percentage: **{risk}%**")

        st.subheader("Safety Analysis Graph")

        fig=plt.figure()

        labels=["Risk","Safe"]
        values=[risk,safe]

        plt.bar(labels,values)

        st.pyplot(fig)

        links = re.findall(r'https?://\S+|www\.\S+', message)

        if links:

            st.warning("⚠ Suspicious Links Detected")

            for link in links:
                st.write(link)

        st.subheader("AI Recommendation")

        st.info(advice)

        st.session_state.history.append({
            "Message":message,
            "Result":result,
            "Risk %":risk
        })

    st.subheader("Detection History")

    if st.session_state.history:

        df=pd.DataFrame(st.session_state.history)
        st.dataframe(df)
