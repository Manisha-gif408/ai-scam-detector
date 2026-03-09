import streamlit as st
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import re
from PIL import Image
import pytesseract

# Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Page setup
st.set_page_config(page_title="AI Scam Detector", page_icon="🛡", layout="wide")

# Custom colors
st.markdown("""
<style>
body {
    background-color: #0f172a;
}

h1,h2,h3 {
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

# Load ML model
model = pickle.load(open("model.pkl","rb"))
vectorizer = pickle.load(open("vectorizer.pkl","rb"))

# Session states
if "users" not in st.session_state:
    st.session_state.users = {"admin":"1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar menu
menu = ["Login","Register"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- REGISTER ----------------

if choice == "Register":

    st.title("📝 Register Account")

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")

    if st.button("Register"):

        if new_user in st.session_state.users:
            st.warning("User already exists")

        else:
            st.session_state.users[new_user] = new_pass
            st.success("Account created successfully")

# ---------------- LOGIN ----------------

if choice == "Login":

    st.title("🔐 Login to AI Scam Detector")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in st.session_state.users and st.session_state.users[username] == password:

            st.session_state.logged_in = True
            st.success("Login successful")

        else:
            st.error("Invalid credentials")

# ---------------- MAIN APP ----------------

if st.session_state.logged_in:

    st.title("🛡 AI Scam Message Detection System")

    tab1, tab2 = st.tabs(["Detect Message","Dashboard"])

    # -------- MESSAGE DETECTION --------

    with tab1:

        st.subheader("✉ Text Message Detection")

        message = st.text_area("Enter message")

        if st.button("Detect Message"):

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

            st.write("Risk Score:", risk,"%")
            st.progress(int(risk))

            if links:
                st.warning("⚠ Suspicious Links Found")
                for l in links:
                    st.write(l)

            st.session_state.history.append({
                "Message":message,
                "Result":result,
                "Risk":risk
            })

        # -------- SCREENSHOT DETECTION --------

        st.subheader("📷 Screenshot Detection")

        uploaded_file = st.file_uploader("Upload message screenshot", type=["png","jpg","jpeg"])

        if uploaded_file is not None:

            image = Image.open(uploaded_file)

            st.image(image, caption="Uploaded Screenshot")

            extracted_text = pytesseract.image_to_string(image)

            st.write("Extracted Text:")
            st.write(extracted_text)

            if st.button("Analyze Screenshot"):

                vector = vectorizer.transform([extracted_text])
                prediction = model.predict(vector)[0]

                prob = model.predict_proba(vector)[0][1]
                risk = round(prob*100,2)

                if prediction == 1:
                    result = "Scam"
                    st.error("🚨 Scam Detected")

                else:
                    result = "Safe"
                    st.success("✅ Safe Message")

                st.progress(int(risk))
                st.write("Risk Score:",risk,"%")

                st.session_state.history.append({
                    "Message":extracted_text,
                    "Result":result,
                    "Risk":risk
                })

    # -------- DASHBOARD --------

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
