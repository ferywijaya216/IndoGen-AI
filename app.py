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
# SESSION STATE INIT
# ==============================

if "resep_sidebar" not in st.session_state:
    st.session_state.resep_sidebar = ""

if "keluhan_sidebar" not in st.session_state:
    st.session_state.keluhan_sidebar = ""

if "reset_form" not in st.session_state:
    st.session_state.reset_form = False

# reset setelah selesai
if st.session_state.reset_form:
    st.session_state.resep_sidebar = ""
    st.session_state.keluhan_sidebar = ""
    st.session_state.reset_form = False

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
    1. Pilih pasien dari daftar misalnya <b>Budi Santoso</b><br>
    2. Isi rencana resep dokter misalnya <b>Metformin 500 mg</b> atau <b>Karbamazepin</b><br>
    3. Isi keluhan pasien misalnya <b>Kejang berulang</b> atau <b>Kadar gula tinggi</b><br>
    4. Klik <b>Analisis AI</b> untuk evaluasi farmakogenomik
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
# GENETIC ALERT SYSTEM
# ==============================

    rsid = selected_patient["rsid"]

    if "HLA-B*15:02" in rsid:

        st.markdown("""
        <div style="background:#FEE2E2;padding:15px;border-radius:10px;border-left:6px solid #DC2626;margin-top:10px;">
        <b>⚠ Genetic Alert</b><br>
        HLA-B*15:02 positif → Risiko Stevens-Johnson Syndrome<br>
        Hindari obat: Carbamazepine, Oxcarbazepine, Phenytoin
        </div>
        """,unsafe_allow_html=True)

    if "CYP2D6" in rsid:

        st.markdown("""
        <div style="background:#FEF3C7;padding:15px;border-radius:10px;border-left:6px solid #F59E0B;margin-top:10px;">
        <b>⚠ Genetic Alert</b><br>
        Variasi CYP2D6 dapat mempengaruhi metabolisme obat
        </div>
        """,unsafe_allow_html=True)

# ==============================
# ANALISIS AI
# ==============================

    if analisis_btn:

        if resep and keluhan:

            prompt = f"""
            Anda adalah clinical decision support system.

            Data pasien:
            Nama: {selected_patient['nama']}
            Diagnosis: {selected_patient['kondisi']}
            Genetik: {selected_patient['rsid']}
            Keluhan: {keluhan}
            Rencana resep: {resep}

            Berikan analisis dokter:

            1. Evaluasi farmakogenomik
            2. Risiko efek samping
            3. Alternatif terapi
            4. Estimasi dosis
            5. Analisis nutrigenomik
            6. Probabilitas diagnosis (%)

            Gunakan bahasa medis ringkas untuk dokter.
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

            except:

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
# FORM EDIT RESEP & DIAGNOSIS
# ==============================

        st.markdown("### Evaluasi Akhir Dokter")

        resep_input = st.text_input(
            "Resep Final Dokter",
            value=st.session_state.resep_sidebar,
            key="resep_input"
        )

        penyakit_input = st.text_input(
            "Diagnosis Final",
            value=selected_patient["kondisi"],
            key="penyakit_input"
        )

        if st.button("Selesai"):

            st.success("Data konsultasi berhasil disimpan.")

            if "ai_result" in st.session_state:
                del st.session_state["ai_result"]

            if "resep_input" in st.session_state:
                del st.session_state["resep_input"]

            if "penyakit_input" in st.session_state:
                del st.session_state["penyakit_input"]

            st.session_state.reset_form = True
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
        Sistem ini menggunakan AI untuk analisis farmakogenomik berbasis data genom pasien.
        Hasil analisis bersifat simulasi penelitian.
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
