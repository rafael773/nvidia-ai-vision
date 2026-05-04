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

# --- CUSTOM CSS PREMIUM ALA GEMINI ADVANCED ---
st.markdown("""
    <style>
    /* Mengubah background utama menjadi gelap elegan */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Mengatur area chat agar pas di tengah */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 6rem;
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

    /* Mempercantik tampilan Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }

    /* Sembunyikan Header dan Footer bawaan Streamlit */
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

# --- BAGIAN SAMPING (SIDEBAR) UNTUK UPLOAD GAMBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #3b82f6;'>📁 Lampiran</h2>", unsafe_allow_html=True)
    st.write("Tambahkan gambar untuk dianalisis oleh AI.")
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.write("---")
        st.image(uploaded_file, caption="Gambar Terpilih", use_container_width=True)
        if st.button("🗑️ Hapus Gambar", use_container_width=True):
            uploaded_file = None
            st.rerun()
            
    st.write("---")
    st.info("💡 Tips Android:\nKlik ikon garis tiga (☰) di pojok kiri atas untuk upload gambar.")

# 4. Header Utama dengan Efek Gradasi
st.markdown('<div class="gradient-text">Jev-AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">The next-gen intelligent AI powered by NVIDIA</div>', unsafe_allow_html=True)

# 5. Menampilkan Riwayat Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Tombol Ketik di Bawah (Chat Input)
if prompt := st.chat_input("Apa yang ingin kamu tanyakan pada Jev-AI?"):
    
    # Simpan chat user ke riwayat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 7. Proses Jawaban AI
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Jev-AI sedang berpikir..."):
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
                                {"type": "text", "text": prompt},
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
                        {"role": "user", "content": prompt}
                    ]

                # Panggil API NVIDIA (Llama 3.2 Vision)
                response = client.chat.completions.create(
                    model="meta/llama-3.2-11b-vision-instruct",
                    messages=messages_to_send,
                    max_tokens=1024,
                    temperature=0.7
                )
                
                full_response = response.choices[0].message.content
                placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = f"Maaf, terjadi kesalahan: {str(e)}"
                placeholder.error(full_response)

    # Simpan jawaban AI ke riwayat
    st.session_state.messages.append({"role": "assistant", "content": full_response})
