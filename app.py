import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io

# Konfigurasi halaman
st.set_page_config(
    page_title="NVIDIA AI Vision", 
    page_icon="🟢", 
    layout="centered"
)

st.markdown("<h1 style='text-align: center;'>🟢 NVIDIA AI Vision</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6b7280;'>Analisis gambar tanpa batas menggunakan NVIDIA API Catalog</p>", unsafe_allow_html=True)
st.write("---")

# Input API Key NVIDIA (Bisa dimasukkan manual oleh pengguna)
nv_api_key = st.text_input("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", type="password", placeholder="nvapi-...")

# Fungsi mengubah gambar ke Base64 agar bisa dibaca NVIDIA
def encode_image_to_base64(image):
    buffered = io.BytesIO()
    # Mengubah format gambar ke JPEG agar ukurannya lebih ringkas
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

if nv_api_key:
    # Inisialisasi Client OpenAI dengan Endpoint NVIDIA
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=nv_api_key
    )

    # Fitur Upload Gambar
    uploaded_file = st.file_uploader("Pilih gambar...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Gambar yang di-upload", use_container_width=True)
        
        user_prompt = st.text_input(
            "Mau tanya apa tentang gambar ini?", 
            placeholder="Contoh: Deskripsikan isi dari gambar ini secara detail."
        )

        if st.button("Tanya AI 🚀", type="primary"):
            if user_prompt:
                with st.spinner("NVIDIA AI sedang menganalisis gambar..."):
                    try:
                        base64_image = encode_image_to_base64(image)

                        # Mengirim permintaan ke Model Llama 3.2 Vision milik NVIDIA
                        response = client.chat.completions.create(
                            model="meta/llama-3.2-11b-vision-instruct",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": user_prompt},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{base64_image}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            max_tokens=1024
                        )
                        
                        # Tampilkan hasil jawaban
                        st.success("Jawaban dari AI NVIDIA:")
                        st.write(response.choices[0].message.content)

                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat memproses gambar: {e}")
            else:
                st.warning("Silakan ketik pertanyaanmu terlebih dahulu!")
else:
    st.info("Masukkan API Key NVIDIA kamu untuk mengaktifkan AI.")