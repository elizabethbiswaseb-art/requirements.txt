import io
import google.generativeai as genai
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="Blogger SEO Content Generator", page_icon="📝", layout="wide"
)

st.title("📝 Blogger SEO Content & HTML Generator")
st.caption(
    "আপনার আগের অ্যাপ সম্পূর্ণ নিরাপদ রেখে এটি শুধুমাত্র ব্লগার (Blogger)-এর"
    " জন্য এসইও ফ্রেন্ডলি HTML ফরম্যাট তৈরি করবে।"
)

# Sidebar Configuration
st.sidebar.header("⚙️ কনফিগারেশন")
secret_key = st.secrets.get("GEMINI_API_KEY", "")
api_key = st.sidebar.text_input(
    "Gemini API Key দিন:", value=secret_key, type="password"
)
quality = st.sidebar.slider(
    "WebP কোয়ালিটি (Quality %):", min_value=10, max_value=100, value=80
)


def generate_blogger_html(image_bytes, user_api_key):
  try:
    genai.configure(api_key=user_api_key.strip())
    image_pil = Image.open(io.BytesIO(image_bytes))

    prompt = (
        "Analyze this image and generate an SEO Title, Alt Text, and a detailed"
        " SEO Description in English. Format the output cleanly using HTML tags"
        " like <h2>, <p>, and <strong> so it can be directly pasted into a"
        " Blogger post editor."
    )

    # সঠিক ও সচল মডেল ব্যবহার করা হলো
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([prompt, image_pil])

    if response and response.text:
      return response.text
    else:
      return "Error: Empty response from Gemini API."

  except Exception as e:
    return f"Error: {str(e)}"


# Main Upload Logic
uploaded_file = st.file_uploader(
    "📷 ছবি আপলোড করুন (JPG, PNG, JPEG):", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
  image = Image.open(uploaded_file)

  # Convert to WebP
  buffer = io.BytesIO()
  image.save(buffer, format="WEBP", quality=quality)
  webp_bytes = buffer.getvalue()

  col1, col2 = st.columns(2)
  with col1:
    st.image(image, caption="মূল ছবি", use_container_width=True)

  with col2:
    st.image(webp_bytes, caption="WebP অপ্টিমাইজড ছবি", use_container_width=True)
    st.download_button(
        "📥 অপ্টিমাইজড WebP ডাউনলোড করুন",
        data=webp_bytes,
        file_name="blogger-optimized.webp",
        mime="image/webp",
    )

  st.markdown("---")
  st.subheader("🤖 ব্লগার এসইও কন্টেন্ট ও HTML জেনারেটর")

  if st.button("✨ ব্লগ পোস্টের জন্য HTML কন্টেন্ট তৈরি করুন"):
    if not api_key:
      st.error("দয়া করে সাইডবারে আপনার Gemini API Key বসান!")
    else:
      with st.spinner("ব্লগার উপযোগী এসইও কন্টেন্ট তৈরি হচ্ছে..."):
        result = generate_blogger_html(webp_bytes, api_key)
        if result.startswith("Error"):
          st.error(result)
        else:
          st.session_state["blogger_html"] = result
          st.success("সফলভাবে তৈরি হয়েছে!")

  if "blogger_html" in st.session_state:
    st.subheader("👁️ প্রিভিউ (Preview):")
    st.markdown(st.session_state["blogger_html"], unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📋 ব্লগস্পটে ব্যবহারের জন্য HTML কোড:")
    st.info(
        "নিচের কোডটি কপি করে আপনার Blogger পোস্ট এডিটরের **HTML View**-এ পেস্ট"
        " করলেই ডিজাইন সহ সাজানো পোস্ট পেয়ে যাবেন।"
    )

    st.text_area(
        "HTML Code:", value=st.session_state["blogger_html"], height=200
    )
