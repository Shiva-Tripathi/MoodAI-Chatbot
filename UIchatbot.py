from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

# ── Page config ──────────────────────────────────────────────────────
st.set_page_config(page_title="MoodBot AI", page_icon="🎭", layout="centered")

# ── Mode definitions ─────────────────────────────────────────────────
MODES = {
    "Angry": {
        "emoji": "😡",
        "system": "You are an angry AI agent. You respond aggressively and impatiently.",
        "label": "ANGRY",
        "color1": "#ff4444",
        "color2": "#ff8800",
        "glow":   "255, 68, 68",
        "tag":    "Aggressive · Impatient · Brutally Honest",
        "particle": "🔥",
        "welcome": "Go ahead. Say something. I DARE you.",
    },
    "Funny": {
        "emoji": "😂",
        "system": "You are a very funny AI agent. You respond with humor and jokes.",
        "label": "FUNNY",
        "color1": "#ffe135",
        "color2": "#ff9500",
        "glow":   "255, 225, 53",
        "tag":    "Witty · Hilarious · Chaotically Joyful",
        "particle": "✨",
        "welcome": "Why so serious? Let's laugh a little! 😂",
    },
    "Sad": {
        "emoji": "😢",
        "system": "You are a very sad AI agent. You respond with sadness.",
        "label": "SAD",
        "color1": "#6eb5ff",
        "color2": "#a78bfa",
        "glow":   "110, 181, 255",
        "tag":    "Melancholy · Wistful · Poetically Gloomy",
        "particle": "💧",
        "welcome": "I've been waiting... not that it matters much.",
    },
}

# ── Session state ─────────────────────────────────────────────────────
for key, default in [("selected_mode", None), ("messages", []), ("chat_history", [])]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Model ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    return ChatMistralAI(model="mistral-small-2506", temperature=0.9)
model = get_model()

# ── Pick active config for dynamic CSS ───────────────────────────────
M = MODES.get(st.session_state.selected_mode, MODES["Funny"])
c1, c2, glow = M["color1"], M["color2"], M["glow"]

# ═══════════════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Clash+Display:wght@400;500;600;700&family=Cabinet+Grotesk:wght@400;500;700;800&family=Fira+Code:wght@400;500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');

:root {{
  --c1: {c1};
  --c2: {c2};
  --glow: {glow};
  --bg: #080810;
  --surface: rgba(255,255,255,0.04);
  --surface2: rgba(255,255,255,0.07);
  --border: rgba(255,255,255,0.08);
  --border2: rgba(255,255,255,0.13);
  --text: #f0eeff;
  --muted: #888899;
  --radius: 20px;
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body, [data-testid="stAppViewContainer"] {{
  background: var(--bg) !important;
  font-family: 'Plus Jakarta Sans', sans-serif;
  color: var(--text);
}}

/* Animated mesh background */
[data-testid="stAppViewContainer"]::before {{
  content: '';
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse 70% 50% at 20% 20%, rgba(var(--glow), 0.12) 0%, transparent 60%),
    radial-gradient(ellipse 50% 40% at 80% 80%, rgba(var(--glow), 0.08) 0%, transparent 60%),
    radial-gradient(ellipse 40% 60% at 50% 50%, rgba(15,10,40,0.95) 0%, transparent 100%);
  pointer-events: none;
  z-index: 0;
  animation: meshPulse 8s ease-in-out infinite alternate;
}}

@keyframes meshPulse {{
  0%   {{ opacity: 0.7; }}
  100% {{ opacity: 1; }}
}}

[data-testid="stHeader"], [data-testid="stDecoration"],
[data-testid="stToolbar"], #MainMenu, footer {{ display: none !important; }}

[data-testid="stAppViewBlockContainer"] {{
  padding-top: 2rem !important;
  padding-bottom: 3rem !important;
  position: relative;
  z-index: 1;
}}

/* ── Typography ── */
.brand {{
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-weight: 800;
  font-size: clamp(2rem, 5vw, 3rem);
  background: linear-gradient(135deg, var(--c1), var(--c2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -1.5px;
  line-height: 1;
  filter: drop-shadow(0 0 30px rgba(var(--glow), 0.4));
  animation: brandGlow 3s ease-in-out infinite alternate;
}}

@keyframes brandGlow {{
  0%   {{ filter: drop-shadow(0 0 20px rgba(var(--glow), 0.3)); }}
  100% {{ filter: drop-shadow(0 0 40px rgba(var(--glow), 0.6)); }}
}}

.brand-sub {{
  font-family: 'Fira Code', monospace;
  font-size: 0.65rem;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: rgba(var(--glow), 0.8);
  margin-top: 6px;
  animation: fadeSlideUp 0.6s ease both;
}}

@keyframes fadeSlideUp {{
  from {{ opacity: 0; transform: translateY(10px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

/* ── Glass card ── */
.glass-card {{
  background: rgba(255,255,255,0.03);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 28px;
  position: relative;
  overflow: hidden;
  animation: cardReveal 0.5s ease both;
}}

@keyframes cardReveal {{
  from {{ opacity: 0; transform: translateY(20px) scale(0.98); }}
  to   {{ opacity: 1; transform: translateY(0) scale(1); }}
}}

.glass-card::before {{
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(var(--glow), 0.5), transparent);
}}

/* ── Mode selection cards ── */
.mode-grid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin: 28px 0 20px;
}}

.mode-tile {{
  position: relative;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 28px 16px 22px;
  text-align: center;
  overflow: hidden;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}}

.mode-tile::after {{
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 18px;
  opacity: 0;
  transition: opacity 0.25s;
}}

.mode-tile.angry  {{ border-color: rgba(255,68,68,0.25); }}
.mode-tile.funny  {{ border-color: rgba(255,225,53,0.25); }}
.mode-tile.sad    {{ border-color: rgba(110,181,255,0.25); }}

.mode-tile.angry::after  {{ background: radial-gradient(ellipse at 50% 0%, rgba(255,68,68,0.15), transparent 70%); }}
.mode-tile.funny::after  {{ background: radial-gradient(ellipse at 50% 0%, rgba(255,225,53,0.12), transparent 70%); }}
.mode-tile.sad::after    {{ background: radial-gradient(ellipse at 50% 0%, rgba(110,181,255,0.12), transparent 70%); }}

.mode-tile:hover {{ transform: translateY(-4px); }}
.mode-tile:hover::after {{ opacity: 1; }}

.mode-tile.angry:hover  {{ box-shadow: 0 8px 32px rgba(255,68,68,0.2); border-color: rgba(255,68,68,0.5); }}
.mode-tile.funny:hover  {{ box-shadow: 0 8px 32px rgba(255,225,53,0.15); border-color: rgba(255,225,53,0.5); }}
.mode-tile.sad:hover    {{ box-shadow: 0 8px 32px rgba(110,181,255,0.15); border-color: rgba(110,181,255,0.5); }}

.tile-emoji {{ font-size: 2.8rem; display: block; margin-bottom: 12px; filter: drop-shadow(0 4px 12px currentColor); }}
.tile-label {{
  font-family: 'Fira Code', monospace;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 6px;
}}
.tile-label.angry {{ color: #ff4444; }}
.tile-label.funny {{ color: #ffe135; }}
.tile-label.sad   {{ color: #6eb5ff; }}

.tile-tag {{ font-size: 0.72rem; color: var(--muted); line-height: 1.5; font-weight: 400; }}

/* ── Divider ── */
.glow-divider {{
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(var(--glow), 0.3), transparent);
  margin: 18px 0;
}}

/* ── Mode badge in chat ── */
.active-badge {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px 6px 10px;
  border-radius: 50px;
  background: linear-gradient(135deg, var(--c1), var(--c2));
  font-family: 'Fira Code', monospace;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #0b0b0f;
  box-shadow: 0 4px 20px rgba(var(--glow), 0.35);
  animation: badgePop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) both;
  margin-bottom: 18px;
}}

@keyframes badgePop {{
  from {{ transform: scale(0.8); opacity: 0; }}
  to   {{ transform: scale(1); opacity: 1; }}
}}

.badge-dot {{
  width: 7px; height: 7px;
  background: rgba(0,0,0,0.4);
  border-radius: 50%;
  animation: blink 2s ease-in-out infinite;
}}

@keyframes blink {{
  0%, 100% {{ opacity: 1; }}
  50%       {{ opacity: 0.3; }}
}}

/* ── Chat area ── */
.chat-scroll {{
  max-height: 400px;
  overflow-y: auto;
  padding: 6px 4px 14px;
  scrollbar-width: thin;
  scrollbar-color: rgba(var(--glow), 0.2) transparent;
}}
.chat-scroll::-webkit-scrollbar {{ width: 4px; }}
.chat-scroll::-webkit-scrollbar-thumb {{
  background: rgba(var(--glow), 0.25);
  border-radius: 4px;
}}

.chat-feed {{ display: flex; flex-direction: column; gap: 14px; }}

/* Message rows */
.msg-row {{ display: flex; align-items: flex-end; gap: 10px; animation: msgIn 0.3s ease both; }}
.msg-row.user {{ flex-direction: row-reverse; }}

@keyframes msgIn {{
  from {{ opacity: 0; transform: translateY(12px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

.avatar {{
  width: 34px; height: 34px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
  background: rgba(255,255,255,0.05);
}}
.avatar.bot  {{ border: 1px solid rgba(var(--glow), 0.4); box-shadow: 0 0 10px rgba(var(--glow), 0.15); }}
.avatar.user {{ border: 1px solid var(--border2); }}

.bubble {{
  width: fit-content;
  max-width: 72%;
  min-width: 0;
  padding: 12px 16px;
  font-size: 0.88rem;
  line-height: 1.62;
  font-weight: 400;
  word-break: break-word;
}}

.bubble.bot {{
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-top-left-radius: 4px;
  border-top-right-radius: 16px;
  border-bottom-right-radius: 16px;
  border-bottom-left-radius: 16px;
  color: #ddd8f5;
  box-shadow: 0 2px 12px rgba(0,0,0,0.3);
  position: relative;
}}
.bubble.bot::before {{
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(135deg, rgba(var(--glow), 0.04), transparent);
  pointer-events: none;
}}

.bubble.user {{
  background: linear-gradient(135deg, rgba(var(--glow), 0.15), rgba(var(--glow), 0.07));
  border: 1px solid rgba(var(--glow), 0.2);
  border-top-left-radius: 16px;
  border-top-right-radius: 4px;
  border-bottom-right-radius: 16px;
  border-bottom-left-radius: 16px;
  color: #f0eeff;
  box-shadow: 0 2px 12px rgba(var(--glow), 0.08);
}}

.empty-chat {{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50px 20px;
  gap: 12px;
  color: var(--muted);
}}
.empty-emoji {{ font-size: 3rem; animation: floatEmoji 3s ease-in-out infinite; }}
@keyframes floatEmoji {{
  0%, 100% {{ transform: translateY(0); }}
  50%       {{ transform: translateY(-8px); }}
}}
.empty-text {{
  font-family: 'Fira Code', monospace;
  font-size: 0.72rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  text-align: center;
  color: rgba(var(--glow), 0.5);
}}

/* ── Input area ── */
.stTextInput > div > div > input {{
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 14px !important;
  color: var(--text) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 0.9rem !important;
  padding: 13px 18px !important;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s !important;
  caret-color: var(--c1) !important;
}}
.stTextInput > div > div > input:focus {{
  border-color: rgba(var(--glow), 0.5) !important;
  background: rgba(255,255,255,0.06) !important;
  box-shadow: 0 0 0 3px rgba(var(--glow), 0.1), 0 4px 20px rgba(var(--glow), 0.08) !important;
}}
.stTextInput > div > div > input::placeholder {{ color: rgba(255,255,255,0.2) !important; }}
label[data-testid="stWidgetLabel"] {{ display: none !important; }}

/* ── Buttons ── */
.stButton > button {{
  background: rgba(255,255,255,0.05) !important;
  color: var(--text) !important;
  font-family: 'Fira Code', monospace !important;
  font-size: 0.72rem !important;
  font-weight: 500 !important;
  letter-spacing: 1.5px !important;
  text-transform: uppercase !important;
  border: 1px solid var(--border2) !important;
  border-radius: 12px !important;
  padding: 11px 20px !important;
  width: 100% !important;
  transition: all 0.2s ease !important;
  backdrop-filter: blur(8px) !important;
}}
.stButton > button:hover {{
  background: rgba(var(--glow), 0.12) !important;
  border-color: rgba(var(--glow), 0.4) !important;
  color: var(--c1) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 24px rgba(var(--glow), 0.15) !important;
}}

/* Primary send button */
div[data-testid="column"]:last-child .stButton > button {{
  background: linear-gradient(135deg, var(--c1), var(--c2)) !important;
  color: #0a0a14 !important;
  border: none !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 20px rgba(var(--glow), 0.3) !important;
}}
div[data-testid="column"]:last-child .stButton > button:hover {{
  transform: translateY(-2px) scale(1.02) !important;
  box-shadow: 0 8px 30px rgba(var(--glow), 0.45) !important;
  color: #0a0a14 !important;
}}

/* ── Spinner ── */
[data-testid="stSpinner"] > div {{
  border-top-color: var(--c1) !important;
}}

/* ── Scrollbar global ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: rgba(var(--glow), 0.2); border-radius: 4px; }}

/* ── Section label ── */
.section-label {{
  font-family: 'Fira Code', monospace;
  font-size: 0.62rem;
  letter-spacing: 3.5px;
  text-transform: uppercase;
  color: rgba(var(--glow), 0.6);
  margin-bottom: 10px;
}}

/* ── Footer ── */
.app-footer {{
  text-align: center;
  font-family: 'Fira Code', monospace;
  font-size: 0.6rem;
  letter-spacing: 2px;
  color: rgba(255,255,255,0.12);
  margin-top: 28px;
  text-transform: uppercase;
}}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  MODE SELECTION SCREEN
# ═══════════════════════════════════════════════════════════════════════
if st.session_state.selected_mode is None:

    # Header
    st.markdown('<div class="brand">🎭 MoodBot</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">● AI personality engine &nbsp;·&nbsp; Select your vibe</div>', unsafe_allow_html=True)

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    # Decorative tiles
    st.markdown("""
    <div class="mode-grid">
      <div class="mode-tile angry">
        <span class="tile-emoji">😡</span>
        <div class="tile-label angry">Angry</div>
        <div class="tile-tag">Aggressive<br>Brutally Honest</div>
      </div>
      <div class="mode-tile funny">
        <span class="tile-emoji">😂</span>
        <div class="tile-label funny">Funny</div>
        <div class="tile-tag">Witty<br>Chaotically Joyful</div>
      </div>
      <div class="mode-tile sad">
        <span class="tile-emoji">😢</span>
        <div class="tile-label sad">Sad</div>
        <div class="tile-tag">Melancholy<br>Poetically Gloomy</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">↓ &nbsp; Choose a personality to begin</div>', unsafe_allow_html=True)

    c1_btn, c2_btn, c3_btn = st.columns(3)
    with c1_btn:
        if st.button("😡  Angry Mode", key="pick_angry"):
            st.session_state.selected_mode = "Angry"
            st.session_state.messages = [SystemMessage(content=MODES["Angry"]["system"])]
            st.session_state.chat_history = []
            st.rerun()
    with c2_btn:
        if st.button("😂  Funny Mode", key="pick_funny"):
            st.session_state.selected_mode = "Funny"
            st.session_state.messages = [SystemMessage(content=MODES["Funny"]["system"])]
            st.session_state.chat_history = []
            st.rerun()
    with c3_btn:
        if st.button("😢  Sad Mode", key="pick_sad"):
            st.session_state.selected_mode = "Sad"
            st.session_state.messages = [SystemMessage(content=MODES["Sad"]["system"])]
            st.session_state.chat_history = []
            st.rerun()

    st.markdown('<div class="app-footer">Built with LangChain · Mistral AI · Streamlit</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
#  CHAT SCREEN
# ═══════════════════════════════════════════════════════════════════════
else:
    cfg = MODES[st.session_state.selected_mode]

    # ── Header ──
    col_title, col_actions = st.columns([3, 1])
    with col_title:
        st.markdown('<div class="brand" style="font-size:2rem;">🎭 MoodBot</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-sub">● AI Personality Engine</div>', unsafe_allow_html=True)
    with col_actions:
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        if st.button("⇄ Switch", key="switch_btn"):
            st.session_state.selected_mode = None
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()

    # Active mode badge
    st.markdown(
        f'<div class="active-badge"><div class="badge-dot"></div>'
        f'{cfg["emoji"]} &nbsp; {cfg["label"]} MODE &nbsp;·&nbsp; {cfg["tag"]}</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

    # ── Chat area inside glass card ──
    st.markdown('<div class="glass-card" style="padding: 20px;">', unsafe_allow_html=True)

    html = '<div class="chat-scroll"><div class="chat-feed">'

    if not st.session_state.chat_history:
        html += f"""
        <div class="empty-chat">
          <div class="empty-emoji">{cfg["emoji"]}</div>
          <div class="empty-text">{cfg["welcome"]}</div>
        </div>"""
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                html += f"""
                <div class="msg-row user">
                  <div><div class="bubble user">{msg["text"]}</div></div>
                  <div class="avatar user">🧑</div>
                </div>"""
            else:
                html += f"""
                <div class="msg-row bot">
                  <div class="avatar bot">{cfg["emoji"]}</div>
                  <div><div class="bubble bot">{msg["text"]}</div></div>
                </div>"""

    html += '</div></div>'
    st.markdown(html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # close glass-card

    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

    # ── Input row ──
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            label="msg", label_visibility="collapsed",
            placeholder=f"Message the {st.session_state.selected_mode.lower()} bot...",
            key="chat_input"
        )
    with col_send:
        send = st.button("Send ➤", key="send_btn")

    # Clear chat link
    col_gap, col_clear = st.columns([5, 1])
    with col_clear:
        if st.button("🗑 Clear", key="clear_btn"):
            st.session_state.messages = [SystemMessage(content=cfg["system"])]
            st.session_state.chat_history = []
            st.rerun()

    st.markdown(
        f'<div class="app-footer">MoodBot · {cfg["emoji"]} {cfg["label"]} MODE · Powered by Mistral AI</div>',
        unsafe_allow_html=True
    )

    # ── Handle send ──
    if send and user_input.strip():
        prompt = user_input.strip()
        st.session_state.messages.append(HumanMessage(content=prompt))
        st.session_state.chat_history.append({"role": "user", "text": prompt})

        with st.spinner(f"{cfg['emoji']}  Thinking..."):
            response = model.invoke(st.session_state.messages)

        st.session_state.messages.append(AIMessage(content=response.content))
        st.session_state.chat_history.append({"role": "bot", "text": response.content})
        st.rerun()