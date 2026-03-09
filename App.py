import streamlit as st
import pickle
import re
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="AI Scam Detector", page_icon="🛡", layout="wide")

# Custom colors
st.markdown("""
<style>
body {
    background-color: #0f172a;
}

h1 {
    color: #38bdf8;
}

.stButton>button {
    background-color: #22c55e;
    color: white;
    border-radius: 10px;
}

.stTextInput>div>div>input {
    background-color: #1e293b;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Load model
model = pickle.load(open("model.pkl","rb"))
vectorizer = pickle.load(open("vectorizer.pkl","rb"))

# User database
if "users" not in st.session_state:
    st.session_state.users = {"admin":"1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- AUTH SYSTEM ----------------

menu = ["Login","Register"]

choice = st.sidebar.selectbox("Menu", menu)

# LOGIN
if choice == "Login":

    st.title("🔐 Login to AI Scam Detector")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.success("Login successful")
        else:
            st.error("Invalid username or password")

# REGISTER
if choice == "Register":

    st.title("📝 Create New Account")

    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Register"):

        if new_user in st.session_state.users:
            st.warning("User already exists")
        else:
            st.session_state.users[new_user] = new_pass
            st.success("Account created successfully")

# ---------------- MAIN APP ----------------

if st.session_state.logged_in:

    st.title("🛡 AI Scam Message Detection System")

    tab1, tab2 = st.tabs(["Detect Message","Dashboard"])

    # Detect message
    with tab1:

        message = st.text_area("Enter message to analyze")

        if st.button("Detect"):

            vector = vectorizer.transform([message])
            prediction = model.predict(vector)[0]
            prob = model.predict_proba(vector)[0][1]

            risk = round(prob*100,2)

            links = re.findall(r'https?://\S+|www\.\S+', message)

            if prediction == 1:
                result = "Scam"
                st.error("🚨 Scam Message Detected")
            else:
                result = "Safe"
                st.success("✅ Safe Message")

            st.progress(int(risk))
            st.write("Risk Score:",risk,"%")

            if links:
                st.warning("⚠ Suspicious Links Found")
                for l in links:
                    st.write(l)

            st.session_state.history.append({
                "Message":message,
                "Result":result,
                "Risk":risk
            })

    # Dashboard
    with tab2:

        st.subheader("📊 Detection Statistics")

        if st.session_state.history:

            df = pd.DataFrame(st.session_state.history)

            scam = len(df[df["Result"]=="Scam"])
            safe = len(df[df["Result"]=="Safe"])

            labels = ["Scam","Safe"]
            values = [scam,safe]

            fig = plt.figure()
            plt.bar(labels,values)
            plt.title("Scam vs Safe Messages")

            st.pyplot(fig)

            st.subheader("Detection History")
            st.dataframe(df)

        else:
            st.write("No detections yet")
