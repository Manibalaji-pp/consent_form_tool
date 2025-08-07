import streamlit as st
import google.generativeai as genai
import os

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini Pro model
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

# Streamlit UI
st.title("📄 Consent Form Generator (NABH Format)")
st.markdown("Generate multilingual patient-specific consent forms instantly.")

# Input fields
patient_name = st.text_input("Patient Name")
patient_age = st.text_input("Age")
hospital_name = st.text_input("Hospital Name")
ip_number = st.text_input("IP Number")
consent_heading = st.text_input("Consent Heading")
language = st.selectbox("Preferred Language", [
    "English", "Tamil", "Hindi", "Telugu", "Malayalam", "Kannada", "Marathi", "Bengali"
])

# Consent form generation button
if st.button("Generate Consent Form"):
    if not all([patient_name, patient_age, hospital_name, ip_number, consent_heading]):
        st.warning("Please fill out all fields before generating the consent form.")
    else:
        prompt = f"""
        You are an expert medical writer. Create a detailed patient consent form 
        in {language} for the following information, following NABH guidelines.

        Patient Name: {patient_name}
        Age: {patient_age}
        Hospital Name: {hospital_name}
        IP Number: {ip_number}
        Consent Heading / Procedure: {
