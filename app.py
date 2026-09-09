import io
import os
import PIL.Image
import google.generativeai as genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Ultra SEO Image Converter & Content AI",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 Ultra SEO Image & AI Content Generator")
st.caption(
    "ওয়েব ব্লগিংয়ের জন্য লাইফটাইম ফ্রি WebP ইমেজ কমপ্রেশন এবং SEO কন্টেন্ট জেনারেটর ড্যাশবোর্ড।"
)

# Sidebar Settings
st.sidebar.header("⚙️ কনফিগারেশন")
api_key = st.sidebar.text_input(
    "Gemini API Key দিন:",
    type="password",
    value=os.environ.get("GEMINI_API_KEY", ""),
    help="Google AI Studio থেকে প্রাপ্ত ফ্রি API Key-টি এখানে দিন।",
)

quality = st.sidebar.slider(
    "WebP কোয়ালিটি (Quality %):", min_value=50, max_value=100, value=80
)

# File Upload
uploaded_file = st.file_uploader(
    "📸 আপনার ছবি আপলোড করুন (JPG, PNG, JPEG):", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    col1, col2 = st.columns(2)

    original_bytes = uploaded_file.getvalue()
    original_size_kb = len(original_bytes) / 1024

    image = PIL.Image.open(io.BytesIO(original_bytes))
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    output_buffer = io.BytesIO()
    image.save(output_buffer, format="WEBP", quality=quality)
    webp_bytes = output_buffer.getvalue()
    webp_size_kb = len(webp_bytes) / 1024
    savings = ((original_size_kb - webp_size_kb) / original_size_kb) * 100

    with col1:
        st.subheader("🖼️ মূল ছবি (Original)")
        st.image(image, use_container_width=True)
        st.metric("ফাইল সাইজ", f"{original_size_kb:.1f} KB")

    with col2:
        st.subheader("⚡ অপটিমাইজড WebP")
        st.image(
            output_buffer.getvalue(),
            caption=f"WebP Quality {quality}%",
            use_container_width=True,
        )
        st.metric(
            "নতুন সাইজ",
            f"{webp_size_kb:.1f} KB",
            delta=f"-{savings:.1f}% সাশ্রয়",
            delta_color="normal",
        )

        webp_filename = os.path.splitext(uploaded_file.name)[0] + ".webp"
        st.download_button(
            label="📥 WebP ছবি ডাউনলোড করুন",
            data=webp_bytes,
            file_name=webp_filename,
            mime="image/webp",
            use_container_width=True,
        )

    st.divider()

    st.subheader("🤖 AI SEO কন্টেন্ট জেনারেটর")

    if not api_key:
        st.warning("⚠️ কন্টেন্ট জেনারেট করতে বামপাশের সাইডবারে Gemini API Key দিন।")
    else:
        if st.button(
            "✨ SEO Title, Alt Text ও Description তৈরি করুন",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner("AI ছবি বিশ্লেষণ করছে..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")

                    prompt = """
                    Analyze this graphic design/image and provide:
                    1. Image Title (SEO optimized, max 8-10 words)
                    2. Alt Text (SEO Friendly description for HTML alt tag)
                    3. Description (Detailed engaging blog description in English, around 100-150 words)

                    Output format strictly as:
                    TITLE: [Title]
                    ALT: [Alt Text]
                    DESCRIPTION: [Description]
                    """

                    response = model.generate_content([prompt, image])
                    res_text = response.text

                    title_val, alt_val, desc_val = "", "", ""
                    for line in res_text.split("\n"):
                        if line.startswith("TITLE:"):
                            title_val = line.replace("TITLE:", "").strip()
                        elif line.startswith("ALT:"):
                            alt_val = line.replace("ALT:", "").strip()
                        elif line.startswith("DESCRIPTION:"):
                            desc_val = line.replace("DESCRIPTION:", "").strip()

                    if not title_val:
                        desc_val = res_text

                    st.success("✅ SEO কন্টেন্ট সফলভাবে জেনারেট হয়েছে!")

                    st.text_input("📌 Image Title:", value=title_val)
                    st.text_input("🏷️ Alt Text (SEO Friendly):", value=alt_val)
                    st.text_area("📝 Blog Description:", value=desc_val, height=150)

                except Exception as e:
                    st.error(f"❌ এরর এসেছে: {e}")
