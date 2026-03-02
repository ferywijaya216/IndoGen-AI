import streamlit as st
import google.generativeai as genai
import json

# --- 1. CONFIG ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Model Gemini 3 Flash dirancang untuk kecepatan (latency rendah)
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error("API Error.")

# --- 2. THEME DESIGN (WHITE PREMIUM) ---
st.set_page_config(page_title="IndoGen-AI | Clinical Portal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    .his-header {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border-bottom: 5px solid #3B82F6; margin-bottom: 30px;
    }
    .report-card { 
        background: white; padding: 40px; border-radius: 25px;
        border: 1px solid #E2E8F0;
        box-shadow: 15px 15px 40px #e2e8f0, -15px -15px 40px #ffffff;
        line-height: 1.9;
    }
    .vital-box {
        background: #F1F5F9; padding: 15px; border-radius: 12px;
        border-left: 5px solid #3B82F6; margin-bottom: 10px;
    }
    .stButton>button {
        background: #3B82F6; color: white; border-radius: 10px;
        border: none; padding: 12px; font-weight: bold; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR (EMR ALUR RUMAH SAKIT) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2966/2966327.png", width=70)
    st.markdown("### **Portal Klinis Dokter**")
    
    try:
        with open('data_genetik.json', 'r') as f:
            db_genom = json.load(f)
        
        selected_display = st.selectbox("Antrean Pasien (HIS):", [f"{p['nama']} - {p['nik']}" for p in db_genom])
        p_name = selected_display.split(" - ")[0]
        p = next(item for item in db_genom if item["nama"] == p_name)

        # DATA DARI PERAWAT (TTV)
        st.markdown("---")
        st.caption("📊 HASIL PEMERIKSAAN PERAWAT")
        v = p['ttv']
        st.markdown(f"""
            <div class="vital-box">
                <b>TD:</b> {v['td']} mmHg<br>
                <b>Nadi:</b> {v['n']} x/mnt<br>
                <b>Antropometri:</b> {v['tb']}cm / {v['bb']}kg
            </div>
        """, unsafe_allow_html=True)

        # INPUT DOKTER
        st.markdown("---")
        st.caption("✍️ ANALISIS DOKTER")
        obat = st.text_input("Rencana Resep:")
        keluhan = st.text_area("Keluhan Utama:", placeholder="Input keluhan...")
        
        # Tombol diubah menjadi "Analisa"
        if st.button("Analisa"):
            st.session_state.run_ai = True
    except:
        st.error("Gagal sinkronisasi HIS.")

# --- 4. MAIN DASHBOARD ---
st.markdown(f"""
<div class="his-header">
    <h2 style="margin:0; color:#1E3A8A;">Clinical Decision Support System</h2>
    <p style="margin:0; color:#64748B;">Integrasi Rekam Medis Elektronik & BGSi Nasional</p>
</div>
""", unsafe_allow_html=True)

if 'run_ai' in st.session_state and st.session_state.run_ai:
    # Menggunakan Spinner yang lebih sederhana untuk mengurangi lag UI
    with st.spinner("Menganalisis..."):
        prompt = f"""
        Identitas: IndoGen-AI Specialist.
        Pasien: {p['nama']} | TTV: {p['ttv']} | Genetik: {p['rsid']}
        Keluhan: {keluhan} | Obat: {obat}

        Berikan Laporan Medis Singkat & Padat:
        1. DIAGNOSIS & PROBABILITAS (%)
        2. FARMAKOGENOMIK: Kecocokan {obat} dengan {p['rsid']}.
        3. NUTRIGENOMIK: Diet personal (Gula merah/tebu kuning jika sesuai klinis).
        4. PASPOR GENOMIK: Pencegahan.

        Vancouver Style.
        """
        try:
            response = model.generate_content(prompt)
            st.markdown(f'<div class="report-card">{response.text}</div>', unsafe_allow_html=True)
            
            st.write("---")
            if st.button("Selesai & Reset"):
                del st.session_state.run_ai
                st.rerun()
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("Pilih profil pasien di sidebar untuk memulai.")
