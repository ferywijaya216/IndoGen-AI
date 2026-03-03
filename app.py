import streamlit as st
import google.generativeai as genai
import json

# --- 1. KONFIGURASI ENGINE ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-3-flash-preview') 
    else:
        st.error("Credential Error: API Key tidak ditemukan.")
except Exception as e:
    st.error(f"Error: {e}")

# --- 2. THEME DESIGN (OPTIMAL & BERSIH) ---
st.set_page_config(page_title="IndoGen-AI | Clinical Portal", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    
    /* Hapus Tombol Geser Sidebar */
    [data-testid="sidebar-button-container"] { display: none !important; }

    .his-header {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 5px solid #3B82F6; margin-bottom: 20px;
    }

    /* Poin Data Pasien Awal */
    .patient-data-point {
        line-height: 1.1; margin-bottom: 0px; font-size: 0.95rem; color: #1E293B;
    }
    .label-bold { font-weight: 700; color: #1E3A8A; }

    /* Hasil Analisis Mewah & Rapi */
    .report-card { 
        background: white; padding: 35px; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #E2E8F0;
        line-height: 1.6; color: #334155; margin-bottom: 25px;
    }

    /* List Poin Identitas di Dalam Analisis */
    .analysis-info-list {
        list-style-type: none; padding: 0; margin-bottom: 20px;
        border-bottom: 1px solid #F1F5F9; padding-bottom: 15px;
    }
    .analysis-info-list li {
        font-size: 0.95rem; margin-bottom: 4px;
    }

    .stButton>button {
        background: #3B82F6; color: white; border-radius: 8px; font-weight: bold; width: 100%; height: 3em; border: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR (KONTROL KLINIS) ---
with st.sidebar:
    st.markdown("### **IndoGen-AI HIS**")
    try:
        with open('data_genetik.json', 'r') as f:
            db_genom = json.load(f)
        
        if 'run_ai' in st.session_state and st.session_state.run_ai:
            if st.button("Sesi Baru"):
                for key in list(st.session_state.keys()): del st.session_state[key]
                st.rerun()
            st.stop()

        selected_display = st.selectbox("Antrean Pasien (HIS):", [f"{p['nama']} - {p['nik']}" for p in db_genom])
        p_name = selected_display.split(" - ")[0]
        p = next(item for item in db_genom if item["nama"] == p_name)
        
        st.markdown("---")
        obat_input = st.text_input("Rencana Resep:")
        keluhan_input = st.text_area("Keluhan Utama:")
        
        if st.button("Analisa"):
            if not obat_input or not keluhan_input:
                st.error("Lengkapi data input.")
            else:
                st.session_state.run_ai = True
                st.session_state.current_p = p
                st.session_state.temp_obat = obat_input
                st.session_state.temp_keluhan = keluhan_input
    except Exception as e:
        st.error(f"Data Error: {e}")

# --- 4. DASHBOARD UTAMA (IDENTITAS AWAL) ---
st.markdown(f"""
<div class="his-header">
    <h2 style="margin:0; color:#1E3A8A; font-size:1.4rem;">Clinical Decision Support System</h2>
    <p style="margin:0; color:#64748B; font-size:0.85rem;">Integrasi Nasional Data Genomik BGSi</p>
</div>
""", unsafe_allow_html=True)

# Data Pasien Singkat
st.markdown(f"""
<div style="background:white; padding:18px; border-radius:15px; border:1px solid #E2E8F0; margin-bottom:20px;">
    <div class="patient-data-point"><span class="label-bold">Nama:</span> {p['nama']}</div>
    <div class="patient-data-point"><span class="label-bold">Diagnosis HIS:</span> {p['kondisi']}</div>
    <div class="patient-data-point"><span class="label-bold">TTV:</span> {p['ttv']['td']} mmHg | {p['ttv']['bb']} kg | {p['ttv']['tb']} cm</div>
    <div class="patient-data-point"><span class="label-bold">Data Genetik (RSID):</span> {p['rsid']}</div>
</div>
""", unsafe_allow_html=True)

# --- 5. OUTPUT ANALISA & VALIDASI ---
if 'run_ai' in st.session_state and st.session_state.run_ai:
    p_active = st.session_state.current_p
    
    if 'ai_result' not in st.session_state:
        with st.status("Memproses Analisa Genomik...", expanded=False):
            prompt = f"""
            Buat analisa medis untuk {p_active['nama']}. 
            Data Genetik: {p_active['rsid']}. Keluhan: {st.session_state.temp_keluhan}. Obat: {st.session_state.temp_obat}.
            Berikan poin analisa: Diagnosis Kerja (%), Farmakogenomik, dan Nutrigenomik.
            Ketentuan: Vancouver Style, Tanpa bold (**), Bahasa Medis Formal.
            """
            response = model.generate_content(prompt)
            st.session_state.ai_result = response.text.replace("**", "")

    # HASIL ANALISIS (Bagian Atas yang Dirapikan)
    st.markdown("### Analisis Rekam Medis (AI)")
    st.markdown(f"""
    <div class="report-card">
        <ul class="analysis-info-list">
            <li><b>Pasien:</b> {p_active['nama']}</li>
            <li><b>Genotipe:</b> {p_active['rsid']}</li>
            <li><b>Keluhan Utama:</b> {st.session_state.temp_keluhan}</li>
            <li><b>Terapi Farmakologi:</b> {st.session_state.temp_obat}</li>
        </ul>
        {st.session_state.ai_result}
    </div>
    """, unsafe_allow_html=True)

    # VALIDASI KLINIS (Hanya Penyakit dan Obat)
    st.markdown("---")
    st.markdown("### Validasi Klinis")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Diagnosis Final:", value=p_active['kondisi'])
    with col2:
        st.text_input("Resep Final:", value=st.session_state.temp_obat)
    
    if st.button("Simpan"):
        st.success("Data klinis telah diverifikasi dan disimpan.")

# --- 6. FOOTER ---
st.markdown("""
<div style="margin-top:40px; padding:15px; text-align:center; border-top:1px solid #E2E8F0; color:#94A3B8; font-size:0.7rem;">
    Powered by Gemini 3 Flash | Cloud AI Integration via Google Vertex API<br>
    IndoGen-AI Precision System © 2026
</div>
""", unsafe_allow_html=True)
