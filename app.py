import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io

# 1. Konfigurasi Halaman (Mobile First & Dark Mode Default)
st.set_page_config(
    page_title="Jev-AI", 
    page_icon="✨", 
    layout="centered"
)

# --- CUSTOM CSS PREMIUM & ADVANCED ALA GEMINI ADVANCED ---
st.markdown("""
    <style>
    /* Mengubah background utama menjadi gelap elegan */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Mengatur area chat agar pas di tengah dan tidak terlalu mepet bawah */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 7rem;
        max-width: 750px;
    }

    /* Efek Gradasi Warna untuk Judul Jev-AI */
    .gradient-text {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
    }

    .sub-text {
        color: #94a3b8;
        text-align: center;
        font-size: 14px;
        margin-bottom: 30px;
    }

    /* Styling Balon Chat User */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 20px 20px 5px 20px !important;
        padding: 14px !important;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        color: #f1f5f9 !important;
    }

    /* Styling Balon Chat AI Assistant */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #0f172a !important;
        border: 1px solid #1e3a8a !important;
        border-radius: 20px 20px 20px 5px !important;
        padding: 14px !important;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        color: #f8fafc !important;
    }
    
    /* --- STYLING KHUSUS UNTUK TOMBOL GAMBAR DI BAWAH --- */
    
    /* Membuat kotak container untuk input bagian bawah */
    [data-testid="stForm"] {
        background-color: #111827;
        border: 1px solid #334155;
        border-radius: 30px;
        padding: 5px 20px;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }
    
    /* Sembunyikan garis bawaan input text */
    [data-testid="stForm"] .stTextInput input {
        border: none !important;
        background-color: transparent !important;
        color: #f8fafc !important;
        padding-left: 0px !important;
    }
    
    /* Ubah tampilan tombol upload gambar jadi ikon kecil */
    [data-testid="stForm"] .stFileUploader section {
        padding: 0px !important;
        border: none !important;
        background-color: transparent !important;
    }
    
    /* Sembunyikan teks-teks bawaan upload file */
    [data-testid="stForm"] .stFileUploader label,
    [data-testid="stForm"] .stFileUploader small,
    [data-testid="stForm"] .stFileUploader .st-emotion-cache-up8up8 {
        display: none !important;
    }
    
    /* Mengatur jarak ikon kamera agar pas di samping */
    [data-testid="stForm"] .stFileUploader div[role="button"] {
        font-size: 20px;
        color: #94a3b8;
        padding: 5px 10px;
        background-color: transparent;
        border: none;
        cursor: pointer;
    }

    /* Sembunyikan Sidebar, Header, Footer */
    [data-testid="stSidebar"] {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 2. Setup API NVIDIA
NVIDIA_API_KEY = "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"
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

# 3. Inisialisasi Memori Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Header Utama dengan Efek Gradasi
st.markdown('<div class="gradient-text">Jev-AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">The next-gen intelligent AI powered by NVIDIA</div>', unsafe_allow_html=True)

# 5. Menampilkan Riwayat Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- BAGIAN BAWAH ALA GEMINI (GAMBAR DISAMPING TEKS) ---

# Buat form agar tombol upload dan teks bisa sejajar dalam satu baris
with st.form("gemini_form", clear_on_submit=True):
    col1, col2 = st.columns([1, 10])
    
    with col1:
        # Upload gambar dalam bentuk ikon (CSS yang ngatur)
        uploaded_file = st.file_uploader("📷", type=["jpg", "jpeg", "png"])
        
    with col2:
        # Kotak input teks
        user_prompt = st.text_input("", placeholder="Tanya Jev-AI di sini...", key="user_input")
        
    # Tombol submit tersembunyi (bisa juga tekan enter)
    submit_button = st.form_submit_button("Kirim", use_container_width=False)

# Cek apakah ada gambar yang sedang dipilih, tampilkan di atas kotak ketik
if uploaded_file:
    st.write("---")
    col1, col2 = st.columns([2, 10])
    with col1:
        st.image(uploaded_file, caption="Gambar Terpilih", use_container_width=True)
    with col2:
        if st.button("🗑️ Hapus Gambar"):
            uploaded_file = None
            st.rerun()

# 6. Proses Jawaban AI saat Submit
if submit_button and user_prompt:
    
    # Simpan chat user ke riwayat
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 7. Proses Jawaban AI
    with st.chat_message("assistant"):
        # Kita gunakan generator untuk efek streaming
        def generate_ai_response():
            try:
                # Fungsi Base64 untuk Gambar
                def get_base64(file):
                    return base64.b64encode(file.getvalue()).decode()

                # Cek apakah ada gambar yang diupload
                if uploaded_file:
                    img_base64 = get_base64(uploaded_file)
                    messages_to_send = [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                            ]
                        }
                    ]
                else:
                    messages_to_send = [
                        {
                            "role": "system", 
                            "content": "Kamu adalah Jev-AI, asisten AI yang sangat cerdas, ramah, dan profesional. Berikan penjelasan yang sangat jelas, rapi, dan terstruktur dalam Bahasa Indonesia."
                        },
                        {"role": "user", "content": user_prompt}
                    ]

                # Panggil API NVIDIA (Llama 3.2 Vision) dengan streaming
                response = client.chat.completions.create(
                    model="meta/llama-3.2-11b-vision-instruct",
                    messages=messages_to_send,
                    max_tokens=1024,
                    temperature=0.7,
                    stream=True  # Mengaktifkan streaming teks
                )
                
                # Mengirim potongan teks satu per satu
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
                        
            except Exception as e:
                yield f"Maaf, terjadi kesalahan: {str(e)}"

        # Jalankan efek ngetik secara real-time di layar
        full_response = st.write_stream(generate_ai_response())

    # Simpan jawaban AI ke riwayat setelah selesai mengetik
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Hapus file upload setelah selesai proses agar tidak dobel
    uploaded_file = None
    st.rerun()
