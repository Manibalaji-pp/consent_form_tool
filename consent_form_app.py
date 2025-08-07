import streamlit as st
import os
import google.generativeai as genai
import openai

# Load API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure Google & OpenAI
genai.configure(api_key=GOOGLE_API_KEY)
openai.api_key = OPENAI_API_KEY

# Try Gemini models first, fallback to OpenAI
def get_consent_content(prompt):
    # Try Gemini Models
    gemini_models = ["models/gemini-pro", "models/gemini-pro-vision"]
    for model_name in gemini_models:
        try:
            model = genai.GenerativeModel(model_name=model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.warning(f"⚠️ Gemini model {model_name} failed: {e}")

    # Fallback: Use OpenAI GPT-3.5
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if available
            messages=[
                {"role": "system", "content": "You are an expert medical consent form writer."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"❌ OpenAI API failed: {e}")
        return None

# Streamlit UI
st.title("📄 Consent Form Generator (NABH Format)")
st.markdown("Generate patient-specific consent forms using AI (Gemini + ChatGPT).")

# Input fields
patient_name = st.text_input("👤 Patient Name")
patient_age = st.text_input("🎂 Age")
hospital_name = st.text_input("🏥 Hospital Name")
ip_number = st.text_input("🆔 IP Number")
consent_heading = st.text_input("📑 Consent Heading / Procedure")
language = st.selectbox("🌐 Preferred Language", ["English", "Tamil", "Hindi", "Telugu", "Malayalam", "Kannada", "Marathi", "Bengali"])

if st.button("📝 Generate Consent Form"):
    if not all([patient_name, patient_age, hospital_name, ip_number, consent_heading]):
        st.warning("⚠️ Please fill all the fields.")
    else:
        prompt = f"""
Generate a detailed patient consent form in {language} (use native script) for the following:

Patient Name: {patient_name}
Age: {patient_age}
Hospital Name: {hospital_name}
IP Number: {ip_number}
Procedure / Consent Heading: {consent_heading}

Include:
- Description of the procedure
- Risks involved
- Available alternatives
- Post-operative care (if applicable)
- Patient acknowledgment
- Signature section

Follow NABH standards. Make the language easy to understand.
"""
        content = get_consent_content(prompt)
        if content:
            st.success("✅ Consent Form Generated")
            st.markdown(content)
        else:
            st.error("❌ All AI models failed to generate content.")
