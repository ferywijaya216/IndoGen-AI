import streamlit as st
import google.generativeai as genai
import json

# --- 1. KONFIGURASI ENGINE ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Menggunakan Gemini 3 Flash untuk kecepatan respon maksimal
        model = genai.GenerativeModel('gemini-3-flash-preview') 
    else:
        st.error("Kesalahan Kredensial: API Key tidak terkonfigurasi.")
except Exception as e:
    st.error(f"Kesalahan Sistem: {e}")

# --- 2. DESAIN ANTARMUKA MEDIS PREMIUM ---
st.set_page_config(page_title="IndoGen-AI | Portal Kedokteran Presisi", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    
    /* Header HIS Premium */
    .his-header {
        background: white; padding: 30px; border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 6px solid #2563EB; margin-bottom: 25px;
    }

    /* Kotak Panduan Reviewer */
    .guide-box {
        background: #F1F5F9; padding: 20px; border-radius: 10px;
        border: 1px solid #E2E8F0; margin-bottom: 25px;
        font-size: 0.9rem; color: #475569;
    }

    /* Kartu Data Pasien */
    .patient-card {
        background: white; padding: 30px; border-radius: 12px;
        border: 1px solid #E2E8F0; margin-bottom: 25px;
    }

    .info-label { color: #94A3B8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .info-value { color: #0F172A; font-size: 1rem; font-weight: 500; margin-bottom: 15px; }

    /* Area Laporan Klinis */
    .clinical-report { 
        background: white; padding: 50px; border-radius: 12px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05);
        border: 1px solid #E2E8F0; line-height: 1.8; color: #1E293B;
        white-space: pre-wrap;
    }

    /* Tombol Analisa */
    .stButton>button {
        background: #2563EB; color: white; border-radius: 6px;
        font-weight: 600; width: 100%; height: 3.5em; border: none;
    }
    .stButton>button:hover { background: #1D4ED8; }

    /* Footer Informasi Mesin AI */
    .engine-footer {
        margin-top: 50px; padding: 20px; text-align: center;
        border-top: 1px solid #E2E8F0; color: #94A3B8; font-size: 0.75rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR: KONTROL INPUT ---
with st.sidebar:
    st.markdown("<h2 style='color:#1E3A8A; font-size:1.2rem;'>Kontrol Sistem</h2>", unsafe_allow_html=True)
    try:
        with open('data_genetik.json', 'r') as f:
            db_genom = json.load(f)
        
        selected_display = st.selectbox("Pilih Rekam Medis Pasien:", [f"{p['nama']} - {p['nik']}" for p in db_genom])
        p_name = selected_display.split(" - ")[0]
        p = next(item for item in db_genom if item["nama"] == p_name)
        
        st.markdown("---")
        obat = st.text_input("Rencana Resep Obat:", placeholder="Contoh: Warfarin")
        keluhan = st.text_area("Observasi Klinis/Keluhan:", placeholder="Contoh: Nyeri dada berkala")
        
        if st.button("Analisa"):
            if not obat or not keluhan:
                st.error("Data Diperlukan: Mohon isi resep dan keluhan.")
            else:
                st.session_state.run_ai = True
        
        if st.button("Reset Sesi"):
            st.session_state.clear()
            st.rerun()

    except Exception as e:
        st.error(f"Gagal Sinkronisasi Database: {e}")

# --- 4. DASHBOARD UTAMA ---
st.markdown(f"""
<div class="his-header">
    <h1 style="margin:0; font-size:1.5rem; color:#0F172A;">Clinical Decision Support System (CDSS)</h1>
    <p style="margin:0; color:#64748B; font-size:0.9rem;">Integrasi Kedokteran Presisi | Pertukaran Data Nasional BGSi</p>
</div>
""", unsafe_allow_html=True)

# PANDUAN SIMULASI UNTUK REVIEWER (Sesuai Revisi Dospem)
st.markdown(f"""
<div class="guide-box">
    <b>Panduan Simulasi Reviewer:</b><br>
    Untuk menguji integrasi genetik-klinis: (1) Pilih <b>'Luh Putu Astuti'</b> pada sidebar. (2) Masukkan <b>'Karbamazepin'</b> pada kolom resep. (3) Masukkan <b>'Kejang berulang'</b> pada observasi. (4) Klik <b>'Analisa'</b> untuk melihat deteksi otomatis risiko fatal akibat varian genetik.
</div>
""", unsafe_allow_html=True)

# GRID PROFIL PASIEN (Tampilan Point Rapi)

with st.container():
    st.markdown('<div class="patient-card">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<p class="info-label">Nama Pasien</p><p class="info-value">{p["nama"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-label">Nomor Identitas (NIK)</p><p class="info-value">{p["nik"]}</p>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<p class="info-label">Diagnosis Utama</p><p class="info-value">{p["kondisi"]}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-label">Marker Genomik (RSID)</p><p class="info-value">{p["rsid"]}</p>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<p class="info-label">Tekanan Darah</p><p class="info-value">{p["ttv"]["td"]} mmHg</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-label">Denyut Nadi</p><p class="info-value">{p["ttv"]["n"]} bpm</p>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<p class="info-label">Berat Badan</p><p class="info-value">{p["ttv"]["bb"]} kg</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-label">Tinggi Badan</p><p class="info-value">{p["ttv"]["tb"]} cm</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. OUTPUT LAPORAN KLINIS ---
if 'run_ai' in st.session_state and st.session_state.run_ai:
    with st.spinner("Memproses sinkronisasi data klinis dan dataset genomik..."):
        # Prompt dioptimalkan untuk hasil teks bersih tanpa format AI yang mencolok
        prompt = f"""
        Lakukan analisis kasus klinis berikut secara profesional:
        Pasien: {p['nama']}
        Tanda Vital: {p['ttv']}
        Profil Genomik: {p['rsid']}
        Diagnosis Klinis: {p['kondisi']}
        Keluhan Saat Ini: {keluhan}
        Rencana Pengobatan: {obat}

        Struktur Laporan:
        1. Diagnosis Banding & Probabilitas (%)
        2. Analisis Farmakogenomik (Interaksi Obat-Gen)
        3. Strategi Nutrigenomik (Sertakan rekomendasi gula tebu kuning atau gula merah hanya jika relevan secara metabolik)
        4. Paspor Genomik (Langkah preventif jangka panjang)

        Gaya Bahasa: Laporan Medis Formal. Tanpa tanda bold (**). Gunakan format Referensi Vancouver.
        """
        try:
            response = model.generate_content(prompt)
            # Membersihkan sisa-sisa format bold jika AI masih bandel mengeluarkannya
            clean_text = response.text.replace("**", "")
            st.markdown(f'<div class="clinical-report">{clean_text}</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Analisis Terhenti: {e}")

# --- 6. FOOTER INFORMASI SISTEM ---
st.markdown("""
<div class="engine-footer">
    Ditenagai oleh Gemini 3 Flash Cognitive Engine | Integrasi Klinis Tingkat Lanjut via Google Cloud Vertex AI API<br>
    IndoGen-AI Precision System v2.1.0 © 2026
</div>
""", unsafe_allow_html=True)
