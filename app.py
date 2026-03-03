import streamlit as st
import google.generativeai as genai
import json

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="IndoGen-AI", layout="wide")

# ==============================
# LOAD DATA JSON
# ==============================
with open("data_genetik.json", "r", encoding="utf-8") as f:
    patients = json.load(f)

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

resep = st.sidebar.text_input("Rencana Resep:")
keluhan = st.sidebar.text_area("Keluhan Utama:")
analisis_btn = st.sidebar.button("Analisis")

# ==============================
# KONFIGURASI GEMINI ENGINE
# ==============================
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-3-flash-preview")
    else:
        st.error("Credential Error: API Key tidak ditemukan.")
except Exception as e:
    st.error(f"Error: {e}")

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
# PANDUAN
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
# LAYOUT UTAMA + PANEL INFO
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
            response = model.generate_content(prompt)
            st.write(response.text)
        except Exception as e:
            st.error(f"Terjadi kesalahan saat analisis: {e}")

# ==============================
# PANEL INFORMASI (SAMPING KANAN)
# ==============================
if "hide_warning" not in st.session_state:
    st.session_state.hide_warning = False

with info_col:
    if not st.session_state.hide_warning:

        st.markdown("""
        <div style="
            background-color: #FEF3C7;
            padding: 18px;
            border-radius: 12px;
            border-left: 6px solid #F59E0B;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        ">
        """, unsafe_allow_html=True)

        col_title, col_x = st.columns([5,1])

        with col_title:
            st.markdown("**Informasi Sistem**")

        with col_x:
            if st.button("✕", key="close_info"):
                st.session_state.hide_warning = True
                st.rerun()

        st.markdown("""
        Sistem ini menggunakan layanan Google Gemini Free Tier.
        Layanan memiliki batasan kuota API dan dapat mengalami kepadatan trafik.
        Apabila terjadi keterlambatan analisis,
        silakan mencoba kembali beberapa saat kemudian.
        </div>
        """, unsafe_allow_html=True)

# ==============================
# FOOTER
# ==============================
st.markdown("""
<hr>
<center>
IndoGen-AI Precision System © 2026 | Powered by Gemini 3 Flash
</center>
""", unsafe_allow_html=True)
