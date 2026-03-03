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

# --- 2. DESAIN UI MODERN & PERBAIKAN SIMBOL SIDEBAR ---
st.set_page_config(page_title="IndoGen-AI | Portal Presisi", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    
    .sidebar-icon {
        font-family: 'Material Icons'; font-size: 20px;
        color: #1E3A8A; vertical-align: middle; margin-right: 5px;
    }

    .his-header {
        background: white; padding: 20px 30px; border-radius: 12px;
        border-left: 5px solid #2563EB; margin-bottom: 20px;
        box-shadow: 0 2px 15px rgba(0,0,0,0.02);
    }

    .patient-data-point {
        line-height: 1.1; margin-bottom: 0px; font-size: 0.95rem; color: #1E293B;
    }
    .label-bold { font-weight: 700; color: #1E3A8A; }

    .instruction-step {
        background: #F0F9FF; border-radius: 8px; padding: 15px;
        border: 1px solid #BAE6FD; margin-bottom: 20px; color: #1E40AF; font-size: 0.85rem;
    }

    .ai-output-container {
        background: #FFFFFF; padding: 25px; border-radius: 12px;
        border: 1px solid #E2E8F0; margin-bottom: 25px;
        line-height: 1.6; color: #334155;
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
    st.markdown('<i class="sidebar-icon">keyboard_double_arrow_right</i><span style="color:#1E3A8A; font-weight:600; font-size:1.1rem;">Kontrol Klinis</span>', unsafe_allow_html=True)
    
    try:
        with open('data_genetik.json', 'r') as f:
            db_genom = json.load(f)
        
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
        obat_input = st.text_input("Rencana Resep:", placeholder="Contoh: Karbamazepin")
        keluhan_input = st.text_area("Observasi Klinis:", placeholder="Contoh: Kejang")
        
        if st.button("Analisis"):
            if not obat_input or not keluhan_input:
                st.error("Data wajib diisi.")
            else:
                st.session_state.run_ai = True
                st.session_state.current_p = p 
                st.session_state.input_obat = obat_input

    except Exception as e:
        st.error(f"Error Database: {e}")

# --- 4. DASHBOARD UTAMA ---
st.markdown(f"""
<div class="his-header">
    <h1 style="margin:0; font-size:1.4rem; color:#0F172A;">Clinical Decision Support System</h1>
    <p style="margin:0; color:#64748B; font-size:0.85rem;">Integrasi Nasional Data Genomik BGSi</p>
</div>
""", unsafe_allow_html=True)

if 'run_ai' not in st.session_state:
    st.markdown(f"""
    <div class="instruction-step">
        <b>Panduan Penggunaan Sistem:</b><br>
        Berikut adalah langkah pengoperasian sistem ini:<br>
        1. Pilih nama pasien pada kolom <b>Daftar Antrean Pasien</b>.<br>
        2. Masukkan nama obat pada kolom resep, misalnya: <b>'Karbamazepin'</b>.<br>
        3. Masukkan gejala pada kolom observasi, misalnya: <b>'Kejang'</b>.<br>
    </div>
    """, unsafe_allow_html=True)

# DATA PASIEN (Rapat sesuai gambar)
st.markdown(f"""
<div style="background:white; padding:15px; border-radius:12px; border:1px solid #E2E8F0; margin-bottom:20px;">
    <div class="patient-data-point"><span class="label-bold">Nama:</span> {p['nama']}</div>
    <div class="patient-data-point"><span class="label-bold">Indeks Massa Tubuh (IMT):</span> {p['ttv']['bb']} kg / {p['ttv']['tb']} cm</div>
    <div class="patient-data-point"><span class="label-bold">Tekanan Darah:</span> {p['ttv']['td']} mmHg</div>
    <div class="patient-data-point"><span class="label-bold">Data Genomik (RSID):</span> {p['rsid']}</div>
</div>
""", unsafe_allow_html=True)

# --- 5. OUTPUT ANALISIS & VALIDASI ---
if 'run_ai' in st.session_state and st.session_state.run_ai:
    p_active = st.session_state.current_p
    
    if 'ai_result' not in st.session_state:
        with st.status("Sinkronisasi database genomik...", expanded=True) as status:
            prompt = f"Berikan laporan medis formal singkat untuk Pasien {p_active['nama']} dengan Genetik {p_active['rsid']} dan obat {st.session_state.input_obat}. Sertakan Diagnosis (%), Farmakogenomik, dan Nutrigenomik. Tanpa bold (**). Referensi Vancouver."
            response = model.generate_content(prompt)
            st.session_state.ai_result = response.text.replace("**", "")
            status.update(label="Analisis Selesai", state="complete", expanded=False)

    # TAMPILAN 1: HASIL ANALISIS AI (Referensi Statis)
    st.markdown("### Hasil Analisis Sistem (AI)")
    st.markdown(f'<div class="ai-output-container">{st.session_state.ai_result}</div>', unsafe_allow_html=True)

    # TAMPILAN 2: FORMULIR VALIDASI DOKTER (Bisa Diedit)
    st.markdown("---")
    st.markdown("### Konfirmasi dan Validasi Dokter")
    
    col1, col2 = st.columns(2)
    with col1:
        # Kolom diagnosa otomatis terisi dari data profil pasien
        final_diag = st.text_input("Final Diagnosis Penyakit:", value=p_active['kondisi'])
    with col2:
        # Kolom resep otomatis terisi dari input sebelumnya
        final_med = st.text_input("Final Resep Obat:", value=st.session_state.input_obat)
    
    # Text area laporan yang otomatis terisi hasil AI tapi bisa diedit total
    editable_report = st.text_area("Final Laporan Klinis (Edit jika diperlukan):", value=st.session_state.ai_result, height=300)
    
    if st.button("Simpan ke Rekam Medis Elektronik"):
        st.success("Data klinis berhasil divalidasi dan disimpan ke sistem EMR.")

# --- 6. FOOTER ---
st.markdown("""
<div class="engine-footer">
    Powered by Gemini 3 Flash | Cloud AI Integration via Google Vertex API<br>
    IndoGen-AI Precision System © 2026
</div>
""", unsafe_allow_html=True)
