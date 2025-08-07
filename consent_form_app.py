import streamlit as st
import google.generativeai as genai
import os

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini Model (correct model path)
model = genai.GenerativeModel("models/gemini-pro")

# UI
st.title("📄 Consent Form Generator (NABH Format)")

patient_name = st.text_input("👤 Patient Name")
age = st.text_input("🎂 Age")
hospital_name = st.text_input("🏥 Hospital Name")
ip_number = st.text_input("🆔 IP Number")
consent_heading = st.text_input("📝 Consent Title")
language = st.selectbox("🌐 Preferred Language", ["English", "Tamil", "Telugu", "Malayalam", "Kannada", "Marathi", "Bengali"])

if st.button("Generate Consent Form"):
    if not all([patient_name, age, hospital_name, ip_number, consent_heading]):
        st.warning("Please fill in all the fields.")
    else:
        prompt = f"""
Generate a NABH-compliant consent form in {language}, based on the following:

- Patient: {patient_name}
- Age: {age}
- IP No.: {ip_number}
- Hospital: {hospital_name}
- Title: {consent_heading}

Include:
- Procedure details
- Risks
- Alternatives
- Benefits
- Post-care instructions
- Patient acknowledgment
- Signature section

Output must be in {language}, using native script.
"""

        try:
            response = model.generate_content(prompt)
            st.success("Consent Form Generated ✅")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"❌ Error: {e}")
