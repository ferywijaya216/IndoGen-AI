import streamlit as st
import google.generativeai as genai
import json

# --- 1. CORE ENGINE CONFIGURATION ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Menggunakan model Gemini 3 Flash untuk latensi rendah
        model = genai.GenerativeModel('gemini-3-flash-preview') 
    else:
        st.error("Credential Error: API Key is not configured.")
except Exception as e:
    st.error(f"System Error: {e}")

# --- 2. INTERNATIONAL MEDICAL UI DESIGN ---
st.set_page_config(page_title="IndoGen-AI | Precision Medicine Portal", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    
    /* Global Container */
    .his-header {
        background: white; padding: 30px; border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 6px solid #2563EB; margin-bottom: 25px;
    }

    .guide-box {
        background: #F1F5F9; padding: 20px; border-radius: 10px;
        border: 1px solid #E2E8F0; margin-bottom: 25px;
        font-size: 0.9rem; color: #475569;
    }

    .patient-card {
        background: white; padding: 30px; border-radius: 12px;
        border: 1px solid #E2E8F0; margin-bottom: 25px;
    }

    .info-label { color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .info-value { color: #0F172A; font-size: 1rem; font-weight: 500; margin-bottom: 15px; }

    /* Report Result Area */
    .clinical-report { 
        background: white; padding: 50px; border-radius: 12px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0; line-height: 1.6; color: #1E293B;
        white-space: pre-wrap;
    }

    .stButton>button {
        background: #2563EB; color: white; border-radius: 6px;
        font-weight: 600; width: 100%; height: 3.2em; border: none;
        transition: background 0.2s;
    }
    .stButton>button:hover { background: #1D4ED8; }

    /* Footer / Engine Info */
    .engine-footer {
        margin-top: 50px; padding: 20px; text-align: center;
        border-top: 1px solid #E2E8F0; color: #94A3B8; font-size: 0.75rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. NAVIGATION & INPUT CONTROL ---
with st.sidebar:
    st.markdown("<h2 style='color:#1E3A8A; font-size:1.2rem;'>System Control</h2>", unsafe_allow_html=True)
    try:
        with open('data_genetik.json', 'r') as f:
            db_genom = json.load(f)
        
        selected_display = st.selectbox("Select Patient Record:", [f"{p['nama']} - {p['nik']}" for p in db_genom])
        p_name = selected_display.split(" - ")[0]
        p = next(item for item in db_genom if item["nama"] == p_name)
        
        st.markdown("---")
        obat = st.text_input("Planned Prescription:", placeholder="e.g. Warfarin")
        keluhan = st.text_area("Clinical Observations:", placeholder="e.g. Occasional chest pain")
        
        if st.button("Analisa"):
            if not obat or not keluhan:
                st.error("Required: Please provide clinical data.")
            else:
                st.session_state.run_ai = True
        
        if st.button("Reset Session"):
            st.session_state.clear()
            st.rerun()

    except Exception as e:
        st.error(f"Database Sync Error: {e}")

# --- 4. CLINICAL DASHBOARD ---
st.markdown(f"""
<div class="his-header">
    <h1 style="margin:0; font-size:1.5rem; color:#0F172A;">Clinical Decision Support System</h1>
    <p style="margin:0; color:#64748B; font-size:0.9rem;">Precision Medicine Integration | BGSi National Data Exchange</p>
</div>
""", unsafe_allow_html=True)

# SIMULATION GUIDE FOR REVIEWERS
st.markdown(f"""
<div class="guide-box">
    <b>Instruction for System Review:</b><br>
    To evaluate genomic-clinical integration: (1) Select 'Luh Putu Astuti' from the sidebar. (2) Input 'Karbamazepin' in prescription. (3) Input 'Recurring seizures' in observations. (4) Execute 'Analisa' to trigger high-risk allele detection.
</div>
""", unsafe_allow_html=True)

# PATIENT PROFILE GRID
with st.container():
    st.markdown('<div class="patient-card">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<p class="info-label">Patient Name</p><p class="info-value">{p["nama"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-label">Identification (NIK)</p><p class="info-value">{p["nik"]}</p>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<p class="info-label">Primary Diagnosis</p><p class="info-value">{p["kondisi"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-label">Genomic Marker (RSID)</p><p class="info-value">{p["rsid"]}</p>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<p class="info-label">Blood Pressure</p><p class="info-value">{p["ttv"]["td"]} mmHg</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-label">Heart Rate</p><p class="info-value">{p["ttv"]["n"]} bpm</p>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<p class="info-label">Weight</p><p class="info-value">{p["ttv"]["bb"]} kg</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-label">Height</p><p class="info-value">{p["ttv"]["tb"]} cm</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. CLINICAL REPORT OUTPUT ---
if 'run_ai' in st.session_state and st.session_state.run_ai:
    with st.spinner("Processing clinical and genomic datasets..."):
        # Prompt disesuaikan untuk menghasilkan teks murni profesional tanpa Markdown bold berlebih
        prompt = f"""
        Analyze the following clinical case:
        Patient: {p['nama']}
        Vital Signs: {p['ttv']}
        Genomic Profile: {p['rsid']}
        Clinical Diagnosis: {p['kondisi']}
        Current Complaint: {keluhan}
        Proposed Medication: {obat}

        Report requirements:
        1. Differential Diagnosis & Probability (%)
        2. Pharmacogenomic Analysis (Drug-Gene Interaction)
        3. Nutrigenomic Strategy (Include cane sugar or palm sugar only if metabolically relevant)
        4. Genomic Passport (Long-term preventive measures)

        Style: Formal Medical Report. No bold markers (**). Use Vancouver Citation Style.
        """
        try:
            response = model.generate_content(prompt)
            # Menghilangkan tanda bold (**) jika AI masih menghasilkannya
            clean_text = response.text.replace("**", "")
            st.markdown(f'<div class="clinical-report">{clean_text}</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Analysis Interrupted: {e}")

# --- 6. FOOTER ENGINE INFO ---
st.markdown("""
<div class="engine-footer">
    Powered by Gemini 3 Flash Cognitive Engine | Advanced Clinical Integration via Google Cloud Vertex AI API<br>
    IndoGen-AI Precision System v2.1.0 © 2026
</div>
""", unsafe_allow_html=True)
