import streamlit as st
import google.generativeai as genai
from datetime import datetime
import re

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
def validate_api_key(key):
    """Basic validation for Gemini API key format"""
    if not key:
        return False
    return len(key) > 20  # Basic length check

def validate_inputs(name, age, procedure, hospital):
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
    
    if not procedure.strip():
        errors.append("Procedure name is required")
    elif len(procedure.strip()) < 3:
        errors.append("Procedure name must be at least 3 characters long")
    
    if not hospital.strip():
        errors.append("Hospital name is required")
    elif len(hospital.strip()) < 3:
        errors.append("Hospital name must be at least 3 characters long")
    
    return errors

# UI Title and Description
st.markdown('<h1 class="main-header">📝 NABH Consent Form Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Generate professional patient consent forms compliant with NABH standards</p>', unsafe_allow_html=True)

# Main form layout
with st.container():
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    
    # API Key Section
    st.subheader("🔐 API Configuration")
    api_key = st.text_input(
        "Enter your Gemini API Key:",
        type="password",
        help="Get your API key from Google AI Studio (ai.google.dev)",
        placeholder="Enter your Gemini API key here"
    )
    
    if api_key and not validate_api_key(api_key):
        st.warning("⚠️ Please enter a valid Gemini API key")
    
    st.markdown('</div>', unsafe_allow_html=True)

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
    procedure = st.text_input("Medical Procedure/Treatment:", placeholder="Enter procedure name")
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
    validation_errors = validate_inputs(name, age, procedure, hospital)
    
    if not api_key:
        st.error("❌ Please enter your Gemini API key")
    elif not validate_api_key(api_key):
        st.error("❌ Please enter a valid Gemini API key")
    elif validation_errors:
        st.error("❌ Please fix the following errors:")
        for error in validation_errors:
            st.write(f"• {error}")
    else:
        try:
            # Configure Gemini API
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Create comprehensive prompt
            prompt = f"""
            Generate a professional patient consent form in {language} language following NABH (National Accreditation Board for Hospitals & Healthcare Providers) standards and Indian healthcare regulations.

            PATIENT DETAILS:
            - Patient Name: {name}
            - Age: {age} years
            - Gender: {gender}
            - Medical Procedure/Treatment: {procedure}
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

            FORM REQUIREMENTS:
            1. Generate a {form_type.lower()} consent form that is legally compliant
            2. Use formal medical terminology appropriate for {language}
            3. Include proper NABH format with hospital letterhead structure
            4. Make the language clear, respectful, and culturally appropriate
            5. Include all mandatory sections as per Indian healthcare standards
            
            MANDATORY SECTIONS TO INCLUDE:
            - Hospital/Clinic header information
            - Patient identification details
            - Procedure description and purpose
            - Doctor/medical team information
            - Consent declaration statements
            - Patient rights and responsibilities
            """

            if include_risks:
                prompt += "- Detailed risk disclosure and complications section\n"
            if include_alternatives:
                prompt += "- Alternative treatment options section\n"
            if include_emergency:
                prompt += "- Emergency contact information section\n"
            if include_witness:
                prompt += "- Witness signature section\n"

            prompt += """
            - Signature sections for patient, doctor, and witness
            - Date and time fields
            - Legal disclaimers as per NABH standards
            
            ADDITIONAL REQUIREMENTS:
            - Format the document with proper spacing and sections
            - Use professional medical language
            - Include fields for signatures and dates
            - Add appropriate legal disclaimers
            - Ensure compliance with Patient Rights Charter
            - Include revocation rights information
            """

            if special_instructions:
                prompt += f"- Special Instructions: {special_instructions}\n"

            prompt += """
            
            The consent form should be ready for printing and official use in a healthcare facility.
            Make it comprehensive but easy to understand for patients and their families.
            """

            # Generate consent form
            with st.spinner("🔄 Generating your NABH-compliant consent form... Please wait."):
                response = model.generate_content(prompt)
                
                if response and response.text:
                    st.success("✅ Consent form generated successfully!")
                    
                    # Display the generated form
                    st.markdown('<div class="consent-form">', unsafe_allow_html=True)
                    st.subheader("📋 Generated NABH Consent Form")
                    st.markdown("---")
                    
                    # Display the consent form content
                    st.markdown(response.text)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Create download options
                    st.markdown("---")
                    st.subheader("📥 Download Options")
                    
                    # Create filename
                    safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
                    filename = f"NABH_Consent_Form_{safe_name}_{date.strftime('%Y%m%d')}.txt"

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
NABH COMPLIANT CONSENT FORM
{"="*60}

Hospital: {hospital}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Patient: {name}
Procedure: {procedure}

{response.text}

{"="*60}
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
                    st.info("""
                    💡 **Important Notes:**
                    - Please review the generated form carefully before use
                    - Have it verified by your hospital's legal and medical team
                    - Ensure all local regulations and hospital policies are met
                    - Keep signed copies as per legal requirements
                    """)
                    
                    # Success metrics
                    st.success(f"✨ Form generated in {language} language with {form_type.lower()} complexity level")
                    
                else:
                    st.error("❌ Failed to generate consent form. The API response was empty.")

        except Exception as e:
            st.error(f"❌ An error occurred while generating the consent form:")
            st.code(str(e))
            
            # Troubleshooting section
            st.markdown("### 🔧 Troubleshooting")
            st.info("""
            **Possible solutions:**
            1. **API Key Issues:** Verify your Gemini API key is valid and active
            2. **Network Issues:** Check your internet connection
            3. **API Limits:** You might have reached your API quota limit
            4. **Service Issues:** Try again after a few moments
            
            **How to get a Gemini API Key:**
            1. Go to [Google AI Studio](https://ai.google.dev/)
            2. Sign in with your Google account
            3. Create a new API key
            4. Copy and paste it in the field above
            """)

# Footer with important information
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 2rem 0;'>
    <p><strong>⚠️ IMPORTANT DISCLAIMER:</strong></p>
    <p>This tool generates consent forms for reference purposes only. All generated forms must be:</p>
    <p>• Reviewed by qualified medical professionals<br>
    • Verified by legal experts<br>
    • Approved by hospital administration<br>
    • Compliant with local healthcare regulations</p>
    
    <p style='margin-top: 1rem;'>
    🏥 <strong>NABH Compliant</strong> • 🔒 <strong>Secure</strong> • 🌍 <strong>Multi-language</strong> • ⚡ <strong>AI-Powered</strong>
    </p>
    
    <p style='margin-top: 1rem; font-size: 0.8rem;'>
    Generated using Google Gemini AI • Version 2.0 • Last Updated: 2024
    </p>
</div>
""", unsafe_allow_html=True)
