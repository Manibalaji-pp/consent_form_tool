import streamlit as st
import os
from google import genai
from google.genai import types
from datetime import datetime
import re

# --- CONFIGURATION & SECURITY ---

# Configure the Gemini API Key using environment variables with fallback
try:
    # First try environment variable, then Streamlit secrets
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY and hasattr(st, 'secrets') and "GEMINI_API_KEY" in st.secrets:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    
    if not GEMINI_API_KEY:
        st.error("🚨 Gemini API Key not found! Please add it to your environment variables.")
        st.stop()
    
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"🚨 Gemini API Key configuration failed! Error: {str(e)}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="NABH Consent Form Generator",
    page_icon="📄",
    layout="centered"
)

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

# Helper functions
def validate_inputs(name, age, diagnosis, hospital, consent_title):
    """Validate user inputs"""
    errors = []
    
    if not name.strip():
        errors.append("Patient name is required")
    elif len(name.strip()) < 2:
        errors.append("Patient name must be at least 2 characters long")
    
    if not age.strip():
        errors.append("Age is required")
    elif not age.isdigit() or int(age) <= 0 or int(age) > 150:
        errors.append("Please enter a valid age (1-150)")
    
    if not diagnosis.strip():
        errors.append("Diagnosis is required")
    elif len(diagnosis.strip()) < 3:
        errors.append("Diagnosis must be at least 3 characters long")
    
    if not hospital.strip():
        errors.append("Hospital name is required")
    elif len(hospital.strip()) < 3:
        errors.append("Hospital name must be at least 3 characters long")
    
    if not consent_title.strip():
        errors.append("Consent title is required")
    elif len(consent_title.strip()) < 5:
        errors.append("Consent title must be at least 5 characters long")
    
    return errors

# UI Title and Description
st.markdown('<h1 class="main-header">📝 NABH Consent Form Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Generate professional patient consent forms compliant with NABH standards using AI</p>', unsafe_allow_html=True)

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
    consent_title = st.text_input("Consent Title:", placeholder="e.g., Informed Consent for Surgical Procedure")
    diagnosis = st.text_input("Diagnosis:", placeholder="Enter medical diagnosis")
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

# Additional options
st.subheader("📋 Form Sections")
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
    department = st.text_input("Department:", placeholder="e.g., Cardiology, Surgery, General Medicine")
    contact_number = st.text_input("Hospital Contact Number:", placeholder="+91-XXXXXXXXXX")
    special_instructions = st.text_area("Special Instructions/Notes:", placeholder="Any specific instructions or notes")

# Generate button
st.markdown("---")
col_center = st.columns([1, 2, 1])
with col_center[1]:
    generate_button = st.button("🚀 Generate NABH Consent Form", type="primary", use_container_width=True)

# Generation logic
if generate_button:
    # Validate inputs
    validation_errors = validate_inputs(name, age, diagnosis, hospital, consent_title)
    
    if validation_errors:
        st.error("❌ Please fix the following errors:")
        for error in validation_errors:
            st.write(f"• {error}")
    else:
        try:
            # Create comprehensive prompt
            prompt = f"""
            Generate a clean, professional patient consent form in {language} language following NABH (National Accreditation Board for Hospitals & Healthcare Providers) standards and Indian healthcare regulations.

            FORMATTING REQUIREMENTS:
            1. Start with the consent title "{consent_title}" in BOLD as the main heading (use HTML: <b>{consent_title}</b>)
            2. NO letterhead or decorative headers - keep it clean and simple
            3. Use standard medical consent form layout with HTML formatting
            4. Clear section divisions with appropriate spacing
            5. Professional medical terminology appropriate for {language}
            6. Use <b></b> tags for all bold text, ensuring content inside appears as bold font
            7. Make sure all text within <b></b> tags displays as actual bold formatting

            PATIENT DETAILS:
            - Patient Name: {name}
            - Age: {age} years
            - Gender: {gender}
            - Medical Diagnosis: {diagnosis}
            - Hospital/Healthcare Facility: {hospital}
            - Date of Consent: {date}
            """
            
            if doctor_name:
                prompt += f"- Attending Doctor: {doctor_name}\n"
            if department:
                prompt += f"- Department/Specialty: {department}\n"
            if contact_number:
                prompt += f"- Hospital Contact: {contact_number}\n"

            prompt += f"""

            STRUCTURE AND CONTENT:
            1. Bold heading with consent title using <b></b> tags - ensure content displays as bold font
            2. Patient identification section (clean format)
            3. Medical diagnosis and treatment explanation
            4. {form_type.lower()} level of detail as requested
            5. Clear, respectful language culturally appropriate for {language}
            6. NABH compliant sections per Indian healthcare standards
            7. Use <b></b> HTML tags for ALL headings and important text to make them bold font
            8. Any text inside <b>content</b> should display as actual bold formatting
            
            MANDATORY SECTIONS TO INCLUDE:
            - Patient identification details (no letterhead)
            - Medical diagnosis and related information
            - Doctor/medical team information
            - Clear consent declaration statements
            - Patient rights and responsibilities
            """

            if include_risks:
                prompt += "- Risk disclosure and potential complications\n"
            if include_alternatives:
                prompt += "- Alternative treatment options available\n"
            if include_emergency:
                prompt += "- Emergency contact information\n"
            if include_witness:
                prompt += "- Witness signature section\n"

            prompt += """
            - Signature lines for patient, doctor, and witness
            - Date and time fields
            - Legal disclaimers as per NABH standards
            
            FORMATTING GUIDELINES:
            - Use clean, standard medical form layout with HTML formatting
            - No decorative elements or letterheads
            - Bold main heading and section headings using <b></b> tags
            - Professional spacing between sections
            - Clear signature lines with labels
            - Easy to read and understand format
            - Compliance with Patient Rights Charter
            - Include consent revocation rights
            - IMPORTANT: Use <b></b> HTML tags for bold text, never use ** markdown
            """

            if special_instructions:
                prompt += f"- Special Instructions: {special_instructions}\n"

            prompt += """
            
            Generate a standard, clean consent form suitable for official medical use.
            Focus on clarity, legal compliance, and professional appearance.
            Remove all unnecessary decorative elements and keep the format simple and standard.
            Use HTML <b></b> tags for the consent title and all section headings to make them bold.
            Never use markdown ** for bold formatting - only use HTML <b></b> tags.
            
            CRITICAL: Ensure all text within <b>content</b> tags displays as actual bold font formatting.
            Example: <b>Consent Title</b> should show "Consent Title" in bold font.
            Example: <b>Patient Information</b> should show "Patient Information" in bold font.
            """

            # Generate consent form using Gemini AI
            with st.spinner("🔄 Generating your AI-powered NABH-compliant consent form... Please wait."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                if response and response.text:
                    st.success("✅ AI-generated consent form created successfully!")
                    
                    # Display the generated form
                    st.markdown('<div class="consent-form">', unsafe_allow_html=True)
                    st.subheader("📋 AI-Generated NABH Consent Form")
                    st.markdown("---")
                    
                    # Display the consent form content with HTML formatting enabled
                    st.markdown(response.text, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Create download options
                    st.markdown("---")
                    st.subheader("📥 Download Options")
                    
                    # Create filename
                    safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
                    safe_title = re.sub(r'[^\w\s-]', '', consent_title).strip().replace(' ', '_')
                    filename = f"NABH_Consent_Form_{safe_name}_{safe_title}_{date.strftime('%Y%m%d')}.txt"

                    col_dl1, col_dl2 = st.columns(2)
                    
                    with col_dl1:
                        st.download_button(
                            label="📄 Download as Text File",
                            data=response.text,
                            file_name=filename,
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col_dl2:
                        # Create formatted version with header
                        formatted_content = f"""
{"="*60}
AI-GENERATED NABH COMPLIANT CONSENT FORM
{"="*60}

Consent Title: {consent_title}
Hospital: {hospital}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Patient: {name}
Diagnosis: {diagnosis}
Language: {language}
Form Type: {form_type}

{response.text}

{"="*60}
Generated by Google Gemini AI
End of Document
{"="*60}
                        """
                        
                        st.download_button(
                            label="📋 Download Formatted Version",
                            data=formatted_content,
                            file_name=f"Formatted_{filename}",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    # Additional information and disclaimer
                    st.info(f"""
                    💡 **AI Generation Successful:**
                    - **Consent Title:** {consent_title}
                    - **Language:** {language}
                    - **Complexity:** {form_type}
                    - **AI Model:** Google Gemini 2.5 Flash
                    - **Sections Included:** {', '.join([
                        'Risk Disclosure' if include_risks else '',
                        'Alternative Treatments' if include_alternatives else '',
                        'Emergency Contacts' if include_emergency else '',
                        'Witness Section' if include_witness else ''
                    ]).strip(', ') or 'Basic sections only'}
                    
                    **Important Notes:**
                    - This form was generated using Google Gemini AI
                    - Please review the generated form carefully before use
                    - Have it verified by your hospital's legal an's the complete, updated code for your NABH Consent Form Generator:

```python
import streamlit as st
import os
from google import genai
from google.genai import types
from datetime import datetime
import re

# --- CONFIGURATION & SECURITY ---

# Configure the Gemini API Key using environment variables with fallback
try:
    # First try environment variable, then Streamlit secrets
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY and hasattr(st, 'secrets') and "GEMINI_API_KEY" in st.secrets:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    
    if not GEMINI_API_KEY:
        st.error("🚨 Gemini API Key not found! Please add it to your environment variables.")
        st.stop()
    
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"🚨 Gemini API Key configuration failed! Error: {str(e)}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="NABH Consent Form Generator",
    page_icon="📄",
    layout="centered"
)

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

# Helper functions
def validate_inputs(name, age, diagnosis, hospital, consent_title):
    """Validate user inputs"""
    errors = []
    
    if not name.strip():
        errors.append("Patient name is required")
    elif len(name.strip()) < 2:
        errors.append("Patient name must be at least 2 characters long")
    
    if not age.strip():
        errors.append("Age is required")
    elif not age.isdigit() or int(age) <= 0 or int(age) > 150:
        errors.append("Please enter a valid age (1-150)")
    
    if not diagnosis.strip():
        errors.append("Diagnosis is required")
    elif len(diagnosis.strip()) < 3:
        errors.append("Diagnosis must be at least 3 characters long")
    
    if not hospital.strip():
        errors.append("Hospital name is required")
    elif len(hospital.strip()) < 3:
        errors.append("Hospital name must be at least 3 characters long")
    
    if not consent_title.strip():
        errors.append("Consent title is required")
    elif len(consent_title.strip()) < 5:
        errors.append("Consent title must be at least 5 characters long")
    
    return errors

# UI Title and Description
st.markdown('<h1 class="main-header">📝 NABH Consent Form Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Generate professional patient consent forms compliant with NABH standards using AI</p>', unsafe_allow_html=True)

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
    consent_title = st.text_input("Consent Title:", placeholder="e.g., Informed Consent for Surgical Procedure")
    diagnosis = st.text_input("Diagnosis:", placeholder="Enter medical diagnosis")
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

# Additional options
st.subheader("📋 Form Sections")
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
    department = st.text_input("Department:", placeholder="e.g., Cardiology, Surgery, General Medicine")
    contact_number = st.text_input("Hospital Contact Number:", placeholder="+91-XXXXXXXXXX")
    special_instructions = st.text_area("Special Instructions/Notes:", placeholder="Any specific instructions or notes")

# Generate button
st.markdown("---")
col_center = st.columns([1, 2, 1])
with col_center[1]:
    generate_button = st.button("🚀 Generate NABH Consent Form", type="primary", use_container_width=True)

# Generation logic
if generate_button:
    # Validate inputs
    validation_errors = validate_inputs(name, age, diagnosis, hospital, consent_title)
    
    if validation_errors:
        st.error("❌ Please fix the following errors:")
        for error in validation_errors:
            st.write(f"• {error}")
    else:
        try:
            # Create comprehensive prompt
            prompt = f"""
            Generate a clean, professional patient consent form in {language} language following NABH (National Accreditation Board for Hospitals & Healthcare Providers) standards and Indian healthcare regulations.

            FORMATTING REQUIREMENTS:
            1. Start with the consent title "{consent_title}" in BOLD as the main heading (use HTML: <b>{consent_title}</b>)
            2. NO letterhead or decorative headers - keep it clean and simple
            3. Use standard medical consent form layout with HTML formatting
            4. Clear section divisions with appropriate spacing
            5. Professional medical terminology appropriate for {language}
            6. Use <b></b> tags for all bold text, ensuring content inside appears as bold font
            7. Make sure all text within <b></b> tags displays as actual bold formatting

            PATIENT DETAILS:
            - Patient Name: {name}
            - Age: {age} years
            - Gender: {gender}
            - Medical Diagnosis: {diagnosis}
            - Hospital/Healthcare Facility: {hospital}
            - Date of Consent: {date}
            """
            
            if doctor_name:
                prompt += f"- Attending Doctor: {doctor_name}\n"
            if department:
                prompt += f"- Department/Specialty: {department}\n"
            if contact_number:
                prompt += f"- Hospital Contact: {contact_number}\n"

            prompt += f"""

            STRUCTURE AND CONTENT:
            1. Bold heading with consent title using <b></b> tags - ensure content displays as bold font
            2. Patient identification section (clean format)
            3. Medical diagnosis and treatment explanation
            4. {form_type.lower()} level of detail as requested
            5. Clear, respectful language culturally appropriate for {language}
            6. NABH compliant sections per Indian healthcare standards
            7. Use <b></b> HTML tags for ALL headings and important text to make them bold font
            8. Any text inside <b>content</b> should display as actual bold formatting
            
            MANDATORY SECTIONS TO INCLUDE:
            - Patient identification details (no letterhead)
            - Medical diagnosis and related information
            - Doctor/medical team information
            - Clear consent declaration statements
            - Patient rights and responsibilities
            """

            if include_risks:
                prompt += "- Risk disclosure and potential complications\n"
            if include_alternatives:
                prompt += "- Alternative treatment options available\n"
            if include_emergency:
                prompt += "- Emergency contact information\n"
            if include_witness:
                prompt += "- Witness signature section\n"

            prompt += """
            - Signature lines for patient, doctor, and witness
            - Date and time fields
            - Legal disclaimers as per NABH standards
            
            FORMATTING GUIDELINES:
            - Use clean, standard medical form layout with HTML formatting
            - No decorative elements or letterheads
            - Bold main heading and section headings using <b></b> tags
            - Professional spacing between sections
            - Clear signature lines with labels
            - Easy to read and understand format
            - Compliance with Patient Rights Charter
            - Include consent revocation rights
            - IMPORTANT: Use <b></b> HTML tags for bold text, never use ** markdown
            """

            if special_instructions:
                prompt += f"- Special Instructions: {special_instructions}\n"

            prompt += """
            
            Generate a standard, clean consent form suitable for official medical use.
            Focus on clarity, legal compliance, and professional appearance.
            Remove all unnecessary decorative elements and keep the format simple and standard.
            Use HTML <b></b> tags for the consent title and all section headings to make them bold.
            Never use markdown ** for bold formatting - only use HTML <b></b> tags.
            
            CRITICAL: Ensure all text within <b>content</b> tags displays as actual bold font formatting.
            Example: <b>Consent Title</b> should show "Consent Title" in bold font.
            Example: <b>Patient Information</b> should show "Patient Information" in bold font.
            """

            # Generate consent form using Gemini AI
            with st.spinner("🔄 Generating your AI-powered NABH-compliant consent form... Please wait."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                
                if response and response.text:
                    st.success("✅ AI-generated consent form created successfully!")
                    
                    # Display the generated form
                    st.markdown('<div class="consent-form">', unsafe_allow_html=True)
                    st.subheader("📋 AI-Generated NABH Consent Form")
                    st.markdown("---")
                    
                    # Display the consent form content with HTML formatting enabled
                    st.markdown(response.text, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Create download options
                    st.markdown("---")
                    st.subheader("📥 Download Options")
                    
                    # Create filename
                    safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
                    safe_title = re.sub(r'[^\w\s-]', '', consent_title).strip().replace(' ', '_')
                    filename = f"NABH_Consent_Form_{safe_name}_{safe_title}_{date.strftime('%Y%m%d')}.txt"

                    col_dl1, col_dl2 = st.columns(2)
                    
                    with col_dl1:
                        st.download_button(
                            label="📄 Download as Text File",
                            data=response.text,
                            file_name=filename,
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col_dl2:
                        # Create formatted version with header
                        formatted_content = f"""
{"="*60}
AI-GENERATED NABH COMPLIANT CONSENT FORM
{"="*60}

Consent Title: {consent_title}
Hospital: {hospital}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Patient: {name}
Diagnosis: {diagnosis}
Language: {language}
Form Type: {form_type}

{response.text}

{"="*60}
Generated by Google Gemini AI
End of Document
{"="*60}
                        """
                        
                        st.download_button(
                            label="📋 Download Formatted Version",
                            data=formatted_content,
                            file_name=f"Formatted_{filename}",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    # Additional information and disclaimer
                    st.info(f"""
                    💡 **AI Generation Successful:**
                    - **Consent Title:** {consent_title}
                    - **Language:** {language}
                    - **Complexity:** {form_type}
                    - **AI Model:** Google Gemini 2.5 Flash
                    - **Sections Included:** {', '.join([
                        'Risk Disclosure' if include_risks else '',
                        'Alternative Treatments' if include_alternatives else '',
                        'Emergency Contacts' if include_emergency else '',
                        'Witness Section' if include_witness else ''
                    ]).strip(', ') or 'Basic sections only'}
                    
                    **Important Notes:**
                    - This form was generated using Google Gemini AI
                    - Please review the generated form carefully before use
                    - Have it verified by your hospital's legal and medical team
                    - Ensure all local regulations and hospital policies are met
                    - Keep signed copies as per legal requirements
                    """)
                    
                    # Success metrics
                    st.success(f"✨ Professional consent form '{consent_title}' generated in {language} language using AI technology")
                    
                else:
                    st.error("❌ Failed to generate consent form. The AI response was empty.")

        except Exception as e:
            st.error(f"❌ An error occurred while generating the AI-powered consent form:")
            st.code(str(e))
            
            # Troubleshooting section
            st.markdown("### 🔧 Troubleshooting")
            st.info("""
            **Possible solutions:**
            1. **Network Issues:** Check your internet connection
            2. **Service Issues:** Try again after a few moments
            3. **API Limits:** The service might be temporarily unavailable
            
            **Contact Support:** If the problem persists, please contact technical support.
            """)

# Footer with important information
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 2rem 0;'>
    <p><strong>⚠️ IMPORTANT DISCLAIMER:</strong></p>
    <p>This tool generates AI-powered consent forms for reference purposes only. All generated forms must be:</p>
    <p>• Reviewed by qualified medical professionals<br>
    • Verified by legal experts<br>
    • Approved by hospital administration<br>
    • Compliant with local healthcare regulations</p>
    
    <p style='margin-top: 1rem;'>
    🏥 <strong>NABH Compliant</strong> • 🔒 <strong>Secure</strong> • 🌍 <strong>Multi-language</strong> • 🤖 <strong>AI-Powered</strong>
    </p>
    
    <p style='margin-top: 1rem; font-size: 0.8rem;'>
    Powered by Google Gemini AI • Version 2.1 • Last Updated: 2025
    </p>
</div>
""", unsafe_allow_html=True)
