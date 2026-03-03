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

# --- 2. DESAIN UI (PRESISI & MEDIS) ---
st.set_page_config(page_title="IndoGen-AI | Portal Presisi", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    
    .his-header {
        background: white; padding: 25px; border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 5px solid #2563EB; margin-bottom: 20px;
    }

    /* Kotak Panduan Penggunaan */
    .instruction-step {
        background: #F0F9FF; border-radius: 8px; padding: 15px;
        border: 1px solid #BAE6FD; margin-bottom: 20px; color: #1E40AF; font-size: 0.85rem;
    }

    /* Poin Data Pasien (Rapat) */
    .patient-data-point { line-height: 1.2; margin-bottom: 0px; font-size: 0.95rem; color: #1E293B; }
    .label-bold { font-weight: 700; color: #1E3A8A; }

    /* Report Card Analisis */
    .report-card { 
        background: white; padding: 30px; border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #E2E8F0;
        line-height: 1.6; color: #334155; margin-bottom: 20px;
    }

    .analysis-info-list {
        margin: 0 0 20px 0; padding: 0; list-style: none;
        border-bottom: 2px solid #F1F5F9; padding-bottom: 15px;
    }
    .analysis-info-list li { font-size: 0.95rem; margin-bottom: 5px; color: #475569; }
    .analysis-info-list b { color: #1E3A8A; }

    .stButton>button {
        background: #2563EB; color: white; border-radius: 6px;
        font-weight: 600; width: 100%; height: 3em; border: none;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR (HIS KONTROL) ---
with st.sidebar:
    st.markdown("<h3 style='color:#1E3A8A; margin-top:-20px;'>IndoGen-AI HIS</h3>", unsafe_allow_html=True)
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
        
        if st.button("Analisis"):
            if not obat_input or not keluhan_input:
                st.error("Data wajib lengkap.")
            else:
                st.session_state.run_ai = True
                st.session_state.current_p = p
                st.session_state.temp_obat = obat_input
                st.session_state.temp_keluhan = keluhan_input
    except Exception as e:
        st.error(f"Error: {e}")

# --- 4. DASHBOARD UTAMA ---
st.markdown(f"""
<div class="his-header">
    <h2 style="margin:0; color:#1E3A8A; font-size:1.3rem;">Clinical Decision Support System</h2>
    <p style="margin:0; color:#64748B; font-size:0.8rem;">Integrasi Nasional Data Genomik BGSi</p>
</div>
""", unsafe_allow_html=True)

# PANDUAN PENGGUNAAN STATIS (Sesuai PUEBI)
if 'run_ai' not in st.session_state:
    st.markdown(f"""
    <div class="instruction-step">
        <b>Panduan Penggunaan Sistem:</b><br>
        Berikut adalah langkah pengoperasian sistem ini:<br>
        1. Pilih nama pasien pada kolom <b>Antrean Pasien</b>.<br>
        2. Masukkan nama obat pada kolom resep, misalnya: <b>'Karbamazepin'</b>.<br>
        3. Masukkan gejala pada kolom observasi, misalnya: <b>'Kejang'</b>.<br>
    </div>
    """, unsafe_allow_html=True)

# Data Pasien Singkat (Selalu muncul)
st.markdown(f"""
<div style="background:white; padding:15px; border-radius:12px; border:1px solid #E2E8F0; margin-bottom:20px;">
    <div class="patient-data-point"><span class="label-bold">Nama:</span> {p['nama']}</div>
    <div class="patient-data-point"><span class="label-bold">Diagnosis HIS:</span> {p['kondisi']}</div>
    <div class="patient-data-point"><span class="label-bold">TTV:</span> {p['ttv']['td']} mmHg | {p['ttv']['bb']} kg | {p['ttv']['tb']} cm</div>
    <div class="patient-data-point"><span class="label-bold">Data Genetik (RSID):</span> {p['rsid']}</div>
</div>
""", unsafe_allow_html=True)

# --- 5. OUTPUT ANALISIS & VALIDASI ---
if 'run_ai' in st.session_state and st.session_state.run_ai:
    p_active = st.session_state.current_p
    
    if 'ai_result' not in st.session_state:
        with st.spinner("Menjalankan Analisis Genomik..."):
            prompt = f"Berikan laporan analisis medis formal untuk {p_active['nama']}. Data Genetik: {p_active['rsid']}. Keluhan: {st.session_state.temp_keluhan}. Obat: {st.session_state.temp_obat}. Sertakan Diagnosis Kerja (%), Farmakogenomik, dan Nutrigenomik (gula merah/tebu kuning). Vancouver Style, Tanpa bold (**), Bahasa Medis Formal."
            try:
                response = model.generate_content(prompt)
                st.session_state.ai_result = response.text.replace("**", "")
            except Exception as e:
                st.error(f"AI Error: {e}")

    # Hasil Analisis
    st.markdown("### Hasil Analisis Sistem")
    st.markdown(f"""
    <div class="report-card">
        <ul class="analysis-info-list">
            <li><b>Pasien:</b> {p_active['nama']}</li>
            <li><b>Genotipe:</b> {p_active['rsid']}</li>
            <li><b>Keluhan:</b> {st.session_state.temp_keluhan}</li>
            <li><b>Terapi:</b> {st.session_state.temp_obat}</li>
        </ul>
        {st.session_state.ai_result}
    </div>
    """, unsafe_allow_html=True)

    # Konfirmasi Klinis
    st.markdown("---")
    st.markdown("### Konfirmasi Klinis")
    c1, c2 = st.columns(2)
    with c1: st.text_input("Diagnosis Final:", value=p_active['kondisi'])
    with c2: st.text_input("Resep Final:", value=st.session_state.temp_obat)
    
    if st.button("Simpan"):
        st.success("Data berhasil disimpan.")

# --- 6. FOOTER ---
st.markdown("""
<div style="margin-top:30px; padding:10px; text-align:center; color:#94A3B8; font-size:0.7rem; border-top:1px solid #E2E8F0;">
    IndoGen-AI Precision System © 2026 | Powered by Gemini 3 Flash
</div>
""", unsafe_allow_html=True)
