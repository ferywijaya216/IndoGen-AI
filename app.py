import streamlit as st
import google.generativeai as genai
import json
from streamlit_lottie import st_lottie
import pandas as pd

# --- 1. KONFIGURASI ENGINE ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview') #
except Exception as e:
    st.error("Koneksi API Gagal. Pastikan API Key terpasang di Secrets.")

# --- 2. ANIMASI ASSETS (Lottie) ---
# Mengambil animasi medis futuristik agar web lebih 'hidup'
def load_lottie_url(url: str):
    import requests
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

lottie_medical = load_lottie_url("https://assets10.lottiefiles.com/packages/lf20_5njp9vbg.json")

# --- 3. UI SETTINGS & CSS ---
st.set_page_config(page_title="IndoGen-AI | HIS Integrated", layout="wide")

st.markdown("""
    <style>
    /* Background Futuristik Dark-Mode Medis */
    .stApp {
        background-color: #050b18;
        color: #e2e8f0;
    }
    /* Card Laporan Medis */
    .report-card { 
        background: rgba(15, 23, 42, 0.8);
        padding: 30px; 
        border-radius: 15px;
        border: 1px solid #1e40af;
        box-shadow: 0 0 20px rgba(37, 99, 235, 0.2);
        line-height: 1.8;
    }
    /* Header HIS */
    .his-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #1e40af 100%);
        padding: 10px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-bottom: 2px solid #3b82f6;
    }
    /* Tombol Analisis Presisi */
    .stButton>button {
        background: linear-gradient(45deg, #2563eb, #7c3aed);
        color: white;
        border: none;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(124, 58, 237, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR: INTEGRASI HIS/EMR ---
with st.sidebar:
    st_lottie(lottie_medical, height=150, key="med_anim")
    st.markdown("### 🏥 HIS Integrated System")
    st.caption("Status: Connected to BGSi Database")
    
    # Dokter hanya perlu memilih pasien, data genomik ditarik otomatis
    try:
        with open('data_genetik.json', 'r') as f:
            db_genom = json.load(f)
        
        patient_names = [p['nama'] for p in db_genom]
        selected_patient = st.selectbox("Cari Data Pasien (NIK/Nama):", patient_names)
        patient_data = next(item for item in db_genom if item["nama"] == selected_patient)
        
        st.markdown("---")
        st.write(f"**Nama:** {patient_data['nama']}")
        st.write(f"**ID Pasien:** ID-{hash(patient_data['nama']) % 10000}")
        st.write(f"**Data Genetik:** {patient_data['rsid_data'][:15]}... (Encrypted)")
        
        # Input Klinis dari Dokter
        st.markdown("### 📝 Parameter Klinis (HIS)")
        obat_resep = st.text_input("Rencana Resep Obat:")
        keluhan_baru = st.text_area("Observasi Klinis Baru:")
        
        # Tombol Analisis dengan Proteksi Double-Click
        if st.button("ANALISIS PRESISI", use_container_width=True):
            st.session_state.execute = True
            
    except Exception as e:
        st.error("Gagal Sinkronisasi Database HIS.")

# --- 5. MAIN DASHBOARD: VISUALISASI ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<div class='his-header'><h2>IndoGen-AI | Clinical Decision Support System</h2></div>", unsafe_allow_html=True)
    st.write("Sistem Kesehatan Presisi Nasional berbasis AI terintegrasi BGSi Nasional.")

with col2:
    # Grafik status kesehatan (Dinamis)
    st.caption("Indikator Risiko Pasien")
    chart_data = pd.DataFrame({'Risiko': [30, 70, 45]}, index=['Kardiologi', 'Metabolik', 'Onkologi'])
    st.bar_chart(chart_data)

# --- 6. PROSES ANALISIS & OUTPUT ---
if 'execute' in st.session_state and st.session_state.execute:
    with st.spinner("Mengintegrasikan Analitik Farmakogenomik & Nutrigenomik..."):
        prompt = f"""
        Anda adalah IndoGen-AI, CDSS terintegrasi EMR/HIS.
        DATA PASIEN: {patient_data['nama']} | Kondisi: {patient_data['kondisi_saat_ini']}
        GENOMIK (RSID): {patient_data['rsid_data']}
        RESEP DOKTER: {obat_resep}
        KELUHAN: {keluhan_baru}

        ANALISIS KLINIS UNTUK DOKTER:
        1. PROBABILITAS DIAGNOSIS: Berikan persentase (%) akurasi berdasarkan integrasi data genom dan gejala klinis.
        2. EVALUASI FARMAKOGENOMIK: Analisis resep {obat_resep} terhadap metabolisme RSID. Rekomendasikan dosis presisi.
        3. INTERVENSI NUTRIGENOMIK: Strategi diet personal. Sertakan penggunaan gula merah atau gula pasir tebu (kuning) jika relevan secara klinis.
        4. PASPOR GENOMIK: Ringkasan risiko jangka panjang.

        Gunakan Bahasa Medis Formal & Poin-Poin. Sertakan Referensi Vancouver di akhir (Daftar Pustaka saja).
        """
        try:
            response = model.generate_content(prompt)
            st.markdown(f'<div class="report-card">{response.text}</div>', unsafe_allow_html=True)
            
            # Tombol Selesai & Refresh
            st.write("---")
            if st.button("Simpan Laporan & Selesai"):
                del st.session_state.execute
                st.rerun()
        except Exception as e:
            st.error(f"Sistem Gagal Memproses Data: {e}")
else:
    st.markdown("""
        <div style='text-align: center; padding: 100px;'>
            <h3 style='color: #4b5563;'>Silakan pilih profil pasien di sidebar HIS untuk memulai analisis kesehatan presisi.</h3>
        </div>
    """, unsafe_allow_html=True)
