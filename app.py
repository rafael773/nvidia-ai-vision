import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io

# 1. Konfigurasi Halaman (Mobile First)
st.set_page_config(
    page_title="jev-ai", 
    page_icon="✨", 
    layout="centered"
)

# --- CUSTOM CSS AGAR MIRIP GEMINI ---
st.markdown("""
    <style>
    /* Mengatur area chat agar tidak terlalu mepet atas */
    .main .block-container {
        padding-top: 2rem;
        max-width: 800px;
    }
    /* Mengatur gaya balon chat */
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    /* Sembunyikan footer streamlit */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 2. Setup API NVIDIA
NVIDIA_API_KEY = "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"
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

# 3. Inisialisasi Memori Chat (Agar chat tidak hilang saat diketik)
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- BAGIAN SAMPING (SIDEBAR) UNTUK UPLOAD GAMBAR ---
# Di Android, ini akan tersembunyi di balik tombol garis tiga (hamburger)
with st.sidebar:
    st.title("📁 Lampiran")
    uploaded_file = st.file_uploader("Tambah gambar untuk dianalisis:", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Gambar Terpilih", use_container_width=True)
        if st.button("Hapus Gambar"):
            uploaded_file = None
            st.rerun()
    st.write("---")
    st.info("Tips: Di Android, klik ikon ☰ di pojok kiri atas untuk upload gambar.")

# 4. Header Utama
st.markdown("<h2 style='text-align: center;'>✨ Pael AI Assistant</h2>", unsafe_allow_html=True)

# 5. Menampilkan Riwayat Chat ala Gemini
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Tombol Ketik di Bawah (Chat Input)
if prompt := st.chat_input("Tanya Pael AI di sini..."):
    
    # Simpan chat user ke riwayat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 7. Proses Jawaban AI
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Sedang berpikir..."):
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
                        {"role": "system", "content": "Kamu adalah Pael AI, asisten yang cerdas dan ramah. Berikan jawaban yang sangat jelas dan terstruktur dalam Bahasa Indonesia."},
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
