import streamlit as st
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Create Gemini model
model = genai.GenerativeModel(model="models/gemini-pro")

# Language options
languages = {
    "English": "en",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
    "Kannada": "kn",
    "Bengali": "bn",
    "Marathi": "mr",
    "Bhojpuri": "bho"
}

# Streamlit UI
st.title("📝 Consent Form AI Generator")
st.markdown("Generate patient consent forms in your preferred language using AI.")

# Form inputs
patient_name = st.text_input("Patient Name")
age = st.text_input("Age")
procedure = st.text_input("Procedure Name")
language_selected = st.selectbox("Select Language", list(languages.keys()))
additional_info = st.text_area("Additional Notes (optional)")

# Button to generate
if st.button("Generate Consent Form"):
    if patient_name and age and procedure:
        lang_code = languages[language_selected]

        # Prompt to Gemini
        prompt = (
            f"Generate a patient consent form in {language_selected} language "
            f"for a patient named {patient_name}, aged {age}, undergoing {procedure}. "
            f"Ensure it follows standard Indian hospital consent format. "
        )
        if additional_info:
            prompt += f"Include this extra detail: {additional_info}"

        # Get response from Gemini
        try:
            response = model.generate_content(prompt)
            st.subheader("🧾 Consent Form:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please fill in all required fields (Name, Age, Procedure).")
