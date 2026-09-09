import io
import google.generativeai as genai
from PIL import Image
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

st.set_page_config(
    page_title="Blogger SEO Content Generator", page_icon="📝", layout="wide"
)

st.title("📝 Blogger SEO Content & HTML Generator")
st.caption(
    "আপনার আগের অ্যাপ সম্পূর্ণ নিরাপদ রেখে এটি শুধুমাত্র ব্লগার (Blogger)-এর"
    " জন্য এসইও ফ্রেন্ডলি HTML ফরম্যাট তৈরি করবে।"
)

# --- Blogger API Configuration (Secure via st.secrets) ---
BLOG_ID = st.secrets["BLOG_ID"]
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]

CLIENT_CONFIG = {
    "web": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [REDIRECT_URI]
    }
}
SCOPES = ['https://www.googleapis.com/auth/blogger']

def authenticate_blogger():
    try:
        flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES, redirect_uri=REDIRECT_URI)
        auth_url, _ = flow.authorization_url(prompt='consent')
        st.markdown(f"### [🔐 Click here to authorize with Blogger]({auth_url})")
        
        query_params = st.query_params
        code = query_params.get("code")
        if code:
            flow.fetch_token(code=code)
            credentials = flow.credentials
            st.session_state['blogger_credentials'] = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            st.success("Successfully authenticated with Blogger!")
    except Exception as e:
        st.error(f"Auth Error: {e}")

def publish_post(title, content, is_draft=True):
    if 'blogger_credentials' not in st.session_state:
        st.warning("Please authenticate first using the authorization link above.")
        return
    
    try:
        credentials = Credentials(**st.session_state['blogger_credentials'])
        service = build('blogger', 'v3', credentials=credentials)
        
        body = {
            'title': title,
            'content': content,
            'isDraft': is_draft
        }
        
        posts = service.posts()
        posts.insert(blogId=BLOG_ID, body=body, isDraft=is_draft).execute()
        if is_draft:
            st.success("Post successfully saved as Draft in Blogger!")
        else:
            st.success("Post successfully Published to Blogger!")
    except Exception as e:
        st.error(f"Publishing Error: {e}")

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

    model = genai.GenerativeModel("gemini-3.6-flash")
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
    st.subheader("✍️ Review, Edit & Publish to Blogger")
    st.info("এআই-এর কন্টেন্টে কোনো ভুল থাকলে নিচে ম্যানুয়ালি এডিট করে সরাসরি ব্লগে পাবলিশ বা ড্রাফট করতে পারেন:")

    editable_title = st.text_input("Post Title", value="SEO Optimized Post from Image")
    editable_content = st.text_area("Post HTML Content (Edit if needed)", value=st.session_state["blogger_html"], height=300)

    authenticate_blogger()

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("💾 Save as Draft to Blogger"):
            publish_post(editable_title, editable_content, is_draft=True)

    with col_btn2:
        if st.button("🚀 Publish Now to Blogger"):
            publish_post(editable_title, editable_content, is_draft=False)
