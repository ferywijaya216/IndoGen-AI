import streamlit as st
import google.generativeai as genai
import json

# --- 1. KONFIGURASI ENGINE ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Menggunakan model paling mutakhir
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error("Sistem gagal memverifikasi kredensial API.")

# --- 2. STATE MANAGEMENT ---
if 'analisis_selesai' not in st.session_state:
    st.session_state.analisis_selesai = ""

# --- 3. UI SETTINGS ---
st.set_page_config(page_title="IndoGen-AI | Clinical Dashboard", layout="wide")

st.markdown("""
    <style>
    button[disabled] { cursor: not-allowed !important; opacity: 0.6; }
    .report-card { 
        background-color: #f8fafc; 
        padding: 30px; 
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        color: #1e293b;
        font-size: 14px;
    }
    .patient-info {
        background-color: #eff6ff;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        border-left: 5px solid #2563eb;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR: REKAM MEDIS ---
st.sidebar.title("🩺 Rekam Medis & Genomik")
input_mode = st.sidebar.radio("Metode Input Data:", ["Database BGSi", "Input Manual Klinis"])

target_data = {}

if input_mode == "Database BGSi":
    try:
        with open('data_genetik.json', 'r') as f:
            data_pasien = json.load(f)
        selected_name = st.sidebar.selectbox("Pilih Profil Pasien:", [p['nama'] for p in data_pasien])
        p = next(item for item in data_pasien if item["nama"] == selected_name)
        
        # Menampilkan Detail Fisik Sesuai Data
        st.sidebar.markdown(f"""
        <div class='patient-info'>
        <b>Pasien:</b> {p['nama']}<br>
        <b>Fisik:</b> {p.get('tb_bb', 'N/A')}<br>
        <b>Kondisi:</b> {p['kondisi_saat_ini']}<br>
        <b>Risiko:</b> {p.get('keterangan_risiko', 'N/A')}
        </div>
        """, unsafe_allow_html=True)
        
        obat = st.sidebar.text_input("Resep Obat Saat Ini:", placeholder="Contoh: Metformin 500mg...")
        keluhan = st.sidebar.text_area("Observasi Tambahan:", placeholder="Gejala atau Tekanan Darah...")
        
        target_data = {
            "nama": p['nama'], "fisik": p.get('tb_bb', 'N/A'), "rsid": p['rsid_data'],
            "kondisi": p['kondisi_saat_ini'], "obat": obat, "tambahan": keluhan
        }
    except:
        st.sidebar.error("Database tidak ditemukan.")

else:
    with st.sidebar.form("form_manual"):
        st.write("Formulir Klinis Manual")
        n = st.text_input("Nama Pasien")
        f = st.text_input("TB / BB / TD (Tekanan Darah)")
        r = st.text_area("Data RSID (SNP)")
        k = st.text_area("Diagnosis Klinis")
        o = st.text_input("Rencana Resep Obat")
        t = st.text_area("Keluhan Tambahan")
        
        if st.form_submit_button("Simpan Data"):
            target_data = {"nama": n, "fisik": f, "rsid": r, "kondisi": k, "obat": o, "tambahan": t}
            st.sidebar.success("Data Siap.")

# --- TOMBOL ANALISIS DI SIDEBAR ---
if target_data:
    if st.sidebar.button("Analisis", use_container_width=True):
        with st.spinner("Menganalisis profil farmakogenomik..."):
            prompt = f"""
            Anda adalah IndoGen-AI, asisten klinis profesional.
            Analisis data pasien:
            - Nama: {target_data['nama']} | Fisik/TD: {target_data['fisik']}
            - Diagnosis: {target_data['kondisi']}
            - Obat: {target_data['obat']}
            - RSID: {target_data['rsid']}
            - Catatan: {target_data['tambahan']}

            TUGAS:
            1. EVALUASI OBAT: Apakah resep {target_data['obat']} efektif berdasarkan RSID pasien? Berikan saran dosis atau alternatif jika ada risiko inefektivitas.
            2. INTERVENSI NUTRIGENOMIK: Rekomendasi diet menyeluruh. Gunakan info gula merah/tebu kuning HANYA jika relevan dengan kondisi glikemik.
            3. TINJAUAN KLINIS: Hubungkan hasil fisik (TB/BB/TD) dengan risiko genetik.

            Gunakan bahasa medis formal, tanpa emotikon. Referensi Vancouver (langsung daftar pustaka).
            """
            try:
                # Menggunakan Gemini 3 Flash Preview
                response = model.generate_content(prompt)
                st.session_state.analisis_selesai = response.text
            except Exception as e:
                st.error(f"Error: {e}")

# --- 5. MAIN DASHBOARD ---
st.title("IndoGen-AI: Dashboard Intervensi Klinis")
if st.session_state.analisis_selesai:
    st.markdown(f'<div class="report-card">{st.session_state.analisis_selesai}</div>', unsafe_allow_html=True)
else:
    st.info("Silakan lengkapi data pasien di sidebar dan klik 'Analisis' untuk memulai.")
