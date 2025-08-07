import streamlit as st
import google.generativeai as genai
import os

# Configure Gemini with API key from environment variable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini Pro model
model = genai.GenerativeModel(model_name="gemini-pro")

# Streamlit App UI
st.title("📄 Consent Form Generator (NABH Format)")
st.markdown("Generate multilingual NABH-format consent forms instantly.")

# Input Fields
patient_name = st.text_input("👤 Patient Name")
age = st.text_input("🎂 Age")
hospital_name = st.text_input("🏥 Hospital Name")
ip_number = st.text_input("🆔 IP Number")
consent_heading = st.text_input("📝 Consent Title")
language = st.selectbox("🌐 Preferred Language", [
    "English", "Tamil", "Telugu", "Malayalam", "Kannada", "Marathi", "Bengali"
])

if st.button("Generate Consent Form"):
    if not all([patient_name, age, hospital_name, ip_number, consent_heading]):
        st.warning("Please fill in all the fields.")
    else:
        # Prompt to Gemini
        prompt = f"""
You are an expert medical documentation AI. Generate a detailed patient consent form in {language} 
for the procedure titled: "{consent_heading}".

Include:
- Patient Details:
  - Name: {patient_name}
  - Age: {age}
  - IP Number: {ip_number}
  - Hospital: {hospital_name}

Follow NABH guidelines strictly. Include the following sections:
- Description of the procedure
- Risks involved
- Benefits
- Alternatives (if any)
- Post-procedure care
- Patient understanding and acknowledgment
- Signature section

Use professional, patient-friendly language. Format clearly. 
Return the response only in {language}, using native script where applicable.
"""

        # Generate content
        try:
            response = model.generate_content(prompt)
            st.success("Consent Form Generated ✅")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Error: {str(e)}")
