import streamlit as st
import google.generativeai as genai
import json
import time

# --- 1. KONFIGURASI ENGINE ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-3-flash-preview')
    else:
        st.error("Credential Error: API Key tidak ditemukan.")
except Exception as e:
    st.error(f"Error: {e}")

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="IndoGen-AI | Portal Presisi", layout="wide")

# --- LOAD MATERIAL ICON ---
st.markdown("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
""", unsafe_allow_html=True)

# --- FLOATING WINDOW (BISA DITUTUP) ---
st.markdown("""
<style>
.floating-warning {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 320px;
    background-color: #FEF3C7;
    color: #92400E;
    padding: 18px;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    font-size: 0.8rem;
    border-left: 5px solid #F59E0B;
    z-index: 9999;
}
.close-btn {
    position: absolute;
    top: 8px;
    right: 10px;
    cursor: pointer;
    font-weight: bold;
}
</style>

<div id="floatingBox" class="floating-warning">
    <span class="close-btn" onclick="document.getElementById('floatingBox').style.display='none'">✕</span>
    <b>Informasi Sistem</b><br><br>
    Sistem ini menggunakan layanan Google Gemini Free Tier.
    Layanan memiliki batasan kuota API dan dapat mengalami kepadatan trafik.
    Apabila terjadi keterlambatan analisis, silakan mencoba kembali beberapa saat kemudian.
</div>
""", unsafe_allow_html=True)

# --- 3. DESAIN UI (ASLI ANDA) ---
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
.instruction-step {
    background: #F0F9FF; border-radius: 8px; padding: 15px;
    border: 1px solid #BAE6FD; margin-bottom: 20px; color: #1E40AF; font-size: 0.85rem;
}
.patient-data-point { font-size: 0.95rem; color: #1E293B; }
.label-bold { font-weight: 700; color: #1E3A8A; }
.report-card { 
    background: white; padding: 30px; border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    border: 1px solid #E2E8F0;
    line-height: 1.6; color: #334155;
}
</style>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h3 style='color:#1E3A8A;'>IndoGen-AI HIS</h3>", unsafe_allow_html=True)

    with open('data_genetik.json', 'r') as f:
        db_genom = json.load(f)

    selected_display = st.selectbox(
        "Antrean Pasien (HIS):",
        [f"{p['nama']} - {p['nik']}" for p in db_genom]
    )

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

# --- 5. HEADER ---
st.markdown("""
<div class="his-header">
<h2 style="margin:0;">Clinical Decision Support System 
<span class="material-icons" style="vertical-align:middle;">keyboard_double_arrow_right</span>
</h2>
<p style="margin:0;">Integrasi Nasional Data Genomik BGSi</p>
</div>
""", unsafe_allow_html=True)

# --- 6. PANDUAN PENGGUNAAN (TIDAK DIHAPUS) ---
if 'run_ai' not in st.session_state:
    st.markdown("""
    <div class="instruction-step">
        <b>Panduan Penggunaan Sistem:</b><br>
        Berikut adalah langkah pengoperasian sistem ini:<br>
        1. Pilih nama pasien pada kolom <b>Antrean Pasien</b>.<br>
        2. Masukkan nama obat pada kolom resep, misalnya: <b>'Karbamazepin'</b>.<br>
        3. Masukkan gejala pada kolom observasi, misalnya: <b>'Kejang'</b>.<br>
    </div>
    """, unsafe_allow_html=True)

# --- 7. DATA PASIEN ---
st.markdown(f"""
<div style="background:white; padding:15px; border-radius:12px; border:1px solid #E2E8F0; margin-bottom:20px;">
<div class="patient-data-point"><span class="label-bold">Nama:</span> {p['nama']}</div>
<div class="patient-data-point"><span class="label-bold">Diagnosis HIS:</span> {p['kondisi']}</div>
<div class="patient-data-point"><span class="label-bold">TTV:</span> {p['ttv']['td']} mmHg | {p['ttv']['bb']} kg | {p['ttv']['tb']} cm</div>
<div class="patient-data-point"><span class="label-bold">Data Genetik (RSID):</span> {p['rsid']}</div>
</div>
""", unsafe_allow_html=True)

# --- 8. ANALISIS AI (STABIL, TANPA 600 DETIK) ---
if 'run_ai' in st.session_state and st.session_state.run_ai:

    if 'ai_result' not in st.session_state:
        with st.spinner("Menjalankan Analisis Genomik..."):
            prompt = f"""
Berikan laporan analisis medis formal untuk {p['nama']}.
Data Genetik: {p['rsid']}.
Keluhan: {st.session_state.temp_keluhan}.
Obat: {st.session_state.temp_obat}.
Sertakan Diagnosis Kerja (%), Farmakogenomik, dan Nutrigenomik (gula merah/tebu kuning).
Vancouver Style, tanpa bold (**), bahasa medis formal.
"""

            MAX_RETRY = 2
            RETRY_DELAY = 3
            response_text = None

            for attempt in range(MAX_RETRY):
                try:
                    response = model.generate_content(
                        prompt,
                        request_options={"timeout": 60}
                    )

                    if response and hasattr(response, "text") and response.text:
                        response_text = response.text.replace("**", "")
                        break

                except Exception:
                    if attempt < MAX_RETRY - 1:
                        time.sleep(RETRY_DELAY)
                    else:
                        st.error("Sistem AI sedang mengalami kepadatan trafik. Silakan coba kembali.")
                        st.session_state.run_ai = False

            if response_text:
                st.session_state.ai_result = response_text

    if 'ai_result' in st.session_state:
        st.markdown("### Hasil Analisis Sistem")
        st.markdown(f"""
        <div class="report-card">
        {st.session_state.ai_result}
        </div>
        """, unsafe_allow_html=True)

# --- 9. FOOTER ---
st.markdown("""
<div style="margin-top:30px; padding:10px; text-align:center; color:#94A3B8; font-size:0.7rem; border-top:1px solid #E2E8F0;">
IndoGen-AI Precision System © 2026 | Powered by Gemini 3 Flash
</div>
""", unsafe_allow_html=True)
