import streamlit as st
import google.generativeai as genai
import json
import random

# --- 1. KONFIGURASI ENGINE GEMINI 3 FLASH ---
# Pastikan Anda sudah mengisi API Key di .streamlit/secrets.toml
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Menggunakan model Gemini 3 Flash terbaru
    model = genai.GenerativeModel('gemini-3-flash-preview')
except Exception as e:
    st.error("Konfigurasi API Gagal. Pastikan API Key ada di Secrets.")

# --- 2. FUNGSI LOAD DATA DUMMY ---
def load_data():
    try:
        with open('data_genetik.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("File data_genetik.json tidak ditemukan!")
        return []

# --- 3. UI DASHBOARD PROFESIONAL ---
st.set_page_config(page_title="IndoGen-AI | Precision Health", layout="wide", page_icon="🧬")

# Custom CSS untuk tampilan Dashboard Medis
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stAlert { border-radius: 10px; }
    .report-box { 
        background-color: white; 
        padding: 30px; 
        border-radius: 15px; 
        border-left: 8px solid #0047AB; 
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .header-text { color: #0047AB; font-family: 'Helvetica'; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='header-text'>🧬 IndoGen-AI: Sistem Kesehatan Presisi</h1>", unsafe_allow_html=True)
st.markdown("Integrasi **Farmakogenomik** & **Nutrigenomik** berbasis data BGSi Nasional.")
st.markdown("---")

# --- 4. SIDEBAR INPUT ---
st.sidebar.header("📋 Rekam Medis & Genomik")
input_mode = st.sidebar.selectbox("Pilih Metode Input", ["Demo Profil Masyarakat (Dummy)", "Input Manual Klinis"])

target_data = ""

if input_mode == "Demo Profil Masyarakat (Dummy)":
    data_pasien = load_data()
    if st.sidebar.button("🎲 Muat Profil Acak"):
        st.session_state.p = random.choice(data_pasien)
    
    if 'p' in st.session_state:
        p = st.session_state.p
        with st.sidebar.expander("Biodata Pasien", expanded=True):
            st.write(f"**Nama:** {p['nama']}")
            st.write(f"**Usia/Etnis:** {p['usia']} th / {p['etnis']}")
            st.write(f"**Kondisi Awal:** {p['kondisi_saat_ini']}")
        
        # Fitur Interaktif: Input keluhan baru
        keluhan_baru = st.sidebar.text_area("🔍 Keluhan Tambahan Saat Ini:", 
                                            placeholder="Contoh: Mengeluh gatal setelah minum obat, atau nyeri jantung...")
        
        target_data = f"""
        PASIEN: {p['nama']}, {p['usia']} th, {p['etnis']}.
        KONDISI KLINIS SAAT INI: {p['kondisi_saat_ini']}.
        KELUHAN BARU: {keluhan_baru}.
        DATA RSID (GEN): {p['rsid_data']}.
        CATATAN NUTRISI: {p['fokus_nutrigenomik']}.
        """
else:
    st.sidebar.warning("Mode Input Manual dalam pengembangan.")

# --- 5. EKSEKUSI AI GEMINI 3 FLASH ---
if st.sidebar.button("🚀 ANALISIS KESEHATAN PRESISI"):
    if target_data:
        with st.status("Gemini 3 Flash sedang memproses data genomik...", expanded=True) as status:
            st.write("Sinkronisasi database farmakogenomik (PharmGKB)...")
            
            prompt = f"""
            Anda adalah IndoGen-AI, asisten dokter ahli kesehatan presisi.
            Gunakan data pasien berikut untuk memberikan rekomendasi klinis:
            {target_data}

            STRUKTUR LAPORAN:
            1. ANALISIS FARMAKOGENOMIK: Jelaskan kecocokan obat dengan genetik (RSID). Berikan rekomendasi obat yang aman atau penyesuaian dosis.
            2. INTERPRETASI NUTRIGENOMIK: Berikan saran diet lokal. Khusus untuk asupan gula, berikan rekomendasi penggunaan gula pasir tebu (kuning) atau gula merah sebagai nutrisi tambahan sesuai kondisi genetiknya.
            3. PREDIKSI RISIKO: Jelaskan risiko penyakit masa depan berdasarkan RSID yang ditemukan.

            SYARAT: Bahasa profesional medis. Gunakan Vancouver Style untuk referensi di akhir laporan.
            """
            
            # Memanggil Gemini 3 Flash
            response = model.generate_content(prompt)
            status.update(label="Analisis Selesai!", state="complete", expanded=False)

        # Output Tampilan Profesional
        st.markdown(f"""
            <div class="report-box">
                <h2 style='color: #0047AB;'>📋 Hasil Interpretasi Paspor Genomik</h2>
                <hr>
                {response.text}
            </div>
        """, unsafe_allow_html=True)
        
        st.download_button("📥 Download Laporan", response.text, file_name=f"Laporan_IndoGen_{st.session_state.p['nama']}.txt")
    else:
        st.warning("Silakan muat profil pasien terlebih dahulu di sidebar.")

st.sidebar.markdown("---")
st.sidebar.caption("Powered by Gemini 3 Flash (Free Tier)")



