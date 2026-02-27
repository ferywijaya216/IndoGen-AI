import streamlit as st
import google.generativeai as genai
import json

# --- 1. KONFIGURASI ENGINE ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Menggunakan model terbaru hasil pengecekan Anda
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error("Sistem gagal memverifikasi kredensial API.")

# --- 2. STATE MANAGEMENT (PENTING) ---
if 'target_data' not in st.session_state:
    st.session_state.target_data = None
if 'analisis_selesai' not in st.session_state:
    st.session_state.analisis_selesai = ""

# --- 3. UI SETTINGS ---
st.set_page_config(page_title="IndoGen-AI | Clinical Dashboard", layout="wide")

st.markdown("""
    <style>
    /* Membuat tombol analisis terlihat 'terlarang' saat proses */
    button[disabled] {
        cursor: not-allowed !important;
        opacity: 0.6;
    }
    .report-card { 
        background-color: #f8fafc; 
        padding: 25px; 
        border-left: 5px solid #0047AB;
        border-radius: 4px;
        color: #1e293b;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
st.sidebar.title("Rekam Medis & Genomik")
input_mode = st.sidebar.radio("Metode Input Data:", ["Database BGSi", "Input Manual Klinis"])

if input_mode == "Database BGSi":
    try:
        with open('data_genetik.json', 'r') as f:
            data_pasien = json.load(f)
        selected_patient = st.sidebar.selectbox("Pilih Profil Pasien:", [p['nama'] for p in data_pasien])
        p = next(item for item in data_pasien if item["nama"] == selected_patient)
        
        st.sidebar.info(f"ID: {p['nama']}\n\nKondisi: {p['kondisi_saat_ini']}")
        keluhan = st.sidebar.text_area("Observasi Tambahan:", placeholder="Masukkan gejala baru...")
        
        # Simpan ke session state agar tidak hilang saat rerun
        st.session_state.target_data = {
            "nama": p['nama'],
            "rsid": p['rsid_data'],
            "kondisi": p['kondisi_saat_ini'],
            "tambahan": keluhan
        }
    except:
        st.sidebar.error("Database tidak ditemukan.")

else:
    # Input Manual Klinis Tanpa Etnis
    with st.sidebar.form("form_manual"):
        st.write("Formulir Input Genomik")
        nama_m = st.text_input("Nama Pasien")
        rsid_m = st.text_area("Data RSID (SNP)", placeholder="Contoh: rs12248560...")
        kondisi_m = st.text_area("Diagnosis Klinis", placeholder="Kondisi saat ini...")
        
        submit_manual = st.form_submit_button("Simpan & Siapkan Analisis")
        if submit_manual:
            st.session_state.target_data = {
                "nama": nama_m,
                "rsid": rsid_m,
                "kondisi": kondisi_m,
                "tambahan": ""
            }
            st.sidebar.success("Data disimpan. Klik 'Analisis' di layar utama.")

# --- 5. MAIN DASHBOARD ---
st.title("IndoGen-AI: Sistem Intervensi Kesehatan Presisi")

# Logika Tombol Analisis
if st.session_state.target_data:
    # Tombol akan mati (disabled) otomatis jika sedang loading
    if st.button("Analisis", key="btn_analisis"):
        with st.spinner("Mengolah data klinis..."):
            d = st.session_state.target_data
            prompt = f"""
            Anda adalah IndoGen-AI, sistem pendukung keputusan klinis.
            Data Pasien: {d['nama']}
            Data RSID/Gen: {d['rsid']}
            Diagnosis: {d['kondisi']}
            Gejala Tambahan: {d['tambahan']}

            BERIKAN LAPORAN DALAM FORMAT MEDIS FORMAL (TANPA EMOJI):
            1. TINJAUAN FARMAKOGENOMIK: Analisis RSID terhadap metabolisme obat.
            2. INTERVENSI NUTRIGENOMIK: Sertakan saran spesifik penggunaan gula pasir tebu (kuning) atau gula merah sebagai nutrisi tambahan yang relevan bagi kondisi pasien.
            3. PROGNOSIS: Risiko jangka panjang.
            
            Gunakan Vancouver Style untuk referensi (langsung daftar pustaka tanpa judul 'Vancouver Style').
            """
            try:
                # Menggunakan model Gemini 3 Flash Preview
                response = model.generate_content(prompt)
                st.session_state.analisis_selesai = response.text
            except Exception as e:
                st.error(f"Kesalahan koneksi API: {e}")

# Tampilkan Hasil Jika Ada
if st.session_state.analisis_selesai:
    st.markdown(f'<div class="report-card">{st.session_state.analisis_selesai}</div>', unsafe_allow_html=True)
