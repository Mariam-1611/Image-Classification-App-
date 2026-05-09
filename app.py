import streamlit as st
import requests
from PIL import Image
import io
import base64

st.set_page_config(page_title="OCR - Text Extractor", page_icon="📄", layout="centered")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  h1, h2, h3 { font-family: 'Space Mono', monospace; }
  .stApp { background: #0d1117; color: #e6edf3; }
  .result-box {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 12px; padding: 20px;
    font-family: 'Space Mono', monospace;
    font-size: 0.9rem; line-height: 1.7;
    color: #e6edf3; white-space: pre-wrap;
    max-height: 400px; overflow-y: auto;
  }
  .stat-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 8px; padding: 12px 16px;
    text-align: center;
  }
  .stat-num { font-family: 'Space Mono', monospace; font-size: 1.5rem; color: #58a6ff; }
  .stat-label { font-size: 0.75rem; color: #8b949e; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📄 OCR Text Extractor")
st.markdown("Upload a scanned document — extract text instantly using **Hugging Face**")
st.divider()

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    hf_token = st.text_input("Hugging Face API Token", type="password", placeholder="hf_xxxxxxxxxxxxxxxxxxxx")
    st.markdown("---")
    st.markdown("**How to get a free token:**")
    st.markdown("1. Go to [huggingface.co](https://huggingface.co)")
    st.markdown("2. Sign up / Log in")
    st.markdown("3. Settings → Access Tokens")
    st.markdown("4. Create a **Read** token")
    st.markdown("---")
    st.markdown("**Supported formats:**")
    st.markdown("JPG, PNG, BMP, TIFF, WEBP")

uploaded = st.file_uploader(
    "Drop your scanned document here",
    type=["jpg", "jpeg", "png", "bmp", "tiff", "webp"],
    label_visibility="collapsed"
)

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Uploaded document", use_container_width=True)
    st.divider()

    if not hf_token:
        st.warning("⬅️ Enter your Hugging Face API token in the sidebar to extract text.")
    else:
        with st.spinner("Extracting text..."):
            try:
                buf = io.BytesIO()
                image.convert("RGB").save(buf, format="JPEG")
                img_bytes = buf.getvalue()

                # Use microsoft/trocr-base-printed — best for scanned docs
                API_URL = "https://router.huggingface.co/hf-inference/models/microsoft/trocr-base-printed"
                headers = {
                    "Authorization": f"Bearer {hf_token}",
                    "Content-Type": "image/jpeg",
                }

                response = requests.post(API_URL, headers=headers, data=img_bytes, timeout=60)
                response.raise_for_status()
                result = response.json()

                # Extract text from response
                if isinstance(result, list) and len(result) > 0:
                    extracted = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    extracted = result.get("generated_text", str(result))
                else:
                    extracted = str(result)

                if extracted:
                    st.markdown("### ✅ Extracted Text")

                    # Stats
                    words = len(extracted.split())
                    chars = len(extracted)
                    lines = len(extracted.splitlines())
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(f'<div class="stat-card"><div class="stat-num">{words}</div><div class="stat-label">Words</div></div>', unsafe_allow_html=True)
                    with c2:
                        st.markdown(f'<div class="stat-card"><div class="stat-num">{chars}</div><div class="stat-label">Characters</div></div>', unsafe_allow_html=True)
                    with c3:
                        st.markdown(f'<div class="stat-card"><div class="stat-num">{lines}</div><div class="stat-label">Lines</div></div>', unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Display text
                    st.markdown(f'<div class="result-box">{extracted}</div>', unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Copy to clipboard button
                    st.code(extracted, language=None)

                    # Download as .txt
                    st.download_button(
                        label="⬇️ Download as .txt",
                        data=extracted,
                        file_name="extracted_text.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )
                else:
                    st.warning("No text could be extracted from this image.")

            except requests.exceptions.HTTPError as e:
                st.error(f"HTTP Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("⬆️ Upload a scanned document above to get started.")