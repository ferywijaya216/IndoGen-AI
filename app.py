import streamlit as st
import google.generativeai as genai
import json
import time

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="IndoGen-AI", layout="wide")

# ==============================
# LOAD DATA JSON
# ==============================
try:
    with open("data_genetik.json", "r", encoding="utf-8") as f:
        patients = json.load(f)
except FileNotFoundError:
    st.error("File data_genetik.json tidak ditemukan.")
    patients = []

# ==============================
# GEMINI CONFIG (API dari secrets)
# ==============================
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
    else:
        st.error("API Key tidak ditemukan di Streamlit Secrets.")
except Exception as e:
    st.error(f"Error konfigurasi AI: {e}")

# ==============================
# FUNCTION AI ANALYSIS (ANTI ERROR)
# ==============================
def run_ai_analysis(prompt):

    max_retry = 3

    for attempt in range(max_retry):

        try:

            response = model.generate_content(
                prompt,
                request_options={"timeout": 30}
            )

            return response.text

        except Exception as e:

            error_text = str(e)

            if "429" in error_text or "503" in error_text or "504" in error_text:

                if attempt < max_retry - 1:
                    time.sleep(3)
                    continue
                else:
                    return "Server AI sedang sibuk. Silakan coba beberapa saat lagi."

            return f"Terjadi error sistem: {e}"

# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("IndoGen-AI")

patient_labels = [f"{p['nama']} - {p['nik']}" for p in patients]

selected_label = st.sidebar.selectbox(
    "Antrean Pasien (HIS):",
    patient_labels
)

selected_index = patient_labels.index(selected_label)
selected_patient = patients[selected_index]

resep = st.sidebar.text_input("Rencana Resep:", "Karbamazepin")
keluhan = st.sidebar.text_area("Keluhan Utama:", "Kejang")

analisis_btn = st.sidebar.button("Analisis")

# ==============================
# HEADER
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
# SESSION STATE
# ==============================
if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

# ==============================
# PANDUAN PENGGUNAAN
# ==============================
if not st.session_state.ai_result:

    st.markdown("""
    <div style="
    background-color:#EAF2FF;
    padding:20px;
    border-radius:10px;
    margin-top:20px;">

    <b>Panduan Penggunaan Sistem:</b><br><br>

    1. Pilih pasien pada kolom <b>Antrean Pasien</b>.<br>
    2. Masukkan rencana resep obat.<br>
    3. Masukkan keluhan utama pasien.<br>
    4. Tekan tombol <b>Analisis</b> untuk mendapatkan rekomendasi terapi presisi berbasis genomik.

    </div>
    """, unsafe_allow_html=True)

# ==============================
# LAYOUT
# ==============================
main_col, info_col = st.columns([3,1])

# ==============================
# DASHBOARD UTAMA
# ==============================
with main_col:

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
    # ANALISIS AI
    # ==============================

    if analisis_btn:

        if resep and keluhan:

            prompt = f"""
Pasien: {selected_patient['nama']}
Diagnosis: {selected_patient['kondisi']}
Genetik: {selected_patient['rsid']}
Resep Dokter: {resep}
Keluhan: {keluhan}

Buat analisis klinis berbasis farmakogenomik dan nutrigenomik.

Evaluasi kecocokan obat dengan profil genetik pasien.
Jika obat kurang sesuai, berikan alternatif terapi.
Sertakan estimasi diagnosis dalam persen.

Gunakan bahasa ilmiah singkat.
Gunakan referensi Vancouver style.
"""

            with st.spinner("Menganalisis data genomik pasien..."):
                result = run_ai_analysis(prompt)
                st.session_state.ai_result = result

        else:
            st.warning("Silakan isi resep dan keluhan terlebih dahulu.")

    if st.session_state.ai_result:

        st.write("### Hasil Analisis AI")

        st.markdown(f"""
        <div style="
        background-color:white;
        padding:20px;
        border-radius:15px;
        border:1px solid #E2E8F0;">
        {st.session_state.ai_result}
        </div>
        """, unsafe_allow_html=True)

# ==============================
# PANEL INFO
# ==============================
if "hide_warning" not in st.session_state:
    st.session_state.hide_warning = False

with info_col:

    if not st.session_state.hide_warning:

        box = st.container()

        with box:

            col1, col2 = st.columns([6,1])

            with col1:
                st.markdown("**Informasi Sistem**")

            with col2:
                if st.button("✕"):
                    st.session_state.hide_warning = True
                    st.rerun()

            st.markdown("""
Sistem ini menggunakan layanan AI Google Gemini Free Tier.

Pada kondisi tertentu, server AI dapat mengalami kepadatan trafik
atau pembatasan kuota API sehingga analisis membutuhkan waktu
lebih lama.

Apabila terjadi keterlambatan, silakan mencoba kembali beberapa saat kemudian.
""")

# ==============================
# FOOTER
# ==============================
st.markdown("""
<hr>
<center>
IndoGen-AI Precision System © 2026 | Powered by Gemini
</center>
""", unsafe_allow_html=True)
