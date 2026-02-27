import streamlit as st
import google.generativeai as genai
import json

# --- 1. KONFIGURASI ENGINE ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Menggunakan model Gemini 3 Flash Preview
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error("Sistem gagal memverifikasi kredensial API.")

# --- 2. STATE MANAGEMENT ---
if 'analisis_output' not in st.session_state:
    st.session_state.analisis_output = ""

# Fungsi untuk refresh/reset halaman
def reset_session():
    st.session_state.analisis_output = ""
    if 'run_analysis' in st.session_state:
        del st.session_state.run_analysis
    st.rerun()

# --- 3. UI SETTINGS ---
st.set_page_config(page_title="IndoGen-AI | Clinical Dashboard", layout="wide")

st.markdown("""
    <style>
    button[disabled] { cursor: not-allowed !important; opacity: 0.6; }
    .report-card { 
        background-color: #ffffff; 
        padding: 35px; 
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        color: #1e293b;
        line-height: 1.8;
    }
    .patient-header {
        background-color: #f1f5f9;
        padding: 20px;
        border-radius: 8px;
        border-left: 6px solid #1d4ed8;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR: INPUT MEDIS ---
st.sidebar.title("🩺 Rekam Medis & Genomik")
input_mode = st.sidebar.radio("Pilih Sumber Data:", ["Database BGSi", "Input Manual Klinis"])

final_payload = None

if input_mode == "Database BGSi":
    try:
        with open('data_genetik.json', 'r') as f:
            data_pasien = json.load(f)
        selected_name = st.sidebar.selectbox("Pilih Profil Pasien:", [p['nama'] for p in data_pasien])
        p = next(item for item in data_pasien if item["nama"] == selected_name)
        
        st.sidebar.markdown(f"""
        <div class='patient-header'>
        <b>Identitas:</b> {p['nama']}<br>
        <b>Antropometri:</b> {p.get('tb_bb', 'N/A')}<br>
        <b>Diagnosis Awal:</b> {p['kondisi_saat_ini']}
        </div>
        """, unsafe_allow_html=True)
        
        obat_input = st.sidebar.text_input("Resep Obat Aktif:", placeholder="Misal: Metformin 500mg...")
        gejala_input = st.sidebar.text_area("Observasi Klinis Terbaru:", placeholder="Keluhan tambahan atau TD...")
        
        final_payload = {
            "nama": p['nama'], "fisik": p.get('tb_bb', 'N/A'), "rsid": p['rsid_data'],
            "kondisi": p['kondisi_saat_ini'], "obat": obat_input, "tambahan": gejala_input
        }
        
        if st.sidebar.button("Proses Analisis Klinis", use_container_width=True):
            st.session_state.run_analysis = True
    except:
        st.sidebar.error("Database JSON tidak ditemukan.")

else:
    with st.sidebar.form("manual_form"):
        st.write("### Form Input Klinis")
        n = st.text_input("Nama Lengkap")
        f = st.text_input("Antropometri (TB/BB/TD)")
        r = st.text_area("Profil Genetik (RSID)")
        k = st.text_area("Diagnosis Saat Ini")
        o = st.text_input("Resep Obat")
        t = st.text_area("Keluhan/Observasi Baru")
        
        submit = st.form_submit_button("Simpan & Analisis Sekarang", use_container_width=True)
        
        if submit:
            if n and r:
                final_payload = {"nama": n, "fisik": f, "rsid": r, "kondisi": k, "obat": o, "tambahan": t}
                st.session_state.run_analysis = True
            else:
                st.warning("Data Nama dan RSID wajib diisi.")

# --- 5. LOGIKA ANALISIS AI ---
if 'run_analysis' in st.session_state and st.session_state.run_analysis:
    if final_payload:
        with st.spinner("IndoGen-AI: Menganalisis parameter klinis..."):
            prompt = f"""
            Anda adalah IndoGen-AI, sistem pendukung keputusan klinis.
            Data: {final_payload}

            TUGAS ANALISIS (POIN-POIN):
            1. DIAGNOSIS KERJA & PROBABILITAS: Berikan kemungkinan penyakit (persentase %).
            2. EVALUASI FARMAKOGENOMIK: Efektivitas obat terhadap RSID.
            3. RENCANA NUTRIGENOMIK: Diet berbasis genetik. Gunakan gula merah/tebu kuning jika relevan.
            4. PROGNOSIS KLINIS: Risiko berdasarkan fisik dan genetik.

            Bahasa Medis Formal. Vancouver Style (Daftar Pustaka).
            """
            try:
                response = model.generate_content(prompt)
                st.session_state.analisis_output = response.text
                del st.session_state.run_analysis
            except Exception as e:
                st.error(f"Sistem AI Sibuk: {e}")

# --- 6. MAIN DASHBOARD ---
st.title("IndoGen-AI: Dashboard Intervensi Klinis")

if st.session_state.analisis_output:
    # Tampilkan Hasil Analisis
    st.markdown(f'<div class="report-card">{st.session_state.analisis_output}</div>', unsafe_allow_html=True)
    
    # Tombol Refresh / Selesai
    st.write("---")
    if st.button("Selesai & Reset Dashboard", type="primary"):
        reset_session()
else:
    st.info("Sistem siap. Silakan lengkapi parameter klinis di sidebar untuk memulai.")
