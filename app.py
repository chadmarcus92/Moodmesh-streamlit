import streamlit as st
import random
from datetime import datetime, timedelta

# --- CONFIG ---
st.set_page_config(page_title="MoodMesh", page_icon="Sparkles", layout="centered")

# --- GLASS UI STYLES ---
st.markdown("""
<style>
    .glass {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 16px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .streak { font-size: 24px; font-weight: bold; }
    .emoji { font-size: 32px; }
    .title { text-align: center; color: white; font-size: 36px; margin: 20px 0; }
    .bg { background: linear-gradient(135deg, #4A90E2, #50C878); min-height: 100vh; padding: 20px; }
</style>
""", unsafe_allow_html=True)

# --- SIMULATED DATA ---
if 'streak' not in st.session_state:
    st.session_state.streak = 0
    st.session_state.last_scan = None
    st.session_state.moods = []

def scan_mood():
    mood = random.choice(['stress', 'tired', 'calm'])
    bundle = {'stress': 'Rainy Day Joy', 'tired': 'Energy Burst', 'calm': 'Calm Ocean'}[mood]
    st.session_state.moods.insert(0, {
        'mood': mood,
        'bundle': bundle,
        'time': datetime.now().strftime("%I:%M %p")
    })
    # Update streak
    today = datetime.now().date()
    if st.session_state.last_scan != today:
        st.session_state.streak += 1
        st.session_state.last_scan = today
    return mood, bundle

# --- MAIN APP ---
st.markdown('<div class="bg">', unsafe_allow_html=True)
st.markdown('<h1 class="title">MoodMesh</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#eee;">Speak 10s → Get your $19 joy bundle</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("SCAN MY MOOD", type="primary", use_container_width=True):
        mood, bundle = scan_mood()
        st.success(f"Detected: **{mood.upper()}** → {bundle}")

# --- GLASS ROWS ---
st.markdown("### Your MoodMesh")

# Streak
st.markdown(f"""
<div class="glass">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <span>Streak</span>
        <span class="streak">{st.session_state.streak}</span>
        <span class="emoji">{ "Crown" if st.session_state.streak >= 7 else "Gold Medal" if st.session_state.streak >= 3 else "Fire" }</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Free Unlock
if st.session_state.streak >= 7:
    st.markdown(f"""
    <div class="glass" style="background:rgba(80,200,120,0.3); border:2px solid rgba(255,255,255,0.5);">
        <div style="display:flex; align-items:center; gap:12px;">
            <span class="emoji">Party Popper</span>
            <div>
                <div style="font-weight:bold; color:white;">FREE BUNDLE UNLOCKED!</div>
                <div style="font-size:13px; color:#ddd;">Code: MOOD7FREE</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Mood History
for entry in st.session_state.moods[:5]:
    emoji = {'stress': 'Cloud', 'tired': 'Sleeping Face', 'calm': 'Sun'}[entry['mood']]
    st.markdown(f"""
    <div class="glass">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="text-transform:capitalize; color:{'red' if entry['mood']=='stress' else 'orange' if entry['mood']=='tired' else 'lightgreen'}">
                {entry['mood']}
            </span>
            <span class="emoji">{emoji}</span>
            <span style="font-size:12px; color:#ccc;">{entry['time']}</span>
        </div>
        <div style="margin-top:8px; font-size:14px; color:#eee;">→ {entry['bundle']}</div>
    </div>
    """, unsafe_allow_html=True)

# Tip
st.markdown("""
<div class="glass">
    <div style="display:flex; align-items:center; gap:10px;">
        <span style="font-size:20px;">Light Bulb</span>
        <span style="font-size:14px; color:#ddd; font-style:italic;">
            Try saying "I'm unstoppable" for max energy!
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
