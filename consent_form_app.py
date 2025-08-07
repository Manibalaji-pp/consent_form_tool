import streamlit as st
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="Consent Form Generator",
    page_icon="📄",
    layout="centered"
)

# UI Title
st.title("📝 NABH Consent Form Generator")
st.write("This tool generates a patient consent form in the selected language.")

# API Key
api_key = st.text_input("Enter your Gemini API Key:", type="password")

# Language selection
language = st.selectbox("Select Language:", ["English", "Tamil", "Telugu", "Malayalam", "Kannada", "Marathi", "Bhojpuri", "Bengali"])

# Patient details
name = st.text_input("Patient Name:")
age = st.text_input("Age:")
gender = st.selectbox("Gender:", ["Male", "Female", "Other"])
procedure = st.text_input("Procedure Name:")
hospital = st.text_input("Hospital Name:")
date = st.date_input("Consent Date:")

# Button
if st.button("Generate Consent Form"):
    if all([api_key, name, age, gender, procedure, hospital]):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        Generate a patient consent form in {language} using the NABH format.
        Patient name: {name}
        Age: {age}
        Gender: {gender}
        Procedure: {procedure}
        Hospital: {hospital}
        Date: {date}
        The content should be formal, clear, and culturally appropriate.
        """

        with st.spinner("Generating..."):
            try:
                response = model.generate_content(prompt)
                st.subheader("Generated Consent Form:")
                st.write(response.text)

                # Download button
                st.download_button(
                    label="📥 Download Consent Form",
                    data=response.text,
                    file_name="consent_form.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please fill in all fields and enter your Gemini API key.")
