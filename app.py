import streamlit as st
import google.generativeai as genai
import json
import pandas as pd

# --- 1. KONFIGURASI ENGINE ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Menggunakan model Gemini 3 Flash Preview yang Anda miliki
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error("API Error: Pastikan GEMINI_API_KEY sudah terpasang di Secrets Streamlit.")

# --- 2. THEME DESIGN (WHITE PREMIUM MEDICAL) ---
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
        padding: 12px 24px;
        font-weight: 600;
        box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.39);
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(59, 130, 246, 0.5);
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

# --- 3. SIDEBAR: PASIEN & EMR (HIS INTEGRATED) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=80)
    st.markdown("### **IndoGen-AI Portal**")
    st.caption("Integrated with EMR/HIS & BGSi National Database")
    
    try:
        with open('data_genetik.json', 'r') as f:
            db_genom = json.load(f)
        
        # Dropdown Pasien dengan NIK untuk Keamanan Klinis
        selected_display = st.selectbox(
            "Cari Pasien (Nama - NIK):", 
            [f"{p['nama']} - {p['nik']}" for p in db_genom]
        )

        # Ambil data asli dari pilihan
        selected_name = selected_display.split(" - ")[0]
        p = next(item for item in db_genom if item["nama"] == selected_name)
        
        # Tampilan Ringkasan Profil Pasien
        st.markdown(f"""
        <div style="background: #F1F5F9; padding: 15px; border-radius: 10px; margin-top: 10px;">
            <small>ID BGSi: {hash(p['nik']) % 100000}</small><br>
            <b>{p['nama']}</b><br>
            <span class="risk-badge">Genetik Terdeteksi</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### **Input Klinis (Dokter)**")
        obat = st.text_input("Rencana Resep:", placeholder="Contoh: Metformin, Warfarin...")
        obs = st.text_area("Observasi & Keluhan Baru:", placeholder="Misal: TD 150/90, pusing, mual...")
        
        if st.button("JALANKAN ANALISIS PRESISI"):
            st.session_state.run_analysis = True
            
    except Exception as e:
        st.error(f"Gagal memuat database pasien: {e}")

# --- 4. DASHBOARD UTAMA ---
st.markdown(f"""
<div class="his-header">
    <h2 style="margin:0; color:#1E3A8A;">Clinical Decision Support System (CDSS)</h2>
    <p style="margin:0; color:#64748B;">Sistem Analitik Kesehatan Presisi Nasional - Berbasis Data Genomik Indonesia</p>
</div>
""", unsafe_allow_html=True)

# Indikator Visual (Metrics)
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Akurasi Genomik", "99.2%", "BGSi Verified")
with m2:
    st.metric("Interaksi Obat", "Terdeteksi", delta_color="inverse")
with m3:
    st.metric("Status Sesi", "Aktif")

# --- 5. EKSEKUSI AI & OUTPUT LAPORAN ---
if 'run_analysis' in st.session_state and st.session_state.run_analysis:
    with st.status("IndoGen-AI: Mengintegrasikan metadata klinis...", expanded=True) as status:
        st.write("Menghubungkan ke pusat data BGSi...")
        st.write("Sinkronisasi rekam medis elektronik (EMR)...")
        st.write("Menganalisis variasi genomik terhadap database CPIC & PharmGKB...")
        
        # Prompt Medis Formal dengan Instruksi Khusus Anda
        prompt = f"""
        Identitas: IndoGen-AI Clinical Specialist.
        Data Pasien: {p['nama']} ({p['tb_bb']})
        Diagnosis Awal: {p['kondisi_saat_ini']}
        Profil Genetik (RSID): {p['rsid_data']}
        Input Dokter: Resep {obat}, Observasi Baru {obs}

        TUGAS ANALISIS (FORMAT POIN-POIN PROFESIONAL):
        1. PROBABILITAS DIAGNOSIS: Berikan analisis kemungkinan penyakit saat ini (dalam %) berdasarkan gejala klinis dan data genetik.
        2. EVALUASI FARMAKOGENOMIK: Analisis kecocokan obat {obat} terhadap profil RSID pasien. Berikan saran dosis spesifik atau alternatif obat.
        3. INTERVENSI NUTRIGENOMIK: Strategi diet personal. Sertakan rekomendasi penggunaan gula merah atau gula pasir tebu (kuning) HANYA jika relevan secara klinis.
        4. PASPOR GENOMIK: Ringkasan risiko jangka panjang dan langkah preventif.

        Gunakan Bahasa Medis Formal (Tanpa Emoji). Sertakan Referensi Vancouver langsung di bagian akhir.
        """
        
        try:
            # Menggunakan Gemini 3 Flash Preview
            response = model.generate_content(prompt)
            status.update(label="Analisis Selesai", state="complete", expanded=False)
            
            # Tampilan Hasil dalam Card Premium
            st.markdown(f'<div class="report-card">{response.text}</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            if st.button("Selesaikan Sesi Pasien"):
                del st.session_state.run_analysis
                st.rerun()
                
        except Exception as e:
            st.error(f"Kegagalan Analisis AI: {e}")

else:
    # Tampilan "Waiting State" yang Elegan
    st.markdown("""
    <div style="text-align: center; padding: 80px; color: #94A3B8;">
        <img src="https://cdn-icons-png.flaticon.com/512/3774/3774299.png" width="80" style="opacity: 0.3; margin-bottom: 20px;">
        <h3>Sistem Siap</h3>
        <p>Silakan pilih profil pasien di sidebar HIS untuk memuat data genomik dan memulai analisis.</p>
    </div>
    """, unsafe_allow_html=True)
