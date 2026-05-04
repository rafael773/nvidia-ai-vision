import streamlit as st
from openai import OpenAI
import base64
import io

# 1. Konfigurasi Halaman (Mobile First & Dark Mode Default)
st.set_page_config(
    page_title="Jev-AI", 
    page_icon="✨", 
    layout="centered"
)

# --- CUSTOM CSS PREMIUM UNTUK FIXED BOTTOM INPUT ALA GEMINI ---
st.markdown("""
    <style>
    /* Mengubah background utama menjadi gelap elegan */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Area chat diberi jarak bawah agar tidak tertutup kotak ketik */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 120px;
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
    
    /* --- MEMBUAT KOTAK INPUT MELAYANG DI BAWAH (FIXED BOTTOM) --- */
    div[data-testid="stForm"] {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 100%;
        max-width: 700px;
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 30px !important;
        padding: 8px 15px !important;
        box-shadow: 0 10px 25px rgb(0 0 0 / 0.5) !important;
        z-index: 9999;
    }

    /* Merapikan posisi kolom di dalam form */
    div[data-testid="stForm"] [data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Hilangkan border bawaan input text */
    div[data-testid="stForm"] input {
        background-color: transparent !important;
        border: none !important;
        color: #f8fafc !important;
        padding: 10px 0px !important;
    }

    /* Hilangkan background tombol kirim agar minimalis */
    div[data-testid="stForm"] button[type="submit"] {
        background-color: transparent !important;
        border: none !important;
        color: #3b82f6 !important;
        font-weight: bold;
        font-size: 16px;
    }
    
    /* Sembunyikan garis dan teks bawaan file uploader */
    div[data-testid="stForm"] .stFileUploader section {
        padding: 0px !important;
        border: none !important;
        background-color: transparent !important;
    }
    div[data-testid="stForm"] .stFileUploader label,
    div[data-testid="stForm"] .stFileUploader small,
    div[data-testid="stForm"] .stFileUploader div[role="status"] {
        display: none !important;
    }
    div[data-testid="stForm"] .stFileUploader div[role="button"] {
        font-size: 24px !important;
        color: #94a3b8 !important;
        background: transparent !important;
        border: none !important;
        padding: 0px !important;
        margin: 0px !important;
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

# 4. Header Utama dengan Efek Gradasi
st.markdown('<div class="gradient-text">Jev-AI Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">The next-gen intelligent AI powered by NVIDIA</div>', unsafe_allow_html=True)

# 5. Menampilkan Riwayat Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- BAGIAN BAWAH ALA GEMINI (MELAYANG DI BAWAH SCREEN) ---

# Form Chat yang selalu menempel di bawah
with st.form("gemini_chat_form", clear_on_submit=True):
    # col1 untuk tombol +, col2 untuk teks ketik, col3 untuk tombol kirim
    c1, c2, c3 = st.columns([1, 8, 1.5])
    
    with c1:
        # Tombol + untuk upload gambar
        uploaded_file = st.file_uploader("➕", type=["jpg", "jpeg", "png"])
        
    with c2:
        user_prompt = st.text_input("", placeholder="Tanya Jev-AI di sini...", label_visibility="collapsed")
        
    with c3:
        submit_button = st.form_submit_button("Kirim")

# Jika ada gambar yang terpilih, tampilkan pratinjau kecil di atas kotak ketik agar user tahu
if uploaded_file:
    st.markdown("""
        <style>
        .preview-box {
            position: fixed;
            bottom: 95px;
            left: 50%;
            transform: translateX(-50%);
            width: 100%;
            max-width: 700px;
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 15px;
            padding: 10px;
            z-index: 9998;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Pratinjau Gambar melayang di atas bar chat
    with st.container():
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        col_img, col_btn = st.columns([2, 8])
        with col_img:
            st.image(uploaded_file, use_container_width=True)
        with col_btn:
            st.markdown("<p style='margin:0; font-size:12px; color:#94a3b8;'>Gambar siap dikirim</p>", unsafe_allow_html=True)
            if st.button("Hapus Gambar"):
                uploaded_file = None
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 6. Proses Jawaban AI saat Tombol Kirim Ditekan
if submit_button and user_prompt:
    
    # Simpan chat user ke riwayat
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # 7. Proses Jawaban AI
    with st.chat_message("assistant"):
        def generate_ai_response():
            try:
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
                            "content": "Kamu adalah Jev-AI, asisten AI yang sangat cerdas, ramah, dan profesional. Berikan jawaban yang sangat jelas, rapi, dan terstruktur dalam Bahasa Indonesia."
                        },
                        {"role": "user", "content": user_prompt}
                    ]

                # Panggil API NVIDIA dengan streaming
                response = client.chat.completions.create(
                    model="meta/llama-3.2-11b-vision-instruct",
                    messages=messages_to_send,
                    max_tokens=1024,
                    temperature=0.7,
                    stream=True
                )
                
                # Mengirim potongan teks satu per satu
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
                        
            except Exception as e:
                yield f"Maaf, terjadi kesalahan: {str(e)}"

        # Jalankan efek ngetik secara real-time
        full_response = st.write_stream(generate_ai_response())

    # Simpan jawaban AI ke riwayat
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # Reset file upload dan segarkan halaman
    uploaded_file = None
    st.rerun()
