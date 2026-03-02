import streamlit as st
import google.generativeai as genai
import json

# --- 1. KONFIGURASI ENGINE ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error("API Error: Hubungkan API Key di Secrets.")

# --- 2. THEME DESIGN (WHITE PREMIUM MEDICAL) ---
st.set_page_config(page_title="IndoGen-AI | Clinical Portal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    .his-header { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-bottom: 4px solid #3B82F6; margin-bottom: 30px; }
    .report-card { background: white; padding: 40px; border-radius: 20px; border: 1px solid #E2E8F0; box-shadow: 0 10px 15px rgba(0,0,0,0.05); line-height: 1.8; }
    .vital-sign-card { background: #F1F5F9; padding: 12px; border-radius: 10px; border-left: 5px solid #3B82F6; margin-bottom: 8px; font-size: 0.9rem; }
    .stButton>button { background-color: #3B82F6; color: white; border-radius: 10px; border: none; padding: 12px; font-weight: bold; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR: PASIEN & DATA PERAWAT ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=70)
    st.markdown("### **Portal Konsultasi Dokter**")
    st.caption("Terintegrasi BGSi & EMR RS")
    
    try:
        with open('data_genetik.json', 'r') as f:
            db_genom = json.load(f)
        
        # Seleksi Pasien
        selected_display = st.selectbox(
            "Daftar Antrean Pasien:", 
            [f"{p['nama']} - {p['nik']}" for p in db_genom]
        )
        p_name = selected_display.split(" - ")[0]
        p = next(item for item in db_genom if item["nama"] == p_name)

        # DATA DARI PERAWAT (PASIF)
        st.markdown("---")
        st.markdown("#### 📋 Data Pra-Konsultasi (Perawat)")
        v = p['tanda_vital']
        st.markdown(f"""
            <div class="vital-sign-card"><b>Tekanan Darah:</b> {v['td']}</div>
            <div class="vital-sign-card"><b>Nadi:</b> {v['nadi']}</div>
            <div class="vital-sign-card"><b>TB/BB:</b> {v['tb']} / {v['bb']}</div>
        """, unsafe_allow_html=True)
        
        # DATA DARI DOKTER (AKTIF)
        st.markdown("---")
        st.markdown("#### ✍️ Observasi & Terapi Dokter")
        obat = st.text_input("Rencana Resep Obat:")
        keluhan = st.text_area("Keluhan Utama Pasien:", placeholder="Pasien merasa...")
        
        if st.button("JALANKAN ANALISIS PRESISI"):
            st.session_state.execute = True
            
    except Exception as e:
        st.error(f"Koneksi HIS Terputus: {e}")

# --- 4. MAIN DASHBOARD ---
st.markdown(f"""
<div class="his-header">
    <h2 style="margin:0; color:#1E3A8A;">IndoGen-AI Clinical Decision Support</h2>
    <p style="margin:0; color:#64748B;">Analisis Integratif Genomik BGSi & Rekam Medis Pasien</p>
</div>
""", unsafe_allow_html=True)

if 'execute' in st.session_state and st.session_state.execute:
    with st.status("Sinkronisasi Genomik BGSi...", expanded=True) as status:
        st.write("Mengambil data varian genetik...")
        st.write("Cross-match dengan CPIC/PharmGKB guidelines...")
        
        prompt = f"""
        Identitas: IndoGen-AI CDSS.
        Pasien: {p['nama']} | Tanda Vital: {p['tanda_vital']}
        Profil Genomik: {p['rsid_data']}
        Diagnosis HIS: {p['kondisi_saat_ini']}
        Keluhan Terbaru: {keluhan}
        Obat Rencana: {obat}

        Berikan Analisis Medis Profesional (Format Poin-Poin):
        1. DIAGNOSIS KERJA & PROBABILITAS: Berikan % akurasi berdasarkan integrasi TTV dan Genomik.
        2. FARMAKOGENOMIK: Evaluasi {obat} terhadap metabolisme {p['rsid_data']}.
        3. NUTRIGENOMIK: Diet personal. Gunakan gula merah/tebu kuning jika sesuai profil metabolik.
        4. PASPOR GENOMIK: Prognosis dan langkah preventif jangka panjang.

        Formal, Vancouver Style (Daftar Pustaka).
        """
        
        try:
            response = model.generate_content(prompt)
            status.update(label="Analisis Selesai", state="complete", expanded=False)
            st.markdown(f'<div class="report-card">{response.text}</div>', unsafe_allow_html=True)
            
            if st.button("Selesaikan Sesi Konsultasi"):
                del st.session_state.execute
                st.rerun()
        except Exception as e:
            st.error(f"Gagal memproses AI: {e}")
else:
    st.info("Pilih pasien dari daftar antrean untuk memuat data vital dan memulai analisis.")
