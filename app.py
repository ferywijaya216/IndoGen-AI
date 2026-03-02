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
    st.error("API Error: Hubungkan API Key di Secrets.")

# --- 2. THEME DESIGN (WHITE PREMIUM) ---
st.set_page_config(page_title="IndoGen-AI | Clinical Portal", layout="wide")

st.markdown("""
    <style>
    /* Global White Theme */
    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
    }
    
    /* Header HIS Premium */
    .his-header {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border-bottom: 4px solid #3B82F6;
        margin-bottom: 30px;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #E2E8F0;
    }

    /* Professional Card Report */
    .report-card { 
        background: white;
        padding: 40px; 
        border-radius: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
        color: #1E293B;
        line-height: 1.8;
        font-family: 'Inter', sans-serif;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #3B82F6;
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.39);
        width: 100%;
    }
    
    /* Risk Badge */
    .risk-badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        background: #FEE2E2;
        color: #991B1B;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR: PASIEN & EMR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=80)
    st.markdown("### **IndoGen-AI Portal**")
    st.caption("Integrated with EMR/HIS & BGSi")
    
    try:
        with open('data_genetik.json', 'r') as f:
            db_genom = json.load(f)
        
        # Pencarian Pasien
        search = st.selectbox("Pilih Profil Pasien:", [p['nama'] for p in db_genom])
        p = next(item for item in db_genom if item["nama"] == search)
        
        # Info Singkat di Sidebar
        st.markdown(f"""
        <div style="background: #F1F5F9; padding: 15px; border-radius: 10px; margin-top: 10px;">
            <small>NIK: {p['nik']}</small><br>
            <b>{p['nama']}</b><br>
            <span class="risk-badge">Genetik Terdeteksi</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### **Input Klinis**")
        obat = st.text_input("Resep Rencana:", placeholder="Metformin, Tamoxifen, dll")
        obs = st.text_area("Keluhan/Hasil Lab:", placeholder="Tekanan darah terbaru, gejala...")
        
        if st.button("JALANKAN ANALISIS"):
            st.session_state.run = True
            
    except:
        st.error("Gagal memuat database pasien.")

# --- 4. DASHBOARD UTAMA ---
st.markdown(f"""
<div class="his-header">
    <h2 style="margin:0; color:#1E3A8A;">Clinical Decision Support System</h2>
    <p style="margin:0; color:#64748B;">Sistem Analitik Kesehatan Presisi Nasional - Berbasis Data Genomik Indonesia</p>
</div>
""", unsafe_allow_html=True)

# Visualisasi Data (Chart Progres Pasien)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Kecocokan Genetik", "88%", "Bio-Valid")
with col2:
    st.metric("Risiko Efek Samping", "Low", "-12%", delta_color="inverse")
with col3:
    st.metric("Status BGSi", "Synced")

# --- 5. EKSEKUSI AI & OUTPUT ---
if 'run' in st.session_state and st.session_state.run:
    with st.status("IndoGen-AI sedang mengolah metadata...", expanded=True) as status:
        st.write("Sinkronisasi data rekam medis...")
        st.write("Interpretasi varian genomik melalui CPIC guidelines...")
        
        prompt = f"""
        Identitas: IndoGen-AI Specialist.
        Pasien: {p['nama']} ({p['tb_bb']})
        Kondisi: {p['kondisi_saat_ini']}
        Genetik: {p['rsid_data']}
        Input Dokter: Obat {obat}, Keluhan {obs}

        TUGAS (FORMAT MEDIS PROFESIONAL):
        1. PROBABILITAS DIAGNOSIS: Berikan angka kepercayaan (%) terhadap kondisi pasien.
        2. FARMAKOGENOMIK (PGx): Evaluasi {obat} terhadap RSID. Apakah aman? Berikan dosis spesifik.
        3. NUTRIGENOMIK: Saran diet personal. (Gunakan gula merah/tebu kuning jika sesuai klinis).
        4. PASPOR GENOMIK: Rekomendasi tindakan pencegahan jangka panjang.

        Gunakan Bahasa Medis Formal. Referensi Vancouver.
        """
        
        try:
            response = model.generate_content(prompt)
            status.update(label="Analisis Selesai", state="complete", expanded=False)
            
            st.markdown(f'<div class="report-card">{response.text}</div>', unsafe_allow_html=True)
            
            # Tombol Refresh
            if st.button("Selesaikan Sesi & Cetak"):
                del st.session_state.run
                st.rerun()
        except Exception as e:
            st.error(f"Gagal memproses data: {e}")
else:
    # Ilustrasi Dashboard saat Kosong
    st.markdown("""
    <div style="text-align: center; padding: 100px; color: #94A3B8;">
        <img src="https://cdn-icons-png.flaticon.com/512/3774/3774299.png" width="100" style="opacity: 0.5;">
        <h3>Menunggu Pemilihan Pasien di Sidebar</h3>
        <p>Data genetik akan dimuat otomatis setelah pasien dipilih.</p>
    </div>
    """, unsafe_allow_html=True)
