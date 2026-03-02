import streamlit as st
import google.generativeai as genai
import json

# --- 1. KONFIGURASI ENGINE ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-3-flash-preview') 
    else:
        st.error("API Key tidak ditemukan di Secrets.")
except Exception as e:
    st.error(f"Koneksi AI Gagal: {e}")

# --- 2. DESAIN PREMIUM WHITE & 3D SHADOWS ---
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

# --- 3. SIDEBAR (EMR INTEGRATION) ---
with st.sidebar:
    st.markdown("### **Portal Klinis IndoGen-AI**")
    
    try:
        with open('data_genetik.json', 'r') as f:
            db_genom = json.load(f)
        
        selected_display = st.selectbox("Antrean Pasien (HIS):", [f"{p['nama']} - {p['nik']}" for p in db_genom])
        p_name = selected_display.split(" - ")[0]
        p = next(item for item in db_genom if item["nama"] == p_name)

        # DATA DARI PERAWAT
        st.markdown("---")
        st.caption("📊 STATUS PRA-KONSULTASI")
        v = p['ttv']
        st.markdown(f"""
            <div class="vital-box">
                <b>TD:</b> {v['td']} mmHg<br>
                <b>Nadi:</b> {v['n']} x/mnt<br>
                <b>TB/BB:</b> {v['tb']}cm / {v['bb']}kg
            </div>
        """, unsafe_allow_html=True)

        # INPUT DOKTER
        st.markdown("---")
        st.caption("✍️ ANALISIS DOKTER")
        obat = st.text_input("Rencana Resep:")
        keluhan = st.text_area("Keluhan Utama:")
        
        if st.button("Analisa"):
            st.session_state.run_ai = True
    except Exception as e:
        st.error(f"Error Database: {e}")

# --- 4. DASHBOARD UTAMA ---
st.markdown(f"""
<div class="his-header">
    <h2 style="margin:0; color:#1E3A8A;">Clinical Decision Support System</h2>
    <p style="margin:0; color:#64748B;">Sistem Integrasi Nasional BGSi & Rekam Medis Elektronik</p>
</div>
""", unsafe_allow_html=True)

if 'run_ai' in st.session_state and st.session_state.run_ai:
    with st.spinner("Menganalisis..."):
        prompt = f"""
        Identitas: IndoGen-AI Specialist.
        Pasien: {p['nama']} | TTV: {p['ttv']} | Genetik: {p['rsid']}
        Keluhan: {keluhan} | Obat: {obat}
        Instruksi: Berikan laporan diagnosis, farmakogenomik, nutrigenomik (termasuk gula merah/tebu kuning jika relevan), dan paspor genomik.
        Gunakan Bahasa Medis Formal & Vancouver Style.
        """
        try:
            response = model.generate_content(prompt)
            st.markdown(f'<div class="report-card">{response.text}</div>', unsafe_allow_html=True)
            
            if st.button("Selesai & Reset"):
                del st.session_state.run_ai
                st.rerun()
        except Exception as e:
            st.error(f"Gagal memproses AI: {e}")
else:
    st.info("Silakan pilih pasien dan klik tombol Analisa.")
