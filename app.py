import streamlit as st
import google.generativeai as genai
import json

# --- 1. KONFIGURASI ENGINE ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Menggunakan model paling mutakhir hasil pengecekan Anda
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error("Sistem gagal memverifikasi kredensial API.")

# --- 2. UI SETTINGS ---
st.set_page_config(page_title="IndoGen-AI | Clinical Dashboard", layout="wide")

# CSS untuk tampilan Medis Serius (Tanpa Emo berlebih, font bersih)
st.markdown("""
    <style>
    .report-card { 
        background-color: #ffffff; 
        padding: 25px; 
        border: 1px solid #d1d5db;
        border-radius: 4px;
        color: #1f2937;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        width: 100%;
        border-radius: 4px;
        background-color: #0047AB;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR: REKAM MEDIS ---
st.sidebar.title("Rekam Medis & Genomik")

# State Management untuk Tombol (Mencegah Klik Berkali-kali)
if 'processing' not in st.session_state:
    st.session_state.processing = False

input_mode = st.sidebar.radio("Metode Input Data:", ["Database BGSi", "Input Manual Klinis"])

target_data = ""

if input_mode == "Database BGSi":
    try:
        with open('data_genetik.json', 'r') as f:
            data_pasien = json.load(f)
        selected_patient = st.sidebar.selectbox("Pilih Profil Pasien:", [p['nama'] for p in data_pasien])
        p = next(item for item in data_pasien if item["nama"] == selected_patient)
        
        st.sidebar.info(f"ID: {p['nama']}\n\nEtnis: {p['etnis']}\n\nKondisi: {p['kondisi_saat_ini']}")
        keluhan = st.sidebar.text_area("Observasi Klinis Tambahan:", placeholder="Masukkan gejala baru jika ada...")
        
        target_data = f"Pasien: {p['nama']}, Etnis: {p['etnis']}, RSID: {p['rsid_data']}, Riwayat: {p['kondisi_saat_ini']}, Gejala Baru: {keluhan}"
    except:
        st.sidebar.error("Database tidak ditemukan.")

else:
    # Input Manual Klinis (Sudah diaktifkan)
    with st.sidebar.form("form_manual"):
        st.write("Formulir Input Genomik Manual")
        nama = st.text_input("Nama Pasien")
        etnis = st.selectbox("Etnis", ["Jawa", "Sunda", "Batak", "Dayak", "Papua", "Lainnya"])
        rsid = st.text_area("Data RSID (SNP)", placeholder="Contoh: rs12248560 (CYP2C19)...")
        kondisi = st.text_area("Diagnosis Klinis", placeholder="Kondisi medis saat ini...")
        
        submit_manual = st.form_submit_button("Simpan Data")
        if submit_manual:
            target_data = f"Pasien: {nama}, Etnis: {etnis}, RSID: {rsid}, Kondisi: {kondisi}"
            st.sidebar.success("Data Manual Siap Dianalisis")

# --- 4. MAIN DASHBOARD ---
st.title("IndoGen-AI: Sistem Intervensi Kesehatan Presisi")
st.caption("Integrasi Data Genomik Nasional untuk Personalisasi Terapi.")

# Tombol Analisis dengan Proteksi Double-Click
btn_label = "Memproses Analisis..." if st.session_state.processing else "Analisis"
if st.button(btn_label, disabled=st.session_state.processing):
    if target_data:
        st.session_state.processing = True
        
        # Placeholder loading yang profesional (Tanpa menyebut "Gemini")
        with st.spinner("Mengintegrasikan data genomik dengan basis data farmakologi..."):
            prompt = f"""
            Anda adalah IndoGen-AI, sistem pendukung keputusan klinis (CDSS) untuk dokter.
            Analisis data berikut: {target_data}

            BERIKAN LAPORAN DALAM FORMAT MEDIS:
            1. TINJAUAN FARMAKOGENOMIK: Analisis interaksi obat berdasarkan RSID. Berikan rekomendasi penyesuaian dosis atau alternatif obat secara spesifik.
            2. INTERVENSI NUTRIGENOMIK: Rekomendasi gizi berbasis etnis dan genetik. Masukkan saran penggunaan gula pasir tebu (kuning) atau gula merah sebagai nutrisi tambahan yang relevan.
            3. PROGNOSIS RISIKO: Prediksi risiko penyakit kronis.
            
            Gunakan bahasa medis formal (Dokter-ke-Dokter). Hindari penggunaan emotikon.
            Sertakan daftar referensi ilmiah di akhir menggunakan standar Vancouver (tanpa menulis judul 'Vancouver Style').
            """
            
            try:
                response = model.generate_content(prompt)
                st.markdown(f'<div class="report-card">{response.text}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Kegagalan Analisis: {e}")
        
        st.session_state.processing = False
        st.rerun()
    else:
        st.warning("Mohon masukkan atau pilih data pasien terlebih dahulu.")
