# moodmesh_streamlit.py
# RUN: streamlit run moodmesh_streamlit.py

import streamlit as st
import openai
import requests
from PIL import Image
from io import BytesIO
import hashlib
import base64

st.set_page_config(page_title="MoodMesh Pro", page_icon="artistic", layout="wide")
st.title("MoodMesh **Pro**")
st.markdown("### *Turn any mood into a living AI mesh gradient palette.*")

# --- API KEY ---
openai.api_key = st.secrets.get("OPENAI_API_KEY") or st.text_input("OpenAI API Key", type="password", key="api_key")
if not openai.api_key:
    st.warning("Enter your OpenAI API key to generate moods.")
    st.stop()

# --- COLOR EXTRACTOR ---
def extract_dominant(image: Image.Image, n: int = 5) -> list:
    img = image.resize((150, 150)).convert("RGB")
    pixels = list(img.getdata())
    color_count = {}
    for r, g, b in pixels:
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        color_count[hex_color] = color_count.get(hex_color, 0) + 1
    return [c for c, _ in sorted(color_count.items(), key=lambda x: x[1], reverse=True)[:n]]

# --- MESH CSS ---
def generate_mesh_css(colors: list) -> str:
    stops = ", ".join([f"{c} {i/(len(colors)-1)*100:.0f}%" for i, c in enumerate(colors)])
    return f"""
    background: 
        radial-gradient(circle at 20% 30%, {colors[0]}, transparent 40%),
        radial-gradient(circle at 80% 70%, {colors[-1]}, transparent 40%),
        linear-gradient(135deg, {stops});
    background-size: 200% 200%;
    animation: flow 12s ease infinite;
    border-radius: 16px;
    """

# --- UI ---
col1, col2 = st.columns([1, 1])
with col1:
    mood = st.text_input("Enter your mood", placeholder="e.g. cyberpunk rain, golden hour", key="mood")
    cols_count = st.slider("Number of colors", 3, 8, 5, key="cols")
with col2:
    generate = st.button("Generate MoodMesh", type="primary", use_container_width=True)

if generate and mood:
    with st.spinner("Creating AI image..."):
        try:
            # GPT Prompt
            prompt_res = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Create a vivid, artistic image prompt for this mood. Max 15 words."},
                    {"role": "user", "content": mood}
                ]
            )
            image_prompt = prompt_res.choices[0].message.content.strip()

            # DALL·E
            img_res = openai.images.generate(model="dall-e-3", prompt=image_prompt, size="1024x1024", n=1)
            image_url = img_res.data[0].url
            image = Image.open(BytesIO(requests.get(image_url).content))

            # Extract + Generate
            colors = extract_dominant(image, cols_count)
            css = generate_mesh_css(colors)
            mood_id = hashlib.md5(mood.encode()).hexdigest()[:8]
            share_url = f"https://moodmesh-pro.streamlit.app/?mood={mood_id}"

            st.session_state.result = {
                "mood": mood,
                "image": image,
                "colors": colors,
                "css": css,
                "id": mood_id,
                "share_url": share_url
            }
            st.balloons()
        except Exception as e:
            st.error(f"Failed: {e}")

# --- DISPLAY ---
if "result" in st.session_state:
    res = st.session_state.result
    st.markdown("---")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.image(res["image"], caption=f"AI Mood: {res['mood']}", use_column_width=True)
    with c2:
        st.markdown("### Live Mesh Gradient")
        st.markdown(f"<div style='height:400px; {res['css']}'></div>", unsafe_allow_html=True)
        st.markdown("<style>@keyframes flow {0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}</style>", unsafe_allow_html=True)

    st.markdown("### Palette")
    cols = st.columns(len(res["colors"]))
    for i, color in enumerate(res["colors"]):
        with cols[i]:
            st.color_picker("", color, disabled=True, label_visibility="collapsed")
            st.code(color)

    st.markdown("### Export")
    e1, e2, e3 = st.columns(3)
    with e1:
        st.download_button("CSS", res["css"], "moodmesh.css", "text/css")
    with e2:
        img_bytes = BytesIO()
        res["image"].save(img_bytes, format="PNG")
        st.download_button("PNG", img_bytes.getvalue(), "mood.png", "image/png")
    with e3:
        st.code(res["share_url"])
        st.link_button("Share", res["share_url"])

    if st.button("New Mood"):
        st.session_state.clear()
        st.rerun()
