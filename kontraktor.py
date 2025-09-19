import streamlit as st
import openai
from pypdf import PdfReader
import io

# Fungsi untuk mengekstrak teks dari file PDF yang diunggah
def extract_text_from_pdf(pdf_file):
    """
    Membaca file PDF dan mengekstrak teks dari semua halaman.
    """
    try:
        # Membaca file PDF dari bytes
        pdf_reader = PdfReader(io.BytesIO(pdf_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file PDF: {e}")
        return None

# Fungsi untuk mengirim teks ke OpenAI API dan mendapatkan hasil analisis
def analyze_contract_with_openai(api_key, document_text, user_query):
    """
    Mengirimkan teks dokumen dan query ke OpenAI untuk dianalisis.
    """
    if not document_text:
        return "Teks dokumen tidak dapat diekstrak. Tidak ada yang bisa dianalisis."

    try:
        # Mengatur API key untuk library OpenAI
        client = openai.OpenAI(api_key=api_key)
        
        # Membuat prompt yang jelas untuk model AI
        prompt_messages = [
            {
                "role": "system",
                "content": "Anda adalah asisten AI yang ahli dalam menganalisis dokumen hukum dan kontrak. Tugas Anda adalah menjawab pertanyaan pengguna berdasarkan teks dokumen yang diberikan dengan akurat dan ringkas."
            },
            {
                "role": "user",
                "content": f"""
                Berikut adalah teks dari sebuah dokumen kontrak:
                ---
                {document_text}
                ---

                Berdasarkan dokumen di atas, lakukan analisis berikut: "{user_query}"
                ""
            }
        ]

        # Melakukan panggilan ke API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=prompt_messages,
            temperature=0.2,
        )
        return response.choices[0].message.content
    except openai.AuthenticationError:
        st.error("Autentikasi gagal. Pastikan API Key OpenAI Anda benar.")
        return None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat berkomunikasi dengan API OpenAI: {e}")
        return None

# --- Tampilan Utama Aplikasi Streamlit ---

st.set_page_config(page_title="Analisis Kontrak AI", layout="wide")
st.title("📄 Analisis Dokumen Kontrak dengan AI")

# --- Sidebar untuk Input API Key ---
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    openai_api_key = st.text_input(
        "Masukkan OpenAI API Key Anda:",
        type="password",
        help="Dapatkan API key Anda dari [platform.openai.com](https://platform.openai.com/account/api-keys)"
    )
    st.markdown("---")
    st.info("Aplikasi ini menggunakan model GPT-3.5 dari OpenAI untuk menganalisis dokumen Anda.")

# --- Area Utama untuk Unggah File dan Analisis ---
st.header("1. Unggah Dokumen Kontrak Anda")
uploaded_file = st.file_uploader(
    "Pilih file PDF yang ingin dianalisis",
    type="pdf"
)

st.header("2. Ajukan Pertanyaan Analisis")
query = st.text_area(
    "Apa yang ingin Anda ketahui dari dokumen ini?",
    placeholder="Contoh: 'Sebutkan pasal-pasal utama terkait kewajiban para pihak.', 'Ringkas dokumen ini dalam 3 poin utama.', 'Apa saja sanksi yang berlaku jika terjadi pelanggaran?'"
)

# Tombol untuk memulai proses analisis
if st.button("🚀 Mulai Analisis"):
    # Validasi input sebelum memulai
    if not openai_api_key:
        st.error("Harap masukkan OpenAI API Key Anda di sidebar terlebih dahulu.")
    elif not uploaded_file:
        st.error("Harap unggah file PDF kontrak terlebih dahulu.")
    elif not query:
        st.error("Harap masukkan pertanyaan atau instruksi analisis.")
    else:
        with st.spinner("Sedang menganalisis dokumen... Proses ini mungkin memerlukan beberapa saat."):
            # Langkah 1: Ekstrak teks dari PDF
            contract_text = extract_text_from_pdf(uploaded_file)
            
            if contract_text:
                # Langkah 2: Kirim teks ke OpenAI untuk dianalisis
                analysis_result = analyze_contract_with_openai(openai_api_key, contract_text, query)
                
                # Langkah 3: Tampilkan hasil
                if analysis_result:
                    st.header("✅ Hasil Analisis")
                    st.write(analysis_result)
