import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="Image Classifier", page_icon="🔍", layout="centered")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  h1, h2, h3 { font-family: 'Space Mono', monospace; }
  .stApp { background: #0f0f0f; color: #f0f0f0; }
  .result-card {
    background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px;
    padding: 16px 20px; margin: 8px 0; display: flex;
    align-items: center; justify-content: space-between;
  }
  .label { font-size: 1rem; font-weight: 600; color: #f0f0f0; text-transform: capitalize; }
  .score { font-family: 'Space Mono', monospace; font-size: 1rem; color: #00e5a0; }
  .bar-bg { background: #2a2a2a; border-radius: 4px; height: 6px; margin-top: 6px; }
  .bar-fill { background: linear-gradient(90deg, #00e5a0, #00b4d8); border-radius: 4px; height: 6px; }
  .top-badge {
    background: #00e5a0; color: #0f0f0f; font-family: 'Space Mono', monospace;
    font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 20px;
  }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🔍 Image Classifier")
st.markdown("Upload an image — powered by **Hugging Face** · `google/vit-base-patch16-224`")
st.divider()

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    hf_token = st.text_input("Hugging Face API Token", type="password", placeholder="hf_xxxxxxxxxxxxxxxxxxxx")
    model_id = st.selectbox("Model", [
        "google/vit-base-patch16-224",
        "microsoft/resnet-50",
        "google/efficientnet-b7",
        "facebook/convnext-base-224",
    ])
    top_k = st.slider("Top predictions to show", min_value=3, max_value=10, value=5)
    st.markdown("---")
    st.markdown("**How to get a free token:**")
    st.markdown("1. Go to [huggingface.co](https://huggingface.co)")
    st.markdown("2. Sign up / Log in")
    st.markdown("3. Settings → Access Tokens")
    st.markdown("4. Create a **Read** token")

uploaded = st.file_uploader("Drop your image here", type=["jpg", "jpeg", "png", "webp", "bmp"], label_visibility="collapsed")

if uploaded:
    image = Image.open(uploaded)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(image, caption="Your image", use_container_width=True)
    with col2:
        if not hf_token:
            st.warning("⬅️ Enter your Hugging Face API token in the sidebar.")
        else:
            with st.spinner("Classifying..."):
                try:
                    buf = io.BytesIO()
                    image.convert("RGB").save(buf, format="JPEG")
                    img_bytes = buf.getvalue()

                    # Correct URL format from HF docs
                    API_URL = f"https://router.huggingface.co/hf-inference/models/{model_id}/v1/image-classification"
                    headers = {
                        "Authorization": f"Bearer {hf_token}",
                        "Content-Type": "image/jpeg",
                    }

                    response = requests.post(API_URL, headers=headers, data=img_bytes, timeout=30)
                    response.raise_for_status()
                    results = response.json()

                    st.markdown("### Results")
                    for i, item in enumerate(results[:top_k]):
                        label = item["label"].replace("_", " ")
                        pct = round(item["score"] * 100, 1)
                        bar_width = round(item["score"] * 100)
                        badge = '<span class="top-badge">TOP</span>' if i == 0 else ""
                        st.markdown(f"""
                        <div class="result-card">
                          <div style="flex:1">
                            <div style="display:flex;align-items:center;gap:8px">
                              <span class="label">{label}</span>{badge}
                            </div>
                            <div class="bar-bg"><div class="bar-fill" style="width:{bar_width}%"></div></div>
                          </div>
                          <span class="score">{pct}%</span>
                        </div>
                        """, unsafe_allow_html=True)

                except requests.exceptions.HTTPError as e:
                    st.error(f"HTTP Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
else:
    st.info("⬆️ Upload an image above to get started.")