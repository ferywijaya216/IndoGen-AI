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
# SESSION INIT
# ==============================

if "resep_sidebar" not in st.session_state:
    st.session_state.resep_sidebar = ""

if "keluhan_sidebar" not in st.session_state:
    st.session_state.keluhan_sidebar = ""

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

resep = st.sidebar.text_input(
    "Rencana Resep",
    key="resep_sidebar"
)

keluhan = st.sidebar.text_area(
    "Keluhan Pasien",
    key="keluhan_sidebar"
)

analisis_btn = st.sidebar.button("Analisis AI")

# ==============================
# PANDUAN
# ==============================
if "ai_result" not in st.session_state:

    st.markdown("""
    <div style="background:#EAF2FF;padding:20px;border-radius:10px;margin-top:20px;">
    <b>Panduan penggunaan:</b><br>
    1. Pilih pasien dari daftar (misalnya: Budi Santoso)<br>
    2. Isi rencana resep dokter (misalnya: Metformin 500 mg 2x sehari)<br>
    3. Isi keluhan pasien (misalnya: poliuria, polidipsia, mudah lelah)<br>
    4. Klik Analisis AI untuk evaluasi farmakogenomik dan rekomendasi terapi
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
            Anda adalah sistem Clinical Decision Support berbasis farmakogenomik.

            Data pasien:
            Nama: {selected_patient['nama']}
            Diagnosis awal: {selected_patient['kondisi']}
            Marker genetik: {selected_patient['rsid']}
            Keluhan: {keluhan}
            Rencana terapi dokter: {resep}

            Berikan analisis klinis singkat untuk dokter dalam format:

            1. Evaluasi farmakogenomik terapi
            2. Potensi interaksi gene–drug
            3. Risiko adverse drug reaction
            4. Rekomendasi terapi alternatif (jika perlu)
            5. Estimasi dosis berbasis profil pasien
            6. Pertimbangan nutrigenomik relevan
            7. Probabilitas diagnosis (%)

            Gunakan bahasa klinis singkat dan langsung ke poin.
            Hindari penjelasan umum untuk pasien.
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
                    st.session_state.resep_input = resep
                    st.session_state.penyakit_input = selected_patient["kondisi"]

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

        st.markdown("---")

        st.subheader("Rekomendasi Akhir Dokter")

        resep_final = st.text_input(
            "Resep Final",
            value=st.session_state.resep_input,
            key="resep_edit"
        )

        penyakit_final = st.text_input(
            "Diagnosis Final",
            value=st.session_state.penyakit_input,
            key="penyakit_edit"
        )

        if st.button("Selesai"):

            st.success("Data konsultasi berhasil disimpan.")

            if "ai_result" in st.session_state:
                del st.session_state["ai_result"]

            if "resep_input" in st.session_state:
                del st.session_state["resep_input"]

            if "penyakit_input" in st.session_state:
                del st.session_state["penyakit_input"]

            st.session_state.resep_sidebar = ""
            st.session_state.keluhan_sidebar = ""

            st.rerun()

# ==============================
# PANEL INFO
# ==============================
with info_col:

    if "hide_warning" not in st.session_state:
        st.session_state.hide_warning=False

    if not st.session_state.hide_warning:

        st.markdown("""
        <div style="background:#FEF3C7;padding:18px;border-radius:12px;border-left:6px solid #F59E0B;">
        Sistem AI ini memberikan analisis farmakogenomik berbasis marker genetik pasien.
        Hasil analisis digunakan sebagai pendukung keputusan klinis.
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
