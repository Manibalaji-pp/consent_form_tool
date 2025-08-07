import streamlit as st
import google.generativeai as genai
import os

# Load your API key from environment variable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Gemini Pro model
model = genai.GenerativeModel(model_name="gemini-pro")

# Streamlit UI
st.title("📄 Consent Form Generator (NABH Format)")
st.markdown("Generate patient-specific consent forms instantly.")

# Input fields
patient_name = st.text_input("Patient Name")
procedure_name = st.text_input("Consent Title")
language = st.selectbox("Preferred Language", ["English", "Tamil", "Hindi", "Telugu"])

if st.button("Generate Consent Form"):
    if not patient_name or not procedure_name:
        st.warning("Please enter both patient name and consent title.")
    else:
        # Generate prompt
        prompt = f"""
        Generate a detailed patient consent form in {language} for the procedure titled '{procedure_name}'. 
        The patient name is {patient_name}. Follow NABH guidelines. Include:

        - Procedure description  
        - Risks involved  
        - Alternatives  
        - Post-operative care (if applicable)  
        - Patient acknowledgment  
        - Signature section  

        Language: {language} (use native script)
        """

        # Call Gemini
        try:
            response = model.generate_content(prompt)
            st.success("Consent Form Generated ✅")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Error: {str(e)}")
