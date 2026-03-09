import streamlit as st
import pickle
import re
import pandas as pd
import matplotlib.pyplot as plt

# Load model
model = pickle.load(open("model.pkl","rb"))
vectorizer = pickle.load(open("vectorizer.pkl","rb"))

# Login
USERNAME = "admin"
PASSWORD = "1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

# Login Page
if not st.session_state.logged_in:

    st.title("🔐 AI Scam Detection System")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == USERNAME and pwd == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login Successful")
        else:
            st.error("Invalid Credentials")

# Main App
else:

    st.title("🛡 AI Scam Message Detection")

    tab1, tab2 = st.tabs(["Detect Message", "Dashboard"])

    # ---------------- DETECTION TAB ----------------
    with tab1:

        message = st.text_area("Enter message to analyze")

        if st.button("Detect Scam"):

            vector = vectorizer.transform([message])
            prediction = model.predict(vector)[0]
            prob = model.predict_proba(vector)[0][1]

            risk_score = round(prob*100,2)

            links = re.findall(r'https?://\S+|www\.\S+', message)

            if prediction == 1:
                result = "Scam"
                st.error("🚨 Scam Message Detected")
            else:
                result = "Safe"
                st.success("✅ Safe Message")

            st.write("Risk Score:", risk_score,"%")
            st.progress(int(risk_score))

            if links:
                st.warning("Suspicious Links Found")
                for l in links:
                    st.write(l)

            st.info("Never share OTP or passwords.")

            st.session_state.history.append({
                "Message": message,
                "Result": result,
                "Risk Score": risk_score
            })

    # ---------------- DASHBOARD TAB ----------------
    with tab2:

        st.subheader("📊 Detection Statistics")

        if st.session_state.history:

            df = pd.DataFrame(st.session_state.history)

            scam_count = len(df[df["Result"]=="Scam"])
            safe_count = len(df[df["Result"]=="Safe"])

            labels = ["Scam","Safe"]
            values = [scam_count, safe_count]

            fig = plt.figure()
            plt.bar(labels, values)
            plt.title("Scam vs Safe Messages")

            st.pyplot(fig)

            st.subheader("Detection History")
            st.dataframe(df)

        else:
            st.write("No detections yet.")