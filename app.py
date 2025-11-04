import streamlit as st
import random
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="MoodMesh", page_icon="Neural", layout="wide", initial_sidebar_state="expanded")

# --- NEURON WEB BACKGROUND (SVG) ---
NEURON_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" style="position:fixed; top:0; left:0; width:100%; height:100%; z-index:-1; opacity:0.25;">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4A90E2" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#50C878" stop-opacity="0.3"/>
    </linearGradient>
  </defs>
  <g fill="none" stroke="url(#grad)" stroke-width="1.2" opacity="0.6">
    <path d="M100,200 Q300,150 500,200 T900,200 Q1100,250 1300,200 T1700,200"/>
    <path d="M200,400 Q400,350 600,400 T1000,400 Q1200,450 1400,400 T1800,400"/>
    <path d="M150,600 Q350,550 550,600 T950,600 Q1150,650 1350,600 T1750,600"/>
    <circle cx="500" cy="200" r="8" fill="#50C878"/>
    <circle cx="900" cy="200" r="8" fill="#4A90E2"/>
    <circle cx="1300" cy="200" r="8" fill="#50C878"/>
    <circle cx="600" cy="400" r="8" fill="#4A90E2"/>
    <circle cx="1000" cy="400" r="8" fill="#50C878"/>
    <circle cx="1400" cy="400" r="8" fill="#4A90E2"/>
    <circle cx="550" cy="600" r="8" fill="#50C878"/>
    <circle cx="950" cy="600" r="8" fill="#4A90E2"/>
    <circle cx="1350" cy="600" r="8" fill="#50C878"/>
  </g>
  <g stroke="#50C878" stroke-width="0.8" opacity="0.3">
    <line x1="500" y1="200" x2="600" y2="400"/>
    <line x1="900" y1="200" x2="1000" y2="400"/>
    <line x1="1300" y1="200" x2="1400" y2="400"/>
    <line x1="600" y1="400" x2="550" y2="600"/>
    <line x1="1000" y1="400" x2="950" y2="600"/>
    <line x1="1400" y1="400" x2="1350" y2="600"/>
  </g>
</svg>
"""
st.markdown(f'<div style="position:fixed; top:0; left:0; width:100%; height:100%; z-index:-1;">{NEURON_SVG}</div>', unsafe_allow_html=True)

# --- GLASS UI CSS ---
st.markdown("""
<style>
    .main { background: #0a0a1a; }
    .glass { background: rgba(255,255,255,0.08); backdrop-filter: blur(14px); border: 1px solid rgba(255,255,255,0.12); 
             border-radius: 20px; padding: 20px; margin: 12px 0; box-shadow: 0 6px 25px rgba(0,0,0,0.25); transition: all 0.3s ease; }
    .glass:hover { transform: translateY(-6px); box-shadow: 0 15px 40px rgba(0,0,0,0.35); }
    .title { text-align: center; color: white; font-size: 52px; font-weight: 900; margin: 30px 0; text-shadow: 0 3px 8px rgba(0,0,0,0.5); }
    .nav { background: rgba(10,10,26,0.95); padding: 14px; border-radius: 18px; backdrop-filter: blur(12px); margin: 10px; }
    .btn-primary { background: linear-gradient(45deg, #50C878, #4A90E2); color: white; font-weight: bold; padding: 18px; border-radius: 50px; text-align: center; font-size: 18px; }
    .emoji { font-size: 38px; }
    .streak { font-size: 36px; font-weight: 900; color: #50C878; }
</style>
""", unsafe_allow_html=True)

# --- STATE ---
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'streak' not in st.session_state: st.session_state.streak = 0
if 'moods' not in st.session_state: st.session_state.moods = []

# --- BUNDLES ---
BUNDLES = {
    'stress': {'name': 'Rainy Day Joy', 'price': 19, 'img': 'https://i.imgur.com/rainy.jpg'},
    'tired': {'name': 'Energy Burst', 'price': 19, 'img': 'https://i.imgur.com/energy.jpg'},
    'calm': {'name': 'Calm Ocean', 'price': 19, 'img': 'https://i.imgur.com/ocean.jpg'}
}

# --- NAVIGATION (FIXED: No `with` + `if`) ---
st.markdown('<div class="nav">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

if col1.button('Home', use_container_width=True):
    st.session_state.page = 'home'
    st.rerun()

if col2.button('Record', use_container_width=True):
    st.session_state.page = 'record'
    st.rerun()

if col3.button('Profile', use_container_width=True):
    st.session_state.page = 'profile'
    st.rerun()

if col4.button('Bundles', use_container_width=True):
    st.session_state.page = 'bundles'
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- PAGES ---
if st.session_state.page == 'home':
    st.markdown('<h1 class="title">MoodMesh</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#ccc; font-size:20px;">Speak 10 seconds → Get your $19 joy bundle</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("SCAN MY MOOD", type="primary", use_container_width=True):
            mood = random.choice(['calm', 'stress', 'tired'])
            st.session_state.moods.append({'mood': mood, 'time': datetime.now().strftime("%I:%M %p")})
            st.session_state.streak += 1
            st.session_state.page = 'bundles'
            st.rerun()

    # Streak Widget
    badge = "Crown" if st.session_state.streak >= 7 else "Gold Medal" if st.session_state.streak >= 3 else "Fire"
    st.markdown(f"""
    <div class="glass">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-size:18px; color:#aaa;">Your Streak</div>
                <div class="streak">{st.session_state.streak}</div>
            </div>
            <div class="emoji">{badge}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == 'record':
    st.markdown('<h1 class="title">Hold & Speak</h1>', unsafe_allow_html=True)
    audio_file = st.file_uploader("Record or upload 10s voice", type=['wav', 'mp3'])
    if audio_file:
        st.audio(audio_file)
        if st.button("Analyze Tone"):
            mood = random.choice(['calm', 'stress', 'tired'])
            st.session_state.moods.append({'mood': mood, 'time': datetime.now().strftime("%I:%M %p")})
            st.session_state.streak += 1
            st.session_state.page = 'bundles'
            st.rerun()

elif st.session_state.page == 'bundles':
    st.markdown('<h1 class="title">Your Joy Bundles</h1>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i, (mood, bundle) in enumerate(BUNDLES.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="glass">
                <img src="{bundle['img']}" style="width:100%; height:140px; object-fit:cover; border-radius:12px;">
                <h4 style="margin:12px 0 4px; color:white;">{bundle['name']}</h4>
                <p style="color:#50C878; font-weight:bold; margin:0;">${bundle['price']}</p>
                <button style="background:#50C878; color:white; border:none; width:100%; padding:10px; margin-top:12px; border-radius:12px; font-weight:bold;">
                    BUY NOW
                </button>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == 'profile':
    st.markdown('<h1 class="title">Your Profile</h1>', unsafe_allow_html=True)
    st.markdown('<div class="glass"><h3>Recent Scans</h3>', unsafe_allow_html=True)
    for entry in st.session_state.moods[-5:]:
        emoji = {'stress': 'Cloud', 'tired': 'Sleeping Face', 'calm': 'Sun'}[entry['mood']]
        st.markdown(f"""
        <div class="glass" style="padding:12px; margin:6px 0;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="text-transform:capitalize; color:{'red' if entry['mood']=='stress' else 'orange' if entry['mood']=='tired' else '#50C878'}">
                    {entry['mood']}
                </div>
                <div class="emoji">{emoji}</div>
                <div style="font-size:13px; color:#aaa;">{entry['time']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.streak >= 7:
        st.balloons()
        st.markdown("""
        <div class="glass" style="background:rgba(80,200,120,0.3); border:2px solid #50C878; text-align:center;">
            <div class="emoji" style="font-size:48px;">Party Popper</div>
            <div style="font-weight:bold; color:white; font-size:18px;">FREE BUNDLE UNLOCKED!</div>
            <div style="font-size:14px; color:#ddd;">Code: MOOD7FREE</div>
        </div>
        """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### Neural")
    st.markdown("**7-day streak = FREE**")
    st.markdown("---")
    st.markdown("**Tip:** Say *'I'm unstoppable'* for max energy!")
