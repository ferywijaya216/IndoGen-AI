import streamlit as st
import google.generativeai as genai
import json

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="IndoGen-AI", layout="wide")

# ==============================
# LOAD JSON DATA
# ==============================
with open("data_genetik.json", "r", encoding="utf-8") as f:
    patients = json.load(f)

# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("IndoGen-AI")

patient_names = [f"{p['nama']} - {p['nik']}" for p in patients]

selected_label = st.sidebar.selectbox(
    "Antrean Pasien (HIS):",
    patient_names
)

selected_index = patient_names.index(selected_label)
selected_patient = patients[selected_index]

resep = st.sidebar.text_input("Rencana Resep:")
keluhan = st.sidebar.text_area("Keluhan Utama:")
analisis_btn = st.sidebar.button("Analisis")

# ==============================
# HEADER (TIDAK DIUBAH)
# ==============================
st.markdown("""
<div style="
    background-color:#F4F6FA;
    padding:30px;
    border-radius:15px;
    border-left:6px solid #2E6BE6;">
    <h1 style="margin-bottom:5px;">Clinical Decision Support System</h1>
    <p>Integrasi Nasional Data Genomik BGSi</p>
</div>
""", unsafe_allow_html=True)

# ==============================
# PANDUAN (TIDAK DIHAPUS)
# ==============================
if 'run_ai' not in st.session_state:
    st.markdown("""
    <div style="
        background-color:#EAF2FF;
        padding:20px;
        border-radius:10px;
        margin-top:20px;">
        <b>Panduan Penggunaan Sistem:</b><br>
        Berikut adalah langkah pengoperasian sistem ini:<br>
        1. Pilih nama pasien pada kolom <b>Antrean Pasien</b>.<br>
        2. Masukkan nama obat pada kolom resep, misalnya: <b>'Karbamazepin'</b>.<br>
        3. Masukkan gejala pada kolom observasi, misalnya: <b>'Kejang'</b>.
    </div>
    """, unsafe_allow_html=True)

# ==============================
# DATA PASIEN (DINAMIS DARI JSON)
# ==============================
st.markdown(f"""
<div style="
    background-color:white;
    padding:20px;
    border-radius:15px;
    margin-top:20px;">
    <b>Nama:</b> {selected_patient['nama']}<br>
    <b>Diagnosis HIS:</b> {selected_patient['kondisi']}<br>
    <b>TTV:</b> {selected_patient['ttv']['td']} mmHg | 
                {selected_patient['ttv']['bb']} kg | 
                {selected_patient['ttv']['tb']} cm | 
                Nadi {selected_patient['ttv']['n']} bpm<br>
    <b>Data Genetik (RSID):</b> {selected_patient['rsid']}
</div>
""", unsafe_allow_html=True)

# ==============================
# FLOATING WINDOW (X DI DALAM BOX)
# ==============================
if "hide_warning" not in st.session_state:
    st.session_state.hide_warning = False

if not st.session_state.hide_warning:

    close_btn = st.button("✕", key="close_warning")

    st.markdown("""
    <style>
    .floating-box {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 360px;
        background-color: #FEF3C7;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        border-left: 6px solid #F59E0B;
        z-index: 9999;
    }
    .floating-title {
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="floating-box">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="floating-title">Informasi Sistem</div>
        </div>
        Sistem ini menggunakan layanan Google Gemini Free Tier.
        Layanan memiliki batasan kuota API dan dapat mengalami kepadatan trafik.
        Apabila terjadi keterlambatan analisis,
        silakan mencoba kembali beberapa saat kemudian.
    </div>
    """, unsafe_allow_html=True)

    if close_btn:
        st.session_state.hide_warning = True
        st.rerun()

# ==============================
# ANALISIS GEMINI (TIDAK DIUBAH STRUKTUR)
# ==============================
if analisis_btn and resep and keluhan:
    st.session_state.run_ai = True

    st.write("### Hasil Analisis AI")

    prompt = f"""
    Pasien: {selected_patient['nama']}
    Diagnosis: {selected_patient['kondisi']}
    RSID: {selected_patient['rsid']}
    Resep: {resep}
    Keluhan: {keluhan}

    Berikan analisis klinis berbasis farmakogenomik.
    """

    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        st.write(response.text)
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

# ==============================
# FOOTER
# ==============================
st.markdown("""
<hr>
<center>
IndoGen-AI Precision System © 2026 | Powered by Gemini 1.5 Flash
</center>
""", unsafe_allow_html=True)
