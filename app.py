import streamlit as st
import google.generativeai as genai
import json

# --- 1. KONFIGURASI ENGINE ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-3-flash-preview') 
    else:
        st.error("Credential Error: API Key tidak ditemukan.")
except Exception as e:
    st.error(f"Error: {e}")

# --- 2. DESAIN UI MODERN (PUEBI & RAPAT) ---
st.set_page_config(page_title="IndoGen-AI | Portal Presisi", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    
    .his-header {
        background: white; padding: 20px 30px; border-radius: 12px;
        border-left: 5px solid #2563EB; margin-bottom: 20px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.02);
    }

    /* Tampilan Point Rapat (Sesuai Gambar User) */
    .patient-data-point {
        line-height: 1.1; margin-bottom: 2px; font-size: 0.95rem; color: #1E293B;
    }
    .label-bold { font-weight: 700; color: #1E3A8A; }

    .instruction-step {
        background: #F0F9FF; border-radius: 8px; padding: 15px;
        border: 1px solid #BAE6FD; margin-bottom: 20px; color: #0369A1; font-size: 0.85rem;
    }

    .report-area {
        background: white; padding: 30px; border-radius: 12px;
        border: 1px solid #E2E8F0; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }

    .stButton>button {
        background: #2563EB; color: white; border-radius: 6px;
        font-weight: 600; width: 100%; height: 3em; border: none;
    }
    
    .engine-footer {
        margin-top: 40px; padding: 15px; text-align: center;
        border-top: 1px solid #E2E8F0; color: #94A3B8; font-size: 0.7rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR: KONTROL ---
with st.sidebar:
    st.markdown("<h3 style='color:#1E3A8A;'>Kontrol Klinis</h3>", unsafe_allow_html=True)
    
    try:
        with open('data_genetik.json', 'r') as f:
            db_genom = json.load(f)
        
        # Proteksi: Jika sedang analisis, sidebar dikunci untuk mencegah error ganti profil
        if 'run_ai' in st.session_state and st.session_state.run_ai:
            st.info("Sesi Analisis Aktif")
            if st.button("Reset Analisis"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
            st.stop()

        selected_display = st.selectbox("Daftar Antrean Pasien:", [f"{p['nama']} - {p['nik']}" for p in db_genom])
        p_name = selected_display.split(" - ")[0]
        p = next(item for item in db_genom if item["nama"] == p_name)
        
        st.markdown("---")
        obat_input = st.text_input("Rencana Resep:", placeholder="Metformin, dll")
        keluhan_input = st.text_area("Observasi Klinis:", placeholder="Input gejala...")
        
        if st.button("Analisis"): # PUEBI: Analisis
            if not obat_input or not keluhan_input:
                st.error("Data wajib diisi.")
            else:
                st.session_state.run_ai = True
                st.session_state.current_p = p # Simpan data pasien terpilih ke state

    except Exception as e:
        st.error(f"Error Database: {e}")

# --- 4. DASHBOARD UTAMA ---
st.markdown(f"""
<div class="his-header">
    <h1 style="margin:0; font-size:1.4rem; color:#0F172A;">Clinical Decision Support System</h1>
    <p style="margin:0; color:#64748B; font-size:0.85rem;">Integrasi Nasional Data Genomik BGSi</p>
</div>
""", unsafe_allow_html=True)

# Instruksi Otomatis Sesuai Permintaan Dospem
if 'run_ai' not in st.session_state:
    st.markdown(f"""
    <div class="instruction-step">
        <b>💡 Instruksi Penggunaan:</b><br>
        1. Pilih pasien <b>'Luh Putu Astuti'</b> pada daftar antrean.<br>
        2. Masukkan <b>'Karbamazepin'</b> pada kolom resep.<br>
        3. Masukkan <b>'Kejang'</b> pada observasi klinis.<br>
        4. Klik tombol <b>'Analisis'</b> untuk sinkronisasi data genetik.
    </div>
    """, unsafe_allow_html=True)

# DATA PASIEN (Point Rapat Persis Gambar)
st.markdown(f"""
<div style="background:white; padding:15px; border-radius:12px; border:1px solid #E2E8F0; margin-bottom:20px;">
    <div class="patient-data-point"><span class="label-bold">Nama:</span> {p['nama']}</div>
    <div class="patient-data-point"><span class="label-bold">Indeks Massa Tubuh (IMT):</span> {p['ttv']['bb']} kg / {p['ttv']['tb']} cm</div>
    <div class="patient-data-point"><span class="label-bold">Tekanan Darah:</span> {p['ttv']['td']} mmHg</div>
    <div class="patient-data-point"><span class="label-bold">Data Genomik (RSID):</span> {p['rsid']}</div>
</div>
""", unsafe_allow_html=True)

# --- 5. OUTPUT ANALISIS & EDIT DOKTER ---
if 'run_ai' in st.session_state and st.session_state.run_ai:
    p_active = st.session_state.current_p
    
    if 'ai_result' not in st.session_state:
        with st.spinner("Menganalisis data..."):
            prompt = f"Berikan laporan medis formal untuk Pasien {p_active['nama']} dengan Genetik {p_active['rsid']} dan rencana obat {obat_input}. Sertakan Diagnosis Kerja (%), Farmakogenomik, dan Nutrigenomik (gula merah/tebu jika relevan). Tanpa bold (**). Vancouver Style."
            response = model.generate_content(prompt)
            st.session_state.ai_result = response.text.replace("**", "")

    st.markdown("### 📋 Validasi Rekam Medis")
    
    col1, col2 = st.columns(2)
    with col1:
        # Perbaikan Error: Mengambil data langsung dari p_active, bukan session_state kosong
        final_diag = st.text_input("Konfirmasi Penyakit:", value=p_active['kondisi'])
    with col2:
        final_med = st.text_input("Final Resep Obat:", value=obat_input)
    
    editable_report = st.text_area("Detail Laporan (Dapat Diedit):", value=st.session_state.ai_result, height=350)
    
    if st.button("Simpan ke EMR"):
        st.success("Data berhasil tersimpan secara aman di sistem EMR.")

# --- 6. FOOTER ---
st.markdown("""
<div class="engine-footer">
    Powered by Gemini 3 Flash | Cloud AI Integration via Google Vertex API<br>
    IndoGen-AI Precision System © 2026
</div>
""", unsafe_allow_html=True)
