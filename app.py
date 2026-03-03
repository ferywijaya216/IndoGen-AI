import streamlit as st
import google.generativeai as genai
import json

# --- 1. CONFIG ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-3-flash-preview') 
    else:
        st.error("API Key missing.")
except Exception as e:
    st.error(f"AI Error: {e}")

# --- 2. THEME DESIGN (CLEAN WHITE MEDICAL) ---
st.set_page_config(page_title="IndoGen-AI | Clinical Portal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    .his-header {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-bottom: 4px solid #3B82F6; margin-bottom: 20px;
    }
    .patient-card {
        background: white; padding: 25px; border-radius: 15px;
        border: 1px solid #E2E8F0; margin-bottom: 20px;
    }
    .info-label { color: #64748B; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; }
    .info-value { color: #1E3A8A; font-size: 1.1rem; font-weight: 600; margin-bottom: 15px; }
    .report-card { 
        background: white; padding: 40px; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #E2E8F0;
    }
    .stButton>button {
        background: #3B82F6; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 3em;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR (PILIH PASIEN) ---
with st.sidebar:
    st.markdown("### **IndoGen-AI HIS**")
    try:
        with open('data_genetik.json', 'r') as f:
            db_genom = json.load(f)
        
        selected_display = st.selectbox("Antrean Pasien (HIS):", [f"{p['nama']} - {p['nik']}" for p in db_genom])
        p_name = selected_display.split(" - ")[0]
        p = next(item for item in db_genom if item["nama"] == p_name)
        
        st.markdown("---")
        obat = st.text_input("Rencana Resep:")
        keluhan = st.text_area("Keluhan Utama:")
        
        if st.button("Analisa"):
            st.session_state.run_ai = True
    except Exception as e:
        st.error(f"JSON Error: {e}")

# --- 4. DASHBOARD UTAMA (TAMPILAN POINT RAPI) ---
st.markdown(f"""
<div class="his-header">
    <h2 style="margin:0; color:#1E3A8A;">Clinical Decision Support System</h2>
</div>
""", unsafe_allow_html=True)

# Tampilan Data Pasien dalam Bentuk Point (Grid)
with st.container():
    st.markdown('<div class="patient-card">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f'<p class="info-label">Nama Pasien</p><p class="info-value">{p["nama"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-label">NIK</p><p class="info-value">{p["nik"]}</p>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<p class="info-label">Diagnosis HIS</p><p class="info-value">{p["kondisi"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-label">Data Genetik (RSID)</p><p class="info-value">{p["rsid"]}</p>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<p class="info-label">Tekanan Darah</p><p class="info-value">{p["ttv"]["td"]} mmHg</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-label">Nadi</p><p class="info-value">{p["ttv"]["n"]} x/mnt</p>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<p class="info-label">Berat Badan</p><p class="info-value">{p["ttv"]["bb"]} kg</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-label">Tinggi Badan</p><p class="info-value">{p["ttv"]["tb"]} cm</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. OUTPUT ANALISA ---
if 'run_ai' in st.session_state and st.session_state.run_ai:
    with st.spinner("Proses..."):
        prompt = f"""
        Pasien: {p['nama']} | TTV: {p['ttv']} | Genetik: {p['rsid']}
        Keluhan: {keluhan} | Obat: {obat}
        Tugas: Berikan analisa Diagnosis (%), Farmakogenomik, Nutrigenomik (sertakan gula merah/tebu kuning jika relevan), dan Paspor Genomik.
        Format: Vancouver Style. Bahasa Medis Formal.
        """
        try:
            response = model.generate_content(prompt)
            st.markdown(f'<div class="report-card">{response.text}</div>', unsafe_allow_html=True)
            if st.button("Reset"):
                del st.session_state.run_ai
                st.rerun()
        except Exception as e:
            st.error(f"AI Error: {e}")
