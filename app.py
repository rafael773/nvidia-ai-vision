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

# --- CUSTOM CSS PREMIUM & AMAN ---
st.markdown("""
    <style>
    /* Mengubah background utama menjadi gelap elegan */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Mengatur area chat agar pas di tengah */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 750px;
    }

    /* Efek Gradasi Warna untuk Judul Jev-AI */
    .gradient-text {
        font-size: 38px;
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
        font-size: 13px;
        margin-bottom: 25px;
    }

    /* Styling Balon Chat User */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 20px 20px 5px 20px !important;
        padding: 14px !important;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        color: #f1f5f9 !important;
        margin-bottom: 15px !important;
    }

    /* Styling Balon Chat AI Assistant */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: #0f172a !important;
        border: 1px solid #1e3a8a !important;
        border-radius: 20px 20px 20px 5px !important;
        padding: 14px !important;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        color: #f8fafc !important;
        margin-bottom: 15px !important;
    }

    /* Mempercantik tampilan Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }

    /* Sembunyikan footer bawaan Streamlit saja */
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 2. Setup API NVIDIA (API Key sudah terpasang)
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
    
    uploaded_file = st.file_uploader("Pilih gambar...", type=["jpg", "jpeg", "png"], key="sidebar_uploader")
    
    if uploaded_file:
        st.write("---")
        st.image(uploaded_file, caption="Gambar Terpilih", use_container_width=True)
        if st.button("🗑️ Hapus Gambar", use_container_width=True):
            st.session_state["sidebar_uploader"] = None
            st.rerun()

# 4. Header Utama
st.markdown('<div class="gradient-text">Jev-AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">The next-gen intelligent AI powered by NVIDIA</div>', unsafe_allow_html=True)

# Petunjuk penggunaan menu samping di komputer dan HP
st.markdown("""
<div style='text-align: center; margin-top: -15px; margin-bottom: 25px;'>
    <span style='background-color: #1e293b; color: #94a3b8; padding: 5px 12px; border-radius: 12px; font-size: 12px;'>
        ℹ️ Klik tombol menu <b>☰</b> atau panah di pojok kiri atas untuk upload gambar
    </span>
</div>
""", unsafe_allow_html=True)

# 5. Menampilkan Riwayat Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. Kotak Input Bawaan Streamlit (Sangat Stabil)
if prompt := st.chat_input("Tanya Jev-AI di sini..."):
    
    # Simpan chat user ke riwayat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 7. Proses Jawaban AI
    with st.chat_message("assistant"):
        with st.status("🔮 Jev-AI sedang berpikir...", expanded=True) as status:
            def generate_ai_response():
                try:
                    def get_base64(file):
                        return base64.b64encode(file.getvalue()).decode()

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
                        # Mengirimkan riwayat lengkap obrolan agar AI mengingat pembicaraan
                        messages_to_send = [
                            {
                                "role": "system", 
                                "content": "Kamu adalah Jev-AI, asisten AI yang sangat cerdas, ramah, dan profesional. Berikan jawaban yang sangat jelas, rapi, dan terstruktur dalam Bahasa Indonesia."
                            }
                        ] + st.session_state.messages

                    response = client.chat.completions.create(
                        model="meta/llama-3.2-11b-vision-instruct",
                        messages=messages_to_send,
                        max_tokens=2048,
                        temperature=0.7,
                        stream=True
                    )
                    
                    for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            yield chunk.choices[0].delta.content
                            
                except Exception as e:
                    yield f"Maaf, terjadi kesalahan: {str(e)}"

            # Menampilkan hasil ketikan streaming secara real-time
            full_response = st.write_stream(generate_ai_response())
            
            # Ubah status loading jadi selesai
            status.update(label="✨ Jev-AI selesai menjawab!", state="complete", expanded=False)

    # Simpan jawaban AI ke riwayat
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.rerun()
