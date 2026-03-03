import streamlit as st

st.set_page_config(page_title="IndoGen-AI HIS", layout="wide")

# ==============================
# ICON FIX (KIRI ATAS JADI PANAH)
# ==============================
st.markdown("""
<style>
.arrow-icon {
    font-size: 28px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    '<div class="arrow-icon">⇒</div>',
    unsafe_allow_html=True
)

st.sidebar.title("IndoGen-AI HIS")

# ==============================
# SIDEBAR CONTENT
# ==============================
st.sidebar.selectbox(
    "Antrean Pasien (HIS):",
    ["Budi Santoso - 3201010"]
)

st.sidebar.text_input("Rencana Resep:")
st.sidebar.text_area("Keluhan Utama:")

st.sidebar.button("Analisis")

# ==============================
# HEADER (TANPA TAMBAHAN PANAH)
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
# DATA PASIEN
# ==============================
st.markdown("""
<div style="
    background-color:white;
    padding:20px;
    border-radius:15px;
    margin-top:20px;">
    <b>Nama:</b> Budi Santoso<br>
    <b>Diagnosis HIS:</b> Diabetes Melitus Tipe 2<br>
    <b>TTV:</b> 145/95 mmHg | 85 kg | 170 cm<br>
    <b>Data Genetik (RSID):</b> rs7903146(T/T) – TCF7L2
</div>
""", unsafe_allow_html=True)

# ==============================
# FLOATING WINDOW (X DI DALAM KOTAK)
# ==============================
if "hide_warning" not in st.session_state:
    st.session_state.hide_warning = False

if not st.session_state.hide_warning:
    st.markdown("""
    <style>
    .floating-box {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 340px;
        background-color: #FEF3C7;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        border-left: 6px solid #F59E0B;
        z-index: 9999;
    }
    .close-btn {
        position: absolute;
        top: 10px;
        right: 15px;
        font-weight: bold;
        cursor: pointer;
        font-size:18px;
    }
    </style>
    """, unsafe_allow_html=True)

    close = st.button("✕", key="close_floating")

    if close:
        st.session_state.hide_warning = True
        st.rerun()

    st.markdown("""
    <div class="floating-box">
        <div style="position:relative;">
            <div style="position:absolute; top:0; right:0;">
            </div>
            <b>Informasi Sistem</b><br><br>
            Sistem ini menggunakan layanan Google Gemini Free Tier.
            Layanan memiliki batasan kuota API dan dapat mengalami kepadatan trafik.
            Apabila terjadi keterlambatan analisis,
            silakan mencoba kembali beberapa saat kemudian.
        </div>
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
