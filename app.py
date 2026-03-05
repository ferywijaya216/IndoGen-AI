import streamlit as st
from groq import Groq
import json

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="IndoGen-AI", layout="wide")

# ==============================
# LOAD DATA
# ==============================
try:
    with open("data_genetik.json", "r", encoding="utf-8") as f:
        patients = json.load(f)
except FileNotFoundError:
    st.error("File data_genetik.json tidak ditemukan.")
    patients = []

# ==============================
# GROQ API
# ==============================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("IndoGen-AI")

patient_labels = [f"{p['nama']} - {p['nik']}" for p in patients]

selected_label = st.sidebar.selectbox(
    "Antrean Pasien (HIS)",
    patient_labels
)

selected_index = patient_labels.index(selected_label)
selected_patient = patients[selected_index]

resep = st.sidebar.text_input("Rencana Resep")
keluhan = st.sidebar.text_area("Keluhan Utama")

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
<h2>Clinical Decision Support System</h2>
Integrasi Nasional Data Genomik BGSi
</div>
""", unsafe_allow_html=True)

# ==============================
# PANDUAN PENGGUNAAN
# ==============================
if 'ai_result' not in st.session_state:
    st.markdown("""
<div style="
background-color:#EAF2FF;
padding:20px;
border-radius:10px;
margin-top:20px;">

<b>Panduan Penggunaan Sistem</b><br><br>

1. Pilih pasien pada panel Antrean Pasien.<br>
2. Masukkan rencana obat pada kolom Resep.<br>
3. Masukkan keluhan pasien.<br>
4. Klik Analisis untuk mendapatkan evaluasi farmakogenomik.

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
background:white;
padding:20px;
border-radius:15px;
margin-top:20px;">

<b>Nama:</b> {selected_patient['nama']}<br>
<b>Diagnosis HIS:</b> {selected_patient['kondisi']}<br>

<b>TTV:</b>
{selected_patient['ttv']['td']} mmHg |
{selected_patient['ttv']['bb']} kg |
{selected_patient['ttv']['tb']} cm |
Nadi {selected_patient['ttv']['n']} bpm

<br><br>

<b>Data Genetik:</b> {selected_patient['rsid']}

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

Keluhan: {keluhan}

Rencana resep dokter: {resep}

Tugas Anda:

1. Analisis farmakogenomik berdasarkan gen pasien
2. Evaluasi kesesuaian obat
3. Berikan alternatif obat jika diperlukan
4. Sertakan estimasi dosis
5. Berikan analisis nutrigenomik
6. Berikan kemungkinan diagnosis (%)

Tuliskan sebagai laporan klinis singkat.
"""

            try:

                with st.spinner("AI sedang menganalisis genom pasien..."):

                    chat = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )

                    st.session_state.ai_result = chat.choices[0].message.content

            except:
                st.error("Server AI sedang sibuk. Silakan coba beberapa saat lagi.")

        else:
            st.warning("Isi Resep dan Keluhan terlebih dahulu.")

    # ==============================
    # TAMPILKAN HASIL AI
    # ==============================

    if 'ai_result' in st.session_state:

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
        # FINALISASI DOKTER
        # ==============================

        st.write("### Finalisasi Dokter")

        with st.form("final_form"):

            resep_final = st.text_input(
                "Resep Final",
                value=resep
            )

            diagnosis_final = st.text_input(
                "Diagnosis Final",
                value=selected_patient['kondisi']
            )

            selesai_btn = st.form_submit_button("Selesai")

            if selesai_btn:

                st.success("Keputusan klinis berhasil disimpan.")

                st.markdown(f"""
<div style="
background:#F0F9FF;
padding:15px;
border-radius:10px;
border-left:5px solid #0284C7;">

<b>Ringkasan Keputusan Klinis</b><br><br>

Resep Final: {resep_final}<br>
Diagnosis Final: {diagnosis_final}

</div>
""", unsafe_allow_html=True)

# ==============================
# PANEL INFO
# ==============================
with info_col:

    if "hide_warning" not in st.session_state:
        st.session_state.hide_warning = False

    if not st.session_state.hide_warning:

        st.markdown("""
<div style="
background-color:#FEF3C7;
padding:18px;
border-radius:12px;
border-left:6px solid #F59E0B;">
""", unsafe_allow_html=True)

        col_title, col_x = st.columns([5,1])

        with col_title:
            st.markdown("**Informasi Sistem**")

        with col_x:
            if st.button("✕"):
                st.session_state.hide_warning = True
                st.rerun()

        st.markdown("""
Sistem ini menggunakan layanan AI berbasis Large Language Model.

Analisis bersifat sebagai Clinical Decision Support
dan tidak menggantikan keputusan klinis dokter.
</div>
""", unsafe_allow_html=True)

# ==============================
# FOOTER
# ==============================
st.markdown("""
<hr>
<center>
IndoGen-AI Precision System © 2026
</center>
""", unsafe_allow_html=True)
