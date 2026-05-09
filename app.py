import streamlit as st
from PIL import Image
import pytesseract
import io

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
    border-radius: 8px; padding: 12px 16px; text-align: center;
  }
  .stat-num { font-family: 'Space Mono', monospace; font-size: 1.5rem; color: #58a6ff; }
  .stat-label { font-size: 0.75rem; color: #8b949e; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 📄 OCR Text Extractor")
st.markdown("Upload a scanned document — extract text instantly, **no API needed**")
st.divider()

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    lang = st.selectbox("Language", ["eng", "ara", "fra", "deu", "spa"], 
                        format_func=lambda x: {"eng": "English", "ara": "Arabic", 
                                               "fra": "French", "deu": "German", 
                                               "spa": "Spanish"}[x])
    st.markdown("---")
    st.markdown("**Supported formats:**")
    st.markdown("JPG, PNG, BMP, TIFF, WEBP")
    st.markdown("---")
    st.markdown("**Tips for best results:**")
    st.markdown("- Use clear, high-resolution images")
    st.markdown("- Make sure text is horizontal")
    st.markdown("- Avoid blurry or skewed scans")

uploaded = st.file_uploader(
    "Drop your scanned document here",
    type=["jpg", "jpeg", "png", "bmp", "tiff", "webp"],
    label_visibility="collapsed"
)

if uploaded:
    image = Image.open(uploaded)
    st.image(image, caption="Uploaded document", use_container_width=True)
    st.divider()

    with st.spinner("Extracting text..."):
        try:
            # Run Tesseract OCR
            extracted = pytesseract.image_to_string(image, lang=lang)

            if extracted.strip():
                st.markdown("### ✅ Extracted Text")

                # Stats
                words = len(extracted.split())
                chars = len(extracted.strip())
                lines = len([l for l in extracted.splitlines() if l.strip()])

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f'<div class="stat-card"><div class="stat-num">{words}</div><div class="stat-label">Words</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="stat-card"><div class="stat-num">{chars}</div><div class="stat-label">Characters</div></div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="stat-card"><div class="stat-num">{lines}</div><div class="stat-label">Lines</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Display + copy
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
                st.warning("No text found. Try a clearer image or change the language in the sidebar.")

        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.info("⬆️ Upload a scanned document above to get started.")