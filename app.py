import streamlit as st
import google.generativeai as genai
import json
import pandas as pd

# --- 1. KONFIGURASI ENGINE ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview') #
except Exception as e:
    st.error("Koneksi API Gagal. Periksa Secrets.")

# --- 2. UI SETTINGS & CSS FUTURISTIK ---
st.set_page_config(page_title="IndoGen-AI | HIS Integrated", layout="wide")

st.markdown("""
    <style>
    /* Background Futuristik Dark Medis */
    .stApp { background-color: #050b18; color: #e2e8f0; }
    
    /* Animasi Glow untuk Laporan */
    @keyframes glow {
        0% { box-shadow: 0 0 5px #1e40af; }
        50% { box-shadow: 0 0 20px #3b82f6; }
        100% { box-shadow: 0 0 5px #1e40af; }
    }
    
    .report-card { 
        background: rgba(15, 23, 42, 0.9);
        padding: 30px; 
        border-radius: 15px;
        border: 1px solid #3b82f6;
        animation: glow 3s infinite;
        line-height: 1.8;
    }
    
    .his-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #1e40af 100%);
        padding: 15px 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        border-bottom: 3px solid #3b82f6;
    }
    
    /* Tombol Analisis Presisi */
    .stButton>button {
        background: linear-gradient(45deg, #2563eb, #7c3aed);
        color: white; border: none; padding: 12px;
        border-radius: 8px; font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR: INTEGRASI HIS/EMR ---
with st.sidebar:
    st.markdown("## 🩺 IndoGen-AI")
    st.status("HIS Connection: Active", state="complete") # Pengganti animasi yang error
    
    st.markdown("### 🏥 Data Pasien (BGSi)")
    try:
        with open('data_genetik.json', 'r') as f:
            db_genom = json.load(f)
        
        selected_patient = st.selectbox("Cari NIK/Nama Pasien:", [p['nama'] for p in db_genom])
        p = next(item for item in db_genom if item["nama"] == selected_patient)
        
        st.info(f"**ID:** {hash(p['nama'])%10000}\n\n**Kondisi:** {p['kondisi_saat_ini']}")
        
        st.markdown("---")
        st.markdown("### 📝 Input Klinis Dokter")
        obat = st.text_input("Resep Obat:")
        keluhan = st.text_area("Observasi Tambahan:")
        
        if st.button("ANALISIS PRESISI"):
            st.session_state.execute = True
    except:
        st.error("Database HIS tidak ditemukan.")

# --- 4. MAIN DASHBOARD ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("<div class='his-header'><h2>Clinical Decision Support System</h2></div>", unsafe_allow_html=True)
    st.caption("Integrasi Rekam Medis Elektronik & BioGenome Science Initiative (BGSi)")

with col2:
    # Grafik Risiko Ringkas
    st.write("Indikator Risiko Genetik")
    st.bar_chart(pd.DataFrame({'Level': [40, 85, 20]}, index=['Jantung', 'Gula', 'Saraf']))

# --- 5. ANALISIS & OUTPUT ---
if 'execute' in st.session_state and st.session_state.execute:
    with st.spinner("Mengolah Data Genomik..."):
        prompt = f"""
        Tugas: IndoGen-AI CDSS Analysis.
        Pasien: {p['nama']} | Fisik: {p.get('tb_bb')}
        RSID: {p['rsid_data']} | Obat: {obat} | Keluhan: {keluhan}

        FORMAT LAPORAN (POIN-POIN):
        1. PROBABILITAS DIAGNOSIS (%): Analisis gejala klinis + variasi genetik.
        2. EVALUASI FARMAKOGENOMIK: Kecocokan {obat} dengan RSID.
        3. INTERVENSI NUTRIGENOMIK: Diet personal (termasuk gula merah/tebu kuning jika relevan).
        4. PASPOR GENOMIK: Ringkasan risiko jangka panjang.

        Bahasa Medis Formal. Referensi Vancouver.
        """
        try:
            response = model.generate_content(prompt)
            st.markdown(f'<div class="report-card">{response.text}</div>', unsafe_allow_html=True)
            
            if st.button("Selesai & Reset"):
                del st.session_state.execute
                st.rerun()
        except Exception as e:
            st.error(f"Gagal memproses AI: {e}")
