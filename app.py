import streamlit as st
import random
from datetime import datetime
import base64  # For bg images

# --- CONFIG ---
st.set_page_config(page_title="MoodMesh", page_icon="🎙️", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #1A1A2E 0%, #4A90E2 50%, #50C878 100%); }
    .glass { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); 
             border-radius: 16px; padding: 16px; margin: 8px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
    .title { text-align: center; color: white; font-size: 48px; font-weight: bold; margin: 20px 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }
    .nav { background: rgba(26,26,46,0.9); padding: 10px; border-radius: 12px; }
    .card { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 12px; margin: 4px; }
    .human-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; object-fit: cover; opacity: 0.3; }
</style>
""", unsafe_allow_html=True)

# --- STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'streak' not in st.session_state: st.session_state.streak = 0
if 'moods' not in st.session_state: st.session_state.moods = []

# --- HUMAN BG IMAGES (AI-Generated Placeholders) ---
def get_human_bg(mood='general'):
    bgs = {
        'general': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD... (base64 of hero-human-bg.jpg)',  # Replace with actual base64
        'calm': 'data:image/jpeg;base64,/9j/... (calm bg)',
        'stress': 'data:image/jpeg;base64,/9j/... (stress bg)',
        'tired': 'data:image/jpeg;base64,/9j/... (tired bg)'
    }
    return bgs.get(mood, bgs['general'])

st.markdown(f'<img class="human-bg" src="{get_human_bg()}" />', unsafe_allow_html=True)

# --- NAVIGATION (Hulu-Style Bottom Bar) ---
st.markdown('<div class="nav">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1: if st.button('🏠 Home'): st.session_state.page = 'home'; st.rerun()
with col2: if st.button('🎙️ Record'): st.session_state.page = 'record'; st.rerun()
with col3: if st.button('📊 Profile'): st.session_state.page = 'profile'; st.rerun()
with col4: if st.button('💳 Bundles'): st.session_state.page = 'bundles'; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- PAGES ---
if st.session_state.page == 'home':
    st.markdown('<h1 class="title">Scan Your Mood. Spark Your Joy.</h1>', unsafe_allow_html=True)
    if st.button("🎤 Start Scan (10s)", type="primary", use_container_width=True, help="Click & speak!"):
        # Sim AI scan
        mood = random.choice(['calm', 'stress', 'tired'])
        st.session_state.moods.append({'mood': mood, 'time': datetime.now().strftime("%H:%M")})
        st.session_state.streak += 1
        st.rerun()
    # Streak Widget
    st.markdown('<div class="glass"><h3>🔥 Your Streak</h3><p style="font-size:24px;">' + str(st.session_state.streak) + ' days</p></div>', unsafe_allow_html=True)

elif st.session_state.page == 'record':
    st.markdown('<h1 class="title">Record Your Voice</h1>', unsafe_allow_html=True)
    audio_file = st.file_uploader("Upload or record audio (10s max)", type=['wav', 'mp3'])
    if audio_file:
        st.audio(audio_file)
        if st.button("Analyze Tone"):
            mood = random.choice(['calm', 'stress', 'tired'])  # Sim AI
            st.success(f"Detected: {mood.upper()}! Redirecting to bundle...")
            st.session_state.page = 'bundles'
            st.rerun()

elif st.session_state.page == 'bundles':
    st.markdown('<h1 class="title">Your Joy Bundles</h1>', unsafe_allow_html=True)
    bundles = [
        {'name': 'Rainy Day Joy', 'price': 19, 'mood': 'stress', 'img': get_human_bg('stress')},
        {'name': 'Energy Burst', 'price': 19, 'mood': 'tired', 'img': get_human_bg('tired')},
        {'name': 'Calm Ocean', 'price': 19, 'mood': 'calm', 'img': get_human_bg('calm')}
    ]
    cols = st.columns(3)
    for i, b in enumerate(bundles):
        with cols[i]:
            st.markdown(f'<div class="glass"><img src="{b["img"]}" style="width:100%; border-radius:8px;"><h4>{b["name"]}</h4><p>${b["price"]}</p><button onclick="location.href=\'https://buy.stripe.com/test\'">Buy</button></div>', unsafe_allow_html=True)

elif st.session_state.page == 'profile':
    st.markdown('<h1 class="title">Your Profile</h1>', unsafe_allow_html=True)
    st.markdown('<div class="glass"><h3>Journal</h3>', unsafe_allow_html=True)
    for mood in st.session_state.moods[-5:]:
        st.markdown(f'<div class="card"><p>{mood["mood"].upper()} at {mood["time"]}</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.streak >= 7:
        st.balloons()  # Fun confetti!

# --- SIDEBAR (Hulu-Style Menu) ---
with st.sidebar:
    st.image(get_human_bg('general'), use_column_width=True)
    st.info("7-day streak = FREE bundle!")

st.markdown('<script>window.onload = function() { document.querySelectorAll(".glass").forEach(el => el.style.transition = "all 0.3s ease"); }</script>', unsafe_allow_html=True)
