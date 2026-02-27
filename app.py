import streamlit as st
import google.generativeai as genai
import json

# --- 1. KONFIGURASI ENGINE ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    # Menggunakan model Gemini 3 Flash Preview sesuai hasil pengecekan Anda
    model = genai.GenerativeModel('gemini-3-flash-preview') 
except Exception as e:
    st.error("Sistem gagal memverifikasi kredensial API.")

# --- 2. STATE MANAGEMENT ---
if 'analisis_output' not in st.session_state:
    st.session_state.analisis_output = ""

# --- 3. UI SETTINGS ---
st.set_page_config(page_title="IndoGen-AI | Clinical Dashboard", layout="wide")

st.markdown("""
    <style>
    /* Kursor terlarang saat loading */
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
    h3 { color: #1e40af; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }
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
        
        # Penyatuan Tombol Simpan & Analisis
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
        with st.spinner("IndoGen-AI: Sinkronisasi data farmakogenomik dan parameter klinis..."):
            prompt = f"""
            Anda adalah IndoGen-AI, sistem pendukung keputusan klinis tingkat lanjut.
            Data Pasien: {final_payload['nama']} | Fisik: {final_payload['fisik']}
            Kondisi Saat Ini: {final_payload['kondisi']}
            Observasi Tambahan: {final_payload['tambahan']}
            Resep Obat: {final_payload['obat']}
            Data RSID: {final_payload['rsid']}

            TUGAS ANALISIS (FORMAT POIN-POIN PROFESIONAL):
            1. DIAGNOSIS KERJA & PROBABILITAS: Berdasarkan diagnosis awal dan observasi tambahan, berikan kemungkinan penyakit (persentase probabilitas).
            2. EVALUASI FARMAKOGENOMIK: Analisis efektivitas {final_payload['obat']} terhadap RSID. Berikan rekomendasi 'Lanjutkan', 'Sesuaikan Dosis', atau 'Ganti Obat'.
            3. RENCANA NUTRIGENOMIK: Strategi diet berbasis genetik. Sertakan penggunaan gula merah atau gula pasir tebu (kuning) HANYA jika relevan secara klinis.
            4. PROGNOSIS: Analisis risiko jangka panjang berdasarkan parameter antropometri dan genetik.

            Gunakan Bahasa Medis Formal. Sertakan Referensi Vancouver langsung di bagian akhir.
            """
            try:
                # Menggunakan model Gemini 3 Flash Preview
                response = model.generate_content(prompt)
                st.session_state.analisis_output = response.text
                del st.session_state.run_analysis
            except Exception as e:
                st.error(f"Kegagalan Sistem AI: {e}")

# --- 6. DISPLAY DASHBOARD ---
st.title("IndoGen-AI: Dashboard Intervensi Klinis")
if st.session_state.analisis_output:
    st.markdown(f'<div class="report-card">{st.session_state.analisis_output}</div>', unsafe_allow_html=True)
else:
    st.info("Sistem siap. Silakan lengkapi parameter klinis di sidebar untuk memulai analisis.")
