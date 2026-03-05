import streamlit as st
import json
from groq import Groq

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="IndoGen-AI", layout="wide")

# ==============================
# LOAD DATA JSON
# ==============================
try:
    with open("data_genetik.json","r",encoding="utf-8") as f:
        patients = json.load(f)
except:
    st.error("File data_genetik.json tidak ditemukan.")
    patients = []

# ==============================
# API GROQ
# ==============================
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ==============================
# HEADER
# ==============================
st.markdown("""
<div style="
background:#F4F6FA;
padding:25px;
border-radius:12px;
border-left:6px solid #2E6BE6;">
<h2>IndoGen-AI Clinical Panel</h2>
Precision Medicine Decision Support System
</div>
""", unsafe_allow_html=True)

# ==============================
# PILIH PASIEN
# ==============================
st.markdown("## 📋 Profil Pasien")

patient_names = [p["nama"] for p in patients]
selected_name = st.selectbox("Pilih pasien", patient_names)

selected_patient = next(p for p in patients if p["nama"] == selected_name)

# ==============================
# CARD PROFIL PASIEN
# ==============================
st.markdown(f"""
<div style="
background:white;
padding:20px;
border-radius:12px;
box-shadow:0px 2px 6px rgba(0,0,0,0.05);
">

<b>Nama</b>: {selected_patient["nama"]} <br>
<b>NIK</b>: {selected_patient["nik"]} <br><br>

<b>Tanda Vital</b><br>
TD : {selected_patient["ttv"]["td"]} mmHg <br>
BB : {selected_patient["ttv"]["bb"]} kg <br>
TB : {selected_patient["ttv"]["tb"]} cm <br>
Nadi : {selected_patient["ttv"]["n"]} bpm <br><br>

<b>Genetik</b>: {selected_patient["rsid"]}

</div>
""", unsafe_allow_html=True)

st.write("")

# ==============================
# INPUT DOKTER
# ==============================
st.markdown("## 🩺 Input Dokter")

col1,col2 = st.columns(2)

with col1:
    resep = st.text_input(
        "Rencana Resep",
        value="Metformin"
    )

with col2:
    penyakit = st.text_input(
        "Diagnosis Penyakit",
        value=selected_patient["kondisi"]
    )

keluhan = st.text_area(
    "Keluhan Pasien",
    placeholder="Contoh: kejang, nyeri sendi, sesak napas..."
)

st.write("")

analisis_btn = st.button("Selesai & Analisis AI")

# ==============================
# ANALISIS AI
# ==============================
if analisis_btn:

    with st.spinner("AI sedang menganalisis data genom pasien..."):

        prompt = f"""
Pasien: {selected_patient["nama"]}
Diagnosis awal: {penyakit}
Genetik: {selected_patient["rsid"]}

Keluhan: {keluhan}

Rencana resep dokter: {resep}

Tugas Anda:

1. Analisis farmakogenomik berdasarkan gen pasien
2. Evaluasi apakah obat sesuai
3. Jika tidak sesuai berikan alternatif obat
4. Berikan dosis yang disarankan
5. Analisis nutrigenomik
6. Berikan kemungkinan diagnosis dalam persen

Tulis dalam format laporan klinis singkat.
"""

        try:

            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role":"user","content":prompt}
                ]
            )

            result = chat.choices[0].message.content

            st.markdown("## 🧠 Hasil Analisis AI")

            st.markdown(f"""
<div style="
background:white;
padding:20px;
border-radius:12px;
border:1px solid #E5E7EB;
">
{result}
</div>
""", unsafe_allow_html=True)

        except Exception as e:
            st.error("Server AI sedang sibuk. Silakan coba lagi.")
