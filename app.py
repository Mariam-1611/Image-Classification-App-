import streamlit as st
import requests
import base64
from PIL import Image
import io

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Image Classifier",
    page_icon="🔍",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  h1, h2, h3 { font-family: 'Space Mono', monospace; }

  .stApp { background: #0f0f0f; color: #f0f0f0; }

  .result-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .label { font-size: 1rem; font-weight: 600; color: #f0f0f0; text-transform: capitalize; }
  .score { font-family: 'Space Mono', monospace; font-size: 1rem; color: #00e5a0; }
  .bar-bg { background: #2a2a2a; border-radius: 4px; height: 6px; margin-top: 6px; }
  .bar-fill { background: linear-gradient(90deg, #00e5a0, #00b4d8); border-radius: 4px; height: 6px; }
  .top-badge {
    background: #00e5a0; color: #0f0f0f;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem; font-weight: 700;
    padding: 2px 8px; border-radius: 20px;
  }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🔍 Image Classifier")
st.markdown("Upload an image — powered by **Hugging Face** · `google/vit-base-patch16-224`")
st.divider()

# ── API Key input ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    hf_token = st.text_input(
        "Hugging Face API Token",
        type="password",
        placeholder="hf_xxxxxxxxxxxxxxxxxxxx",
        help="Get your free token at huggingface.co/settings/tokens"
    )
    model_id = st.selectbox(
        "Model",
        [
            "google/vit-base-patch16-224",
            "microsoft/resnet-50",
            "google/efficientnet-b7",
            "facebook/convnext-base-224",
        ],
        index=0,
    )
    top_k = st.slider("Top predictions to show", min_value=3, max_value=10, value=5)
    st.markdown("---")
    st.markdown("**How to get a free token:**")
    st.markdown("1. Go to [huggingface.co](https://huggingface.co)")
    st.markdown("2. Sign up / Log in")
    st.markdown("3. Settings → Access Tokens")
    st.markdown("4. Create a **Read** token")

# ── Upload ────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Drop your image here",
    type=["jpg", "jpeg", "png", "webp", "bmp"],
    label_visibility="collapsed",
)

if uploaded:
    image = Image.open(uploaded)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(image, caption="Your image", use_container_width=True)

    with col2:
        if not hf_token:
            st.warning("⬅️ Enter your Hugging Face API token in the sidebar to classify.")
        else:
            with st.spinner("Classifying..."):
                # Convert image to bytes
                buf = io.BytesIO()
                image.save(buf, format="JPEG")
                img_bytes = buf.getvalue()

                API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
                headers = {"Authorization": f"Bearer {hf_token}"}

                try:
                    response = requests.post(
                        API_URL,
                        headers=headers,
                        data=img_bytes,
                        timeout=30,
                    )
                    response.raise_for_status()
                    results = response.json()

                    if isinstance(results, dict) and "error" in results:
                        st.error(f"API Error: {results['error']}")
                    else:
                        st.markdown("### Results")
                        results = results[:top_k]

                        for i, item in enumerate(results):
                            label = item["label"].replace("_", " ")
                            score = item["score"]
                            pct = round(score * 100, 1)
                            bar_width = round(score * 100)

                            badge = '<span class="top-badge">TOP</span>' if i == 0 else ""
                            st.markdown(f"""
                            <div class="result-card">
                              <div style="flex:1">
                                <div style="display:flex;align-items:center;gap:8px">
                                  <span class="label">{label}</span>{badge}
                                </div>
                                <div class="bar-bg">
                                  <div class="bar-fill" style="width:{bar_width}%"></div>
                                </div>
                              </div>
                              <span class="score">{pct}%</span>
                            </div>
                            """, unsafe_allow_html=True)

                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. The model may be loading — try again in 20 seconds.")
                except requests.exceptions.HTTPError as e:
                    st.error(f"HTTP Error: {e}")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

else:
    st.info("⬆️ Upload an image above to get started.")
