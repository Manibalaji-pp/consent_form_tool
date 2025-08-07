import streamlit as st
import google.generativeai as genai
import os

# Load API Key from Streamlit secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Correct model name (do NOT include "models/")
model = genai.GenerativeModel("gemini-pro")

st.set_page_config(page_title="Consent Form Generator", layout="centered")

st.title("📝 Consent Form Generator (NABH Format)")
st.markdown("Generate patient-specific consent forms instantly.")

# Input fields
patient_name = st.text_input("Patient Name")
procedure_name = st.text_input("Consent Name")
language = st.selectbox("Preferred Language", ["English", "Tamil", "Hindi"])

# Button to generate form
if st.button("Generate Consent Form"):
    if not patient_name or not procedure_name:
        st.warning("Please enter both patient name and procedure name.")
    else:
        prompt = f"""
        Generate a medical consent form for patient named {patient_name} undergoing the procedure "{procedure_name}".
        Format the form according to NABH guidelines.
        Language: {language}.
        """
        with st.spinner("Generating..."):
            response = model.generate_content(prompt)
            st.success("Consent Form Generated")
            st.text_area("Consent Form", response.text, height=400)
