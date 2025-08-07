import streamlit as st
import yt_dlp
import cv2
import os
import pytesseract
from PIL import Image
import tempfile

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

st.set_page_config(page_title="TikTok Text Extractor", layout="centered")
st.title("📹 TikTok Text Extractor")
st.markdown("Cole o link de um vídeo do TikTok e extraia automaticamente o texto visível no vídeo!")

tiktok_url = st.text_input("🔗 Cole o link do TikTok aqui")

if st.button("▶️ Extrair Texto") and tiktok_url:
    with st.spinner("Baixando vídeo..."):
        temp_video_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        ydl_opts = {'format': 'mp4', 'outtmpl': temp_video_path, 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([tiktok_url])
    st.success("✅ Vídeo baixado com sucesso!")

    with st.spinner("🔍 Extraindo texto do vídeo..."):
        cap = cv2.VideoCapture(temp_video_path)
        texto_extraido = set()
        frame_interval = 10  # Mais frequente (~3x mais frames por segundo)
        i = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if i % frame_interval == 0:
                # Converter para escala de cinza
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Aumentar contraste e aplicar binarização
                _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                texto = pytesseract.image_to_string(thresh, lang='por')
                if texto.strip():
                    texto_extraido.add(texto.strip())
            i += 1

        cap.release()
        os.remove(temp_video_path)

    final_texto = "\n\n".join(texto_extraido)
    if final_texto:
        st.subheader("📝 Texto Extraído:")
        st.text_area("Resultado:", value=final_texto, height=300)
        st.download_button("📥 Baixar texto", data=final_texto, file_name="texto_tiktok.txt")
    else:
        st.warning("⚠️ Nenhum texto foi detectado no vídeo.")