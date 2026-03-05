import streamlit as st
import google.generativeai as genai
import json

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="IndoGen-AI", layout="wide")

# ==============================
# LOAD DATA JSON (CACHE)
# ==============================
@st.cache_data
def load_data():
    try:
        with open("data_genetik.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

patients = load_data()

# ==============================
# GEMINI CONFIG
# ==============================
model = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-2.0-flash")
    else:
        st.error("Credential Error: API Key tidak ditemukan.")
except Exception as e:
    st.error(f"AI Engine Error: {e}")

# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("IndoGen-AI")

if patients:

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

else:
    st.sidebar.error("Data pasien tidak ditemukan.")

# ==============================
# RESET SESSION JIKA GANTI PASIEN
# ==============================
if "last_patient" not in st.session_state:
    st.session_state.last_patient = None

if patients:
    if st.session_state.last_patient != selected_label:
        st.session_state.ai_result = None
        st.session_state.last_patient = selected_label

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
if 'ai_result' not in st.session_state:

    st.markdown("""
    <div style="
    background-color:#EAF2FF;
    padding:20px;
    border-radius:10px;
    margin-top:20px;">

    <b>Panduan Penggunaan Sistem:</b><br>

    1. Pilih nama pasien pada kolom <b>Antrean Pasien</b>.<br>
    2. Masukkan nama obat pada kolom resep.<br>
    3. Masukkan gejala atau keluhan pasien.<br>
    4. Tekan tombol <b>Analisis</b> untuk mendapatkan rekomendasi klinis berbasis genomik.

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

    if patients:

        st.markdown(f"""
        <div style="
        background-color:white;
        padding:20px;
        border-radius:15px;
        margin-top:20px;
        border:1px solid #E5E7EB">

        <b>Nama:</b> {selected_patient['nama']}<br>
        <b>Diagnosis HIS:</b> {selected_patient['kondisi']}<br>

        <b>TTV:</b>
        {selected_patient['ttv']['td']} mmHg |
        {selected_patient['ttv']['bb']} kg |
        {selected_patient['ttv']['tb']} cm |
        Nadi {selected_patient['ttv']['n']} bpm<br>

        <b>Data Genetik (RSID):</b> {selected_patient['rsid']}

        </div>
        """, unsafe_allow_html=True)

        # ==============================
        # RULE ENGINE FARMACOGENOMIK
        # ==============================
        alert = ""

        if "HLA-B*15:02" in selected_patient["rsid"]:
            if resep and "carbamazepine" in resep.lower():
                alert = "⚠ Risiko Stevens-Johnson Syndrome tinggi pada pasien HLA-B*15:02 positif. Hindari Carbamazepine."

        if "CYP2D6" in selected_patient["rsid"]:
            alert = "⚠ Variasi gen CYP2D6 dapat mempengaruhi metabolisme beberapa obat psikiatri dan analgesik."

        if "FTO" in selected_patient["rsid"]:
            alert = "⚠ Varian FTO berkaitan dengan peningkatan risiko obesitas dan respon diet."

        if alert:
            st.error(alert)

        # ==============================
        # ANALISIS AI
        # ==============================
        if analisis_btn:

            if resep and keluhan:

                if model is None:
                    st.error("AI engine belum aktif.")
                else:

                    prompt = f"""
                    Sistem Clinical Decision Support genomik.

                    Data pasien:
                    Nama: {selected_patient['nama']}
                    Diagnosis awal: {selected_patient['kondisi']}
                    Marker genetik: {selected_patient['rsid']}

                    Rencana terapi dokter:
                    {resep}

                    Keluhan:
                    {keluhan}

                    Berikan analisis ringkas:

                    1. Interpretasi farmakogenomik
                    2. Evaluasi kesesuaian obat
                    3. Alternatif terapi jika perlu
                    4. Rekomendasi nutrigenomik
                    5. Probabilitas diagnosis (%)

                    Gunakan bahasa klinis singkat.
                    """

                    try:

                        with st.spinner("Menganalisis data genomik pasien..."):
                            response = model.generate_content(prompt)
                            st.session_state.ai_result = response.text

                    except Exception as e:

                        if "429" in str(e):
                            st.error("Server AI sedang sibuk. Coba lagi beberapa saat.")
                        else:
                            st.error(f"Error: {e}")

            else:
                st.warning("Silakan isi Resep dan Keluhan terlebih dahulu.")

        # ==============================
        # HASIL ANALISIS
        # ==============================
        if 'ai_result' in st.session_state and st.session_state.ai_result:

            st.write("### Hasil Analisis AI")

            st.markdown(f"""
            <div style="
            background-color:white;
            padding:20px;
            border-radius:15px;
            border:1px solid #E5E7EB">

            {st.session_state.ai_result}

            </div>
            """, unsafe_allow_html=True)

# ==============================
# PANEL INFORMASI
# ==============================
if "hide_warning" not in st.session_state:
    st.session_state.hide_warning = False

with info_col:

    if not st.session_state.hide_warning:

        st.markdown("""
        <div style="
        background-color:#FEF3C7;
        padding:20px;
        border-radius:12px;
        border-left:6px solid #F59E0B;
        margin-top:20px;">

        <b>Informasi Sistem</b><br><br>

        Sistem ini merupakan prototipe Clinical Decision Support System
        berbasis farmakogenomik dan nutrigenomik.

        Analisis dilakukan menggunakan model AI dan data genomik
        pasien untuk mendukung terapi presisi.

        </div>
        """, unsafe_allow_html=True)

        if st.button("Tutup Informasi"):
            st.session_state.hide_warning = True
            st.rerun()

# ==============================
# FOOTER
# ==============================
st.markdown("""
<hr>
<center>
IndoGen-AI Precision System © 2026 | Powered by Gemini AI
</center>
""", unsafe_allow_html=True)
