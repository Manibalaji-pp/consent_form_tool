import streamlit as st
import google.generativeai as genai
from datetime import datetime
import re

# --- CONFIGURATION & SECURITY ---

# Configure the Gemini API Key using Streamlit's secrets management
# Make sure you have a .streamlit/secrets.toml file with your API key
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except (FileNotFoundError, KeyError):
    st.error("🚨 Gemini API Key not found! Please add it to your Streamlit secrets.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Consent Form Generator",
    page_icon="📄",
    layout="centered"
)

# --- STYLING ---

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .form-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .consent-form {
        background-color: white;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button {
        background-color: #2E86AB;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        font-size: 1.1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #1e5f7a;
    }
</style>
""", unsafe_allow_html=True)


# --- HELPER FUNCTIONS ---

def validate_inputs(name, age, consent_title, diagnosis, hospital):
    """Validate user inputs before calling the API"""
    errors = []
    
    if not name.strip() or len(name.strip()) < 2:
        errors.append("Patient name must be at least 2 characters long")
    
    if not age.strip() or not age.isdigit() or not (0 < int(age) <= 150):
        errors.append("Please enter a valid age (1-150)")
    
    if not consent_title.strip() or len(consent_title.strip()) < 3:
        errors.append("Consent form title is required (min 3 characters)")
        
    if not diagnosis.strip() or len(diagnosis.strip()) < 3:
        errors.append("Patient diagnosis is required (min 3 characters)")
    
    if not hospital.strip() or len(hospital.strip()) < 3:
        errors.append("Hospital name is required (min 3 characters)")
    
    return errors

# --- UI COMPONENTS ---

st.markdown('<h1 class="main-header">📝 Consent Form Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Generate and edit professional patient consent forms compliant with NABH standards using AI</p>', unsafe_allow_html=True)

# Create columns for patient information
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.subheader("👤 Patient Information")
    name = st.text_input("Patient Name:", placeholder="Enter full patient name")
    age = st.text_input("Age:", placeholder="Enter patient age")
    gender = st.selectbox("Gender:", ["Male", "Female", "Other", "Prefer not to say"])
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.subheader("🏥 Medical Information")
    # CHANGED: 'Procedure' is now 'Consent Form Title'
    consent_title = st.text_input("Consent Form Title:", placeholder="e.g., Informed Consent for Surgery")
    # ADDED: New 'Diagnosis' field
    diagnosis = st.text_input("Patient Diagnosis:", placeholder="e.g., Acute Appendicitis")
    hospital = st.text_input("Hospital/Clinic Name:", placeholder="Enter hospital name")
    date = st.date_input("Consent Date:", value=datetime.now().date())
    st.markdown('</div>', unsafe_allow_html=True)

# Language and Options
st.markdown('<div class="form-section">', unsafe_allow_html=True)
st.subheader("🌐 Language & Options")

col3, col4 = st.columns([1, 1])
with col3:
    language = st.selectbox(
        "Select Language:",
        ["English", "Hindi", "Tamil", "Telugu", "Malayalam", "Kannada", "Marathi", "Bengali", "Gujarati"],
        help="Choose the language for the consent form"
    )

with col4:
    form_type = st.selectbox(
        "Form Complexity:",
        ["Standard", "Detailed", "Comprehensive"],
        help="Choose the level of detail for the consent form"
    )

st.subheader("📋 Form Sections to Include")
col5, col6 = st.columns([1, 1])
with col5:
    include_risks = st.checkbox("Include Risk Disclosure", value=True)
    include_alternatives = st.checkbox("Include Alternative Treatments", value=True)

with col6:
    include_emergency = st.checkbox("Include Emergency Contacts", value=True)
    include_witness = st.checkbox("Include Witness Section", value=True)

st.markdown('</div>', unsafe_allow_html=True)

# Optional additional information
with st.expander("👨‍⚕️ Additional Information (Optional)"):
    doctor_name = st.text_input("Attending Doctor Name:", placeholder="Dr. John Smith")
    department = st.text_input("Department:", placeholder="e.g., Cardiology, Surgery")
    contact_number = st.text_input("Hospital Contact Number:", placeholder="+91-XXXXXXXXXX")
    special_instructions = st.text_area("Special Instructions/Notes:", placeholder="e.g., Patient has a known allergy to...")

# --- GENERATION LOGIC ---

st.markdown("---")
col_center = st.columns([1, 2, 1])
with col_center[1]:
    generate_button = st.button("🚀 Generate NABH Consent Form", type="primary", use_container_width=True)

if generate_button:
    # Validate inputs with the new fields
    validation_errors = validate_inputs(name, age, consent_title, diagnosis, hospital)
    
    if validation_errors:
        st.error("❌ Please fix the following errors before generating:")
        for error in validation_errors:
            st.write(f"• {error}")
    else:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Create a more detailed and robust prompt
            prompt = f"""
            Task: Generate a professional patient consent form.
            Language: {language}
            Standards: NABH (National Accreditation Board for Hospitals & Healthcare Providers) and general Indian healthcare regulations.
            Form Title: "{consent_title}" (This should be the main heading of the document).
            
            PATIENT & CONTEXT:
            - Patient Name: {name}
            - Age: {age} years
            - Gender: {gender}
            - Diagnosis: {diagnosis}
            - Hospital/Facility: {hospital}
            - Date of Consent: {date.strftime('%d-%B-%Y')}
            """
            
            if doctor_name: prompt += f"- Attending Doctor: {doctor_name}\n"
            if department: prompt += f"- Department: {department}\n"

            prompt += f"""
            
            FORM REQUIREMENTS:
            1. Create a {form_type.lower()} consent form. The main heading of the document must be "{consent_title}" translated appropriately into {language}.
            2. Use clear, formal, and respectful language suitable for a patient.
            3. Structure the form with a proper hospital letterhead feel.
            
            MANDATORY SECTIONS:
            - Hospital/Clinic Header
            - A clear title: "{consent_title}" in {language}
            - Patient Identification
            - Introduction and Purpose of Consent
            - Explanation of the proposed procedure/treatment related to the diagnosis '{diagnosis}'.
            - Doctor/Medical Team Information
            """

            if include_risks: prompt += "- Detailed disclosure of potential risks, benefits, and complications.\n"
            if include_alternatives: prompt += "- Explanation of alternative treatment options and their risks/benefits.\n"
            if include_emergency: prompt += "- Section for Emergency Contact Information.\n"
            if include_witness: prompt += "- Section for a Witness signature.\n"

            prompt += """
            - Consent Declaration Statement (I, the undersigned, hereby consent...)
            - Patient Rights (including the right to revoke consent)
            - Signature section for Patient (or Guardian), Doctor, and Witness (if included).
            - Fields for Date and Time of signing.
            
            SPECIAL INSTRUCTIONS:
            - {special_instructions if special_instructions else "None"}
            
            Please generate the full text of the consent form now, ready for printing.
            """

            # Generate consent form using Gemini AI
            with st.spinner("🔄 Generating your AI-powered NABH-compliant consent form... Please wait."):
                response = model.generate_content(prompt)
                
                if response and response.text:
                    st.success("✅ AI-generated consent form created successfully!")
                    
                    st.markdown('<div class="consent-form">', unsafe_allow_html=True)
                    
                    # CHANGED: Dynamic subheader using the user's title
                    st.subheader(f"📋 Generated Form: {consent_title}")
                    st.markdown("---")
                    
                    # CHANGED: Content is now in an editable text area
                    st.info("You can review and edit the generated content below before downloading.")
                    edited_content = st.text_area(
                        label="Editable Consent Form Content", 
                        value=response.text, 
                        height=500,
                        label_visibility="collapsed"
                    )
                    
                    st.markdown('</div>', unsafe_allow_html=True)

                    # --- DOWNLOAD OPTIONS (using the edited content) ---
                    st.markdown("---")
                    st.subheader("📥 Download Your Edited Form")
                    
                    # Create a "safe" filename from the consent title
                    safe_title = re.sub(r'[^\w\s-]', '', consent_title).strip().replace(' ', '_')
                    filename = f"Consent_{safe_title}_{date.strftime('%Y%m%d')}.txt"

                    col_dl1, col_dl2 = st.columns(2)
                    
                    with col_dl1:
                        st.download_button(
                            label="📄 Download as Plain Text",
                            data=edited_content, # Use edited content
                            file_name=filename,
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col_dl2:
                        # Create a formatted version with a header
                        formatted_download_content = f"""
{'='*60}
AI-GENERATED NABH COMPLIANT CONSENT FORM
{'='*60}

Form Title: {consent_title}
Hospital: {hospital}
Patient: {name}
Diagnosis: {diagnosis}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

--- DOCUMENT START ---

{edited_content}

--- DOCUMENT END ---
{'='*60}
Generated by the Consent Form Generator using Google Gemini AI.
This document must be reviewed by legal and medical professionals before use.
{'='*60}
                        """
                        
                        st.download_button(
                            label="📋 Download with Header",
                            data=formatted_download_content, # Use edited content
                            file_name=f"Formatted_{filename}",
                            mime="text/plain",
                            use_container_width=True
                        )
                else:
                    st.error("❌ Failed to generate consent form. The AI response was empty. Please try again.")

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
            st.info("This might be due to API key issues, network problems, or service overload. Please check your API key in secrets.toml and try again later.")

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 2rem 0;'>
    <p><strong>⚠️ IMPORTANT DISCLAIMER:</strong> This tool is for reference purposes only. All generated forms must be reviewed and approved by qualified medical and legal professionals to ensure compliance with all local regulations and hospital policies.</p>
    <p style='margin-top: 1rem; font-size: 0.8rem;'>Powered by Google Gemini AI • App Version 2.1</p>
</div>
""", unsafe_allow_html=True)
