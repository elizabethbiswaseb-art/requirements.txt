import io
import google.generativeai as genai
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
  try:
    genai.configure(api_key=user_api_key.strip())
    image_pil = Image.open(io.BytesIO(image_bytes))
    prompt = (
        "Analyze this image and generate SEO Title, Alt Text, and Description in"
        " English. Format output clearly with headers."
    )

    # Active model list
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "gemini-pro-vision",
    ]

    last_exception = None

    # Try list of models automatically
    for model_name in models_to_try:
      try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([prompt, image_pil])
        if response and response.text:
          return response.text
      except Exception as e:
        last_exception = e
        continue

    # Fallback to dynamic model discovery if static names fail
    for m in genai.list_models():
      if "generateContent" in m.supported_generation_methods and (
          "flash" in m.name or "vision" in m.name
      ):
        try:
          model = genai.GenerativeModel(m.name)
          response = model.generate_content([prompt, image_pil])
          if response and response.text:
            return response.text
        except Exception as e:
          last_exception = e
          continue

    return f"Error: {str(last_exception)}"
  except Exception as e:
    return f"Error: {str(e)}"


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
