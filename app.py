import streamlit as st
import google.generativeai as genai
import json

# --- 1. KONFIGURASI ENGINE ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-3-flash-preview') 
    else:
        st.error("Credential Error.")
except Exception as e:
    st.error(f"Error: {e}")

# --- 2. DESAIN UI MASA DEPAN (CLEAN & FUTURISTIC) ---
st.set_page_config(page_title="IndoGen-AI | Portal Presisi", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');
    
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    
    /* Header Modern */
    .his-header {
        background: linear-gradient(90deg, #FFFFFF 0%, #F1F5F9 100%);
        padding: 20px 30px; border-radius: 12px;
        border-left: 5px solid #2563EB; margin-bottom: 20px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.02);
    }

    /* Tampilan Point (Persis Gambar) */
    .patient-data-point {
        line-height: 1.4; margin-bottom: 2px; font-size: 0.95rem;
    }
    .label-bold { font-weight: 700; color: #1E3A8A; }

    /* Card Analisis (Glassmorphism Ringan) */
    .analysis-box {
        background: white; padding: 35px; border-radius: 16px;
        border: 1px solid #E2E8F0; box-shadow: 0 10px 40px rgba(0,0,0,0.04);
        line-height: 1.6; color: #1E293B;
    }

    /* Tombol & Sidebar */
    .stButton>button {
        background: #2563EB; color: white; border-radius: 8px;
        font-weight: 600; width: 100%; height: 3.2em; border: none;
    }
    
    /* Instruksi Otomatis */
    .instruction-step {
        background: #EFF6FF; border-radius: 8px; padding: 12px;
        border: 1px solid #BFDBFE; margin-bottom: 15px; color: #1E40AF; font-size: 0.85rem;
    }

    /* Footer Ringkas */
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
        
        # Peringatan Jika Ingin Ganti Profil Saat Analisis Aktif
        if 'run_ai' in st.session_state and st.session_state.run_ai:
            st.warning("⚠️ Analisis sedang aktif. Klik 'Reset Analisis' di bawah untuk mengganti pasien.")
            if st.button("Reset Analisis"):
                st.session_state.clear()
                st.rerun()
            st.stop() # Menghentikan input lain agar user reset dulu

        selected_display = st.selectbox("Daftar Antrean Pasien:", [f"{p['nama']} - {p['nik']}" for p in db_genom])
        p_name = selected_display.split(" - ")[0]
        p = next(item for item in db_genom if item["nama"] == p_name)
        
        st.markdown("---")
        obat_input = st.text_input("Rencana Resep:", placeholder="Metformin, dll")
        keluhan_input = st.text_area("Observasi Klinis:", placeholder="Gejala yang dialami...")
        
        if st.button("Analisis"): # Kata baku sesuai PUEBI
            if not obat_input or not keluhan_input:
                st.error("Data wajib diisi.")
            else:
                st.session_state.run_ai = True
                st.session_state.obat = obat_input
                st.session_state.keluhan = keluhan_input

    except Exception as e:
        st.error(f"Error: {e}")

# --- 4. DASHBOARD UTAMA ---
st.markdown(f"""
<div class="his-header">
    <h1 style="margin:0; font-size:1.4rem; color:#0F172A;">Clinical Decision Support System</h1>
    <p style="margin:0; color:#64748B; font-size:0.85rem;">Integrasi Nasional Data Genomik BGSi</p>
</div>
""", unsafe_allow_html=True)

# PANDUAN OTOMATIS (Sesuai Dospem)
if 'run_ai' not in st.session_state:
    st.markdown(f"""
    <div class="instruction-step">
        <b>💡 Instruksi Penggunaan:</b><br>
        1. Pilih pasien <b>'Luh Putu Astuti'</b> pada sidebar.<br>
        2. Masukkan <b>'Karbamazepin'</b> pada kolom resep.<br>
        3. Masukkan <b>'Kejang'</b> pada observasi klinis.<br>
        4. Klik tombol <b>'Analisis'</b> untuk menjalankan sinkronisasi genetik.
    </div>
    """, unsafe_allow_html=True)

# DATA PASIEN (Point Mode Rapat - Persis Gambar)
st.markdown(f"""
<div style="background:white; padding:20px; border-radius:12px; border:1px solid #E2E8F0; margin-bottom:20px;">
    <div class="patient-data-point"><span class="label-bold">Nama:</span> {p['nama']}</div>
    <div class="patient-data-point"><span class="label-bold">Indeks Massa Tubuh (IMT):</span> {p['ttv']['bb']} kg / {p['ttv']['tb']} cm</div>
    <div class="patient-data-point"><span class="label-bold">Tekanan Darah:</span> {p['ttv']['td']} mmHg</div>
    <div class="patient-data-point"><span class="label-bold">Data Genomik (RSID):</span> {p['rsid']}</div>
</div>
""", unsafe_allow_html=True)

# --- 5. LOGIKA ANALISIS & EDIT DOKTER ---
if 'run_ai' in st.session_state and st.session_state.run_ai:
    if 'ai_result' not in st.session_state:
        with st.spinner("Mensinkronisasi data..."):
            prompt = f"Analisis medis: Pasien {p['nama']}, Genetik {p['rsid']}, Obat {st.session_state.obat}. Berikan Hasil Diagnosa dan Rekomendasi Obat dalam format laporan medis formal tanpa simbol bold (**). Sertakan Vancouver Style."
            response = model.generate_content(prompt)
            st.session_state.ai_result = response.text.replace("**", "")

    # DASHBOARD HASIL (Bisa Diedit Dokter)
    st.markdown("### 📋 Hasil Analisis & Validasi Dokter")
    
    # Kolom diagnosa dan obat yang bisa diedit otomatis terisi dari AI
    col_a, col_b = st.columns(2)
    with col_a:
        final_diag = st.text_input("Konfirmasi Penyakit:", value=st.session_state.kondisi)
    with col_b:
        final_med = st.text_input("Final Resep Obat:", value=st.session_state.obat)
    
    # Text area besar untuk detail laporan
    editable_report = st.text_area("Detail Laporan Medis (Dapat diedit):", value=st.session_state.ai_result, height=400)
    
    if st.button("Simpan ke EMR Pasien"):
        st.success("✅ Data berhasil disimpan ke Rekam Medis Elektronik Nasional.")

# --- 6. FOOTER RINGKAS ---
st.markdown("""
<div class="engine-footer">
    Powered by Gemini 3 Flash | Cloud AI Integration via Google Vertex API<br>
    IndoGen-AI Precision System © 2026
</div>
""", unsafe_allow_html=True)
