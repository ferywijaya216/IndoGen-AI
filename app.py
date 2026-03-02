import streamlit as st
import google.generativeai as genai
import json

# --- 1. CONFIG ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error("API Error: Periksa Secrets.")

# --- 2. THEME DESIGN (WHITE PREMIUM + 3D SHADOWS) ---
st.set_page_config(page_title="IndoGen-AI | Clinical Portal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    
    /* Header HIS Premium */
    .his-header {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border-bottom: 5px solid #3B82F6; margin-bottom: 30px;
    }

    /* 3D Glassmorphism Effect for Report */
    .report-card { 
        background: white; padding: 40px; border-radius: 25px;
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 20px 20px 60px #d9d9d9, -20px -20px 60px #ffffff;
        line-height: 1.9; font-family: 'Inter', sans-serif;
    }

    /* Vital Sign Display (Nurse Input) */
    .vital-box {
        background: #F1F5F9; padding: 15px; border-radius: 12px;
        border-left: 5px solid #3B82F6; margin-bottom: 10px;
    }

    /* Premium Button */
    .stButton>button {
        background: linear-gradient(145deg, #3b82f6, #2563eb);
        color: white; border-radius: 12px; border: none;
        padding: 15px; font-weight: bold; width: 100%;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.1);
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

        # DATA DARI PERAWAT (TTV) - Muncul otomatis sesuai permintaan Anda
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
        keluhan = st.text_area("Keluhan Utama Pasien:", placeholder="Pasien mengeluh...")
        
        if st.button("JALANKAN ANALISIS PRESISI"):
            st.session_state.run_ai = True
    except:
        st.error("Gagal sinkronisasi Database HIS.")

# --- 4. MAIN DASHBOARD ---
st.markdown(f"""
<div class="his-header">
    <h2 style="margin:0; color:#1E3A8A;">Clinical Decision Support System</h2>
    <p style="margin:0; color:#64748B;">Integrasi Nasional: Rekam Medis Elektronik & BioGenome Science Initiative (BGSi)</p>
</div>
""", unsafe_allow_html=True)

if 'run_ai' in st.session_state and st.session_state.run_ai:
    with st.spinner("IndoGen-AI sedang melakukan komputasi genomik..."):
        prompt = f"""
        Identitas: IndoGen-AI Specialist.
        Pasien: {p['nama']} | TTV: {p['ttv']}
        Kondisi: {p['kondisi']} | RSID: {p['rsid']}
        Keluhan: {keluhan} | Obat: {obat}

        Berikan Laporan Medis (Format Poin-Poin Profesional):
        1. DIAGNOSIS KERJA & PROBABILITAS: % akurasi berdasarkan integrasi klinis + genetik.
        2. FARMAKOGENOMIK: Kecocokan {obat} dengan {p['rsid']}.
        3. NUTRIGENOMIK: Diet personal. (Gunakan gula merah/tebu kuning jika sesuai klinis).
        4. PASPOR GENOMIK: Prognosis jangka panjang.

        Gunakan Bahasa Medis Formal. Referensi Vancouver.
        """
        try:
            response = model.generate_content(prompt)
            st.markdown(f'<div class="report-card">{response.text}</div>', unsafe_allow_html=True)
            
            if st.button("Selesai & Reset Sesi"):
                del st.session_state.run_ai
                st.rerun()
        except Exception as e:
            st.error(f"AI Error: {e}")
else:
    st.info("Pilih profil pasien di sidebar untuk menampilkan data vital dan memulai analisis kesehatan presisi.")
