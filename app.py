import streamlit as st
import google.generativeai as genai
import json
import time

# ===============================
# KONFIGURASI API
# ===============================

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3-flash-preview")

# ===============================
# KONFIGURASI PAGE
# ===============================

st.set_page_config(
    page_title="Panel Klinis Presisi",
    page_icon="🧬",
    layout="wide"
)

# ===============================
# WARNING / INFORMASI PENGGUNAAN
# ===============================

if "show_info" not in st.session_state:
    st.session_state.show_info = True

if st.session_state.show_info:
    col1, col2 = st.columns([10,1])

    with col1:
        st.warning("""
### ⚠️ Informasi Penggunaan Panel Klinis

Panel ini merupakan **simulasi sistem kesehatan presisi**.

Cara penggunaan:
1. Pilih **profil pasien dummy**
2. Masukkan **keluhan pasien**
3. Masukkan **rencana resep dokter**
4. Klik **Analisis AI**

AI akan melakukan:
- Analisis **farmakogenomik**
- Analisis **nutrigenomik**
- Evaluasi **kesesuaian obat**
- Rekomendasi **obat alternatif**
- Estimasi **diagnosis penyakit**
        """)

    with col2:
        if st.button("✖"):
            st.session_state.show_info = False

# ===============================
# DATA PASIEN DUMMY
# ===============================

data_pasien = [
{"nama": "Budi Santoso", "nik": "3201010022330001", "ttv": {"td": "145/95", "bb": "85", "tb": "170", "n": "88"}, "kondisi": "Diabetes Melitus Tipe 2", "rsid": "rs7903146(T/T) - TCF7L2"},
{"nama": "Siti Aminah", "nik": "3171050044550002", "ttv": {"td": "110/70", "bb": "48", "tb": "155", "n": "76"}, "kondisi": "Kanker Payudara", "rsid": "rs1065852(G/G) - CYP2D6"},
{"nama": "Luh Putu Astuti", "nik": "5171030011220004", "ttv": {"td": "120/80", "bb": "52", "tb": "160", "n": "80"}, "kondisi": "Epilepsi", "rsid": "HLA-B*15:02 (Positif)"},
{"nama": "Irfan Hakim", "nik": "7371020088990003", "ttv": {"td": "150/100", "bb": "92", "tb": "175", "n": "92"}, "kondisi": "Obesitas Morbid", "rsid": "rs9939609(A/A) - FTO"},
{"nama": "Ahmad Fauzi", "nik": "1171010099880005", "ttv": {"td": "135/85", "bb": "65", "tb": "168", "n": "84"}, "kondisi": "Jantung Koroner", "rsid": "rs12248560(C/T)"},
{"nama": "Maria Walanda", "nik": "7171040077660006", "ttv": {"td": "130/90", "bb": "70", "tb": "158", "n": "82"}, "kondisi": "Artritis Reumatoid", "rsid": "rs2476601(A/G)"},
{"nama": "Andi Pratama", "nik": "6471020033440007", "ttv": {"td": "115/75", "bb": "78", "tb": "180", "n": "72"}, "kondisi": "Asma Bronkial", "rsid": "rs1042713(A/G)"},
{"nama": "Samuel Tabuni", "nik": "9171010055440008", "ttv": {"td": "140/95", "bb": "82", "tb": "172", "n": "86"}, "kondisi": "Gout Akut", "rsid": "rs2231142(G/T)"},
{"nama": "Dian Sastro", "nik": "3273010011990009", "ttv": {"td": "110/70", "bb": "55", "tb": "163", "n": "78"}, "kondisi": "Hipotiroidisme", "rsid": "rs1801133(C/T)"},
{"nama": "Eko Prasetyo", "nik": "3578020022880010", "ttv": {"td": "125/80", "bb": "60", "tb": "167", "n": "74"}, "kondisi": "Depresi Mayor", "rsid": "rs6265(C/T)"}
]

# ===============================
# PILIH PASIEN
# ===============================

st.subheader("📋 Profil Pasien")

nama_pasien = st.selectbox(
    "Pilih pasien",
    [p["nama"] for p in data_pasien]
)

pasien = next(p for p in data_pasien if p["nama"] == nama_pasien)

st.json(pasien)

# ===============================
# INPUT DOKTER
# ===============================

st.subheader("🩺 Input Dokter")

keluhan = st.text_area("Keluhan pasien")

resep = st.text_area("Rencana resep dokter")

# ===============================
# ANALISIS AI
# ===============================

def analisis_ai(prompt):

    for i in range(3):

        try:

            response = model.generate_content(prompt)

            return response.text

        except Exception:

            time.sleep(3)

    return "Server AI sedang sibuk. Silakan coba beberapa saat lagi."

# ===============================
# TOMBOL ANALISIS
# ===============================

if st.button("🔬 Analisis AI"):

    if keluhan == "" or resep == "":
        st.error("Keluhan dan resep harus diisi.")

    else:

        prompt = f"""
Anda adalah AI klinis sistem kesehatan presisi.

Data pasien:
{json.dumps(pasien)}

Keluhan pasien:
{keluhan}

Rencana resep dokter:
{resep}

Lakukan analisis:

1. Analisis farmakogenomik
2. Analisis nutrigenomik
3. Evaluasi kesesuaian obat
4. Rekomendasi obat yang lebih sesuai jika ada
5. Estimasi diagnosis penyakit dalam persen

Buat hasil dalam format laporan klinis ringkas.
"""

        with st.spinner("AI sedang menganalisis genom pasien..."):

            hasil = analisis_ai(prompt)

        st.subheader("🧬 Hasil Analisis AI")

        st.write(hasil)
