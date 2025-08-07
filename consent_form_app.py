import streamlit as st
import google.generativeai as genai
import os

# Configure API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Helper to try Gemini Pro first, then fallback
def get_gemini_response(prompt):
    model_names = ["models/gemini-pro", "models/gemini-pro-vision", "models/chat-bison-001"]
    
    for name in model_names:
        try:
            model = genai.GenerativeModel(model_name=name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.warning(f"⚠️ Failed with model: {name} – {e}")
    return None

# Streamlit UI
st.title("📄 Consent Form Generator (NABH Format)")
st.markdown("Generate patient-specific consent forms instantly.")

# Input fields
patient_name = st.text_input("👤 Patient Name")
patient_age = st.text_input("🎂 Age")
hospital_name = st.text_input("🏥 Hospital Name")
ip_number = st.text_input("🆔 IP Number")
consent_heading = st.text_input("📑 Consent Heading / Procedure")
language = st.selectbox("🌐 Preferred Language", ["English", "Tamil", "Hindi", "Telugu", "Malayalam", "Kannada", "Marathi", "Bengali"])

# Generate button
if st.button("📝 Generate Consent Form"):
    if not all([patient_name, patient_age, hospital_name, ip_number, consent_heading]):
        st.warning("⚠️ Please fill all the fields.")
    else:
        # Gemini prompt
        prompt = f"""
You are an expert medical writer. Create a detailed patient consent form 
in {language} for the following information, following NABH guidelines.

Patient Name: {patient_name}
Age: {patient_age}
Hospital Name: {hospital_name}
IP Number: {ip_number}
Consent Heading / Procedure: {consent_heading}

Include:
- Description of the procedure
- Risks involved
- Available alternatives
- Post-operative care (if applicable)
- Patient acknowledgement
- Signature section

Language: {language} (Use the native script and medical terminology)
Make it professional and easy to understand.
"""
        # Get Gemini response with fallback
        content = get_gemini_response(prompt)

        if content:
            st.success("✅ Consent Form Generated")
            st.markdown(content)
        else:
            st.error("❌ Could not generate the consent form. All model attempts failed.")
