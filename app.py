import streamlit as st
import json
from groq import Groq

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="IndoGen-AI", layout="wide")

# ==============================
# LOAD DATA
# ==============================
try:
    with open("data_genetik.json","r",encoding="utf-8") as f:
        patients = json.load(f)
except:
    st.error("File data_genetik.json tidak ditemukan")
    patients = []

# ==============================
# GROQ API
# ==============================
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("API KEY GROQ belum diatur di Streamlit Secrets")

# ==============================
# HEADER
# ==============================
st.markdown("""
<div style="background:#F4F6FA;padding:25px;border-radius:12px;border-left:6px solid #2E6BE6;">
<h2>IndoGen-AI Clinical Decision Support System</h2>
Precision Medicine berbasis Genomik Nasional
</div>
""",unsafe_allow_html=True)

# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("Panel Dokter")

patient_labels = [p["nama"] for p in patients]

selected_name = st.sidebar.selectbox(
    "Pilih Pasien",
    patient_labels
)

selected_patient = next(p for p in patients if p["nama"]==selected_name)

resep = st.sidebar.text_input("Rencana Resep")
keluhan = st.sidebar.text_area("Keluhan Pasien")

analisis_btn = st.sidebar.button("Analisis AI")

# ==============================
# PANDUAN
# ==============================
if "ai_result" not in st.session_state:

    st.markdown("""
    <div style="background:#EAF2FF;padding:20px;border-radius:10px;margin-top:20px;">
    <b>Panduan penggunaan:</b><br>
    1. Pilih pasien dari daftar<br>
    2. Isi rencana resep dokter<br>
    3. Isi keluhan pasien<br>
    4. Klik Analisis AI
    </div>
    """,unsafe_allow_html=True)

# ==============================
# LAYOUT
# ==============================
main_col, info_col = st.columns([3,1])

# ==============================
# PROFIL PASIEN
# ==============================
with main_col:

    st.subheader("Profil Pasien")

    col1,col2,col3 = st.columns(3)

    with col1:
        st.metric("Tekanan Darah",selected_patient["ttv"]["td"])

    with col2:
        st.metric("Berat Badan",selected_patient["ttv"]["bb"]+" kg")

    with col3:
        st.metric("Tinggi Badan",selected_patient["ttv"]["tb"]+" cm")

    st.write("**Nadi:**",selected_patient["ttv"]["n"],"bpm")

    st.write("**Diagnosis HIS:**",selected_patient["kondisi"])

    st.write("**Genetik Pasien:**",selected_patient["rsid"])

# ==============================
# ANALISIS AI
# ==============================
    if analisis_btn:

        if resep and keluhan:

            prompt = f"""
            Anda adalah sistem clinical decision support.

            Data pasien:
            Nama: {selected_patient['nama']}
            Diagnosis: {selected_patient['kondisi']}
            Genetik: {selected_patient['rsid']}
            Keluhan: {keluhan}
            Rencana resep: {resep}

            Berikan analisis:

            1. Evaluasi farmakogenomik obat
            2. Risiko reaksi obat
            3. Rekomendasi terapi optimal
            4. Dosis obat perkiraan
            5. Analisis nutrigenomik
            6. Probabilitas diagnosis (%)

            Gunakan bahasa medis profesional.
            """

            try:

                with st.spinner("AI sedang menganalisis data genom pasien..."):

                    response = client.chat.completions.create(

                        model="llama-3.3-70b-versatile",

                        messages=[
                            {"role":"user","content":prompt}
                        ]

                    )

                    result = response.choices[0].message.content

                    st.session_state.ai_result = result

            except Exception as e:

                st.error("Server AI sedang sibuk. Coba lagi beberapa saat.")

        else:

            st.warning("Isi resep dan keluhan terlebih dahulu")

# ==============================
# HASIL ANALISIS
# ==============================
    if "ai_result" in st.session_state:

        st.subheader("Hasil Analisis AI")

        st.markdown(f"""
        <div style="background:white;padding:20px;border-radius:12px;border:1px solid #E2E8F0;">
        {st.session_state.ai_result}
        </div>
        """,unsafe_allow_html=True)

# ==============================
# PANEL INFO
# ==============================
with info_col:

    if "hide_warning" not in st.session_state:
        st.session_state.hide_warning=False

    if not st.session_state.hide_warning:

        st.markdown("""
        <div style="background:#FEF3C7;padding:18px;border-radius:12px;border-left:6px solid #F59E0B;">
        Sistem ini menggunakan AI untuk analisis farmakogenomik berbasis data genom pasien.
        Hasil analisis bersifat simulasi untuk penelitian.
        </div>
        """,unsafe_allow_html=True)

        if st.button("Tutup Informasi"):
            st.session_state.hide_warning=True
            st.rerun()

# ==============================
# FOOTER
# ==============================
st.markdown("""
<hr>
<center>
IndoGen-AI Precision Medicine System © 2026
</center>
""",unsafe_allow_html=True)
