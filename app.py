import base64
import io
import requests
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="Ultra SEO Image Generator", page_icon="🚀", layout="wide"
)

st.title("🚀 Ultra SEO Image & AI Content Generator")
st.caption(
    "ওয়েব ব্লগিংয়ের জন্য লাইফটাইম ফ্রি WebP ইমেজ কমপ্রেশন এবং SEO কন্টেন্ট জেনারেটর ড্যাশবোর্ড।"
)

# Sidebar Configuration
st.sidebar.header("⚙️ কনফিগারেশন")
secret_key = st.secrets.get("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input(
    "Gemini API Key দিন:", value=secret_key, type="password"
)
quality = st.sidebar.slider(
    "WebP কোয়ালিটি (Quality %):", min_value=10, max_value=100, value=80
)


def generate_seo_content(image_bytes, user_api_key):
  clean_key = user_api_key.strip()
  encoded_image = base64.b64encode(image_bytes).decode("utf-8")

  prompt = (
      "Analyze this image and generate SEO Title, Alt Text, and Description in"
      " Bengali. Format output clearly with headers."
  )

  payload = {
      "contents": [{
          "parts": [
              {"text": prompt},
              {
                  "inline_data": {
                      "mime_type": "image/webp",
                      "data": encoded_image,
                  }
              },
          ]
      }]
  }

  # Passing key via x-goog-api-key header supports both AIzaSy and AQ key formats
  url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
  headers = {
      "Content-Type": "application/json",
      "x-goog-api-key": clean_key,
  }

  response = requests.post(url, headers=headers, json=payload)

  if response.status_code == 200:
    res_data = response.json()
    try:
      return res_data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
      return "AI কন্টেন্ট প্রসেস করতে পারেনি।"
  else:
    return f"Error {response.status_code}: {response.text}"


# Main Upload Logic
uploaded_file = st.file_uploader(
    "📷 আপনার ছবি আপলোড করুন (JPG, PNG, JPEG):", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  image = Image.open(uploaded_file)

  # Convert to WebP
  buffer = io.BytesIO()
  image.save(buffer, format="WEBP", quality=quality)
  webp_bytes = buffer.getvalue()

  orig_size = len(uploaded_file.getvalue()) / 1024
  new_size = len(webp_bytes) / 1024
  savings = ((orig_size - new_size) / orig_size) * 100

  col1, col2 = st.columns(2)
  with col1:
    st.image(image, caption="মূল ছবি", use_container_width=True)
    st.write(f"মূল সাইজ: **{orig_size:.1f} KB**")

  with col2:
    st.image(webp_bytes, caption="WebP ছবি", use_container_width=True)
    st.write(
        f"নতুন সাইজ: **{new_size:.1f} KB** (সাশ্রয়: **{savings:.1f}%**)"
    )
    st.download_button(
        "📥 WebP ছবি ডাউনলোড করুন",
        data=webp_bytes,
        file_name="optimized.webp",
        mime="image/webp",
    )

  st.markdown("---")
  st.subheader("🤖 AI SEO কন্টেন্ট জেনারেটর")

  if st.button("✨ SEO Title, Alt Text ও Description তৈরি করুন"):
    if not api_key:
      st.error("দয়া করে সাইডবারে আপনার API Key বসান!")
    else:
      with st.spinner("AI কন্টেন্ট তৈরি করছে..."):
        result = generate_seo_content(webp_bytes, api_key)
        if result.startswith("Error"):
          st.error(result)
        else:
          st.success("সফলভাবে তৈরি হয়েছে!")
          st.markdown(result)
