import streamlit as st
import google.generativeai as genai

# ✅ Configure Gemini with secret
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ✅ Use correct model name
model = genai.GenerativeModel("gemini-pro")

# UI
st.set_page_config(page_title="Consent Form Generator", layout="centered")
st.title("📝 Consent Form Generator ")
st.markdown("Generate patient-specific consent forms instantly.")

# Form inputs
patient_name = st.text_input("Patient Name")
Age = st.text_input("Age in Number ")
procedure_name = st.text_input("Consent Tittle")
language = st.selectbox("Preferred Language", ["English", "Tamil", "Hindi", "marati" , "kanada" , "Telugu" , " Bhojpuri" ,])

if st.button("Generate Consent Form"):
    if not patient_name or not procedure_name:
        st.warning("Please enter both patient name and procedure name.")
    else:
        prompt = f"""
        You are a hospital documentation assistant. Write a NABH-style patient consent form in {language}
        for a patient named {patient_name} undergoing a procedure called {procedure_name}.
        Output only the consent form. Use medical language suitable for hospital records.
        """
        with st.spinner("Generating..."):
            try:
                response = model.generate_content(prompt)
                st.success("Consent Form Generated")
                st.text_area("Consent Form", response.text, height=400)
            except Exception as e:
                st.error(f"Error: {str(e)}")
