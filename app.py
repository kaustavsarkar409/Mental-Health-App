from elevenlabs.client import ElevenLabs
import os
import streamlit as st
from crew import MentalHealthApp
from dotenv import load_dotenv
from gtts import gTTS
import re
import json
import urllib.request
import urllib.error

# --- Audio recorder for speech input (no ffmpeg dependency) ---
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import io

load_dotenv()
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
# Page config - must be called early!
st.set_page_config(page_title="Calm Nest", layout="centered", page_icon="🧠")

# --- Custom CSS: Premium calming glassmorphism & elegant style ---
st.markdown("""
    <style>
        /* Background: layered radial + linear gradient (mint, lavender, sky) */
        body {
            background:
                radial-gradient(ellipse at 60% 25%, #d4fcf9 0%, #f3e9fc 75%, transparent 100%),
                radial-gradient(ellipse at 15% 90%, #bcdffb 0%, #f1f5fe 95%, transparent 100%),
                linear-gradient(120deg,#e9fdf0 55%, #ece6ff 100%);
            min-height: 100vh;
            margin: 0;
            padding: 0;
        }
        .stApp {
            background: transparent;
        }
        /* Main content glassmorphism card */
        .main > div {
            background: rgba(255,255,255,0.78);
            backdrop-filter: blur(12px);
            border-radius: 32px;
            border: 1px solid rgba(255,255,255,0.55);
            box-shadow: 0 6px 36px 0 rgba(132,90,235, 0.07), 0 2px 26px 0 rgba(100,200,170, 0.03);
            padding: 3.4rem 2.4rem 2.5rem 2.4rem;
            margin-bottom: 2.1rem;
        }
        @media (max-width: 650px) {
            .main > div { padding: 1.2rem 0.6rem 1.1rem 0.6rem; }
        }
        html, body, [class*="css"]  {
            font-family: 'Inter', 'Plus Jakarta Sans', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            color: #1d2746;
            font-size: 1.08rem;
        }
        /* HERO TEXT & BADGE */
        .hero-outer {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: -18px;
            margin-bottom: 36px;
            animation: fadein-hero .95s cubic-bezier(.52,.02,.22,1);
        }
        .hero-badge {
            background: linear-gradient(95deg,#b3dec9 15%,#d5d6f6 90%);
            color: #3a5584;
            font-family: 'Inter',sans-serif;
            font-weight: 700;
            letter-spacing: 0.07em;
            font-size: 0.96rem;
            padding: 5px 22px;
            border-radius: 32px;
            box-shadow: 0 1.5px 12px 0 rgba(150,177,253,0.08);
            margin-bottom: 14px;
            opacity: 0.89;
            border: 0.6px solid #f1effc;
        }
        .hero-title {
            font-family: 'Plus Jakarta Sans', 'Inter',sans-serif;
            font-size: 2.44rem;
            font-weight: 800;
            letter-spacing: 0.02em;
            background: linear-gradient(92deg, #8768dd 25%, #67cfd2 85%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-fill-color: transparent;
            filter: drop-shadow(0 2px 10px #cabfff80);
            text-align: center;
            margin-bottom: 6px;
            text-shadow: 0 2.5px 12px #c4ebfa52,0 0.5px 1px #fff;
        }
        @media (max-width: 460px) {
            .hero-title {
                font-size: 2.05rem; /* reduce if needed for extra narrow screen */
            }
        }
        @media (max-width: 370px) {
            .hero-title {
                font-size: 1.7rem;
            }
        }
        .hero-sub {
            font-family: 'Inter',sans-serif;
            font-size: 1.16rem;
            font-weight: 500;
            color: #565b7c;
            text-align: center;
            margin-bottom: 21px;
            letter-spacing: 0.01em;
        }
        .hero-divider {
            height: 4px;
            width: 68px;
            border-radius: 9px;
            background: linear-gradient(90deg, #c4e8e1 0%, #dbd7fc 80%, #bae6fd 100%);
            margin: 0 auto 16px auto;
            opacity: 0.67;
        }
        .hero-icons {
            display: flex;
            gap: 19px;
            justify-content: center;
            margin-bottom: 2px;
            user-select: none;
        }
        .hero-icon {
            font-size: 1.45rem;
            opacity: 0.40;
            filter: blur(0.1px) drop-shadow(0 1.5px 4.5px #98beff32);
        }
        /* Inputs: Soft, padded & accessible */
        .stTextArea > label {
            color: #7056d1;
            font-family: 'Plus Jakarta Sans',sans-serif;
            font-weight: 700;
            font-size: 1.11rem;
            letter-spacing: 0.01em;
        }
        .stTextArea textarea {
            background: rgba(255,255,255, 0.75);
            border-radius: 17px;
            border: 1.6px solid #dcedf8;
            min-height: 104px;
            font-size: 1.09rem;
            color: #273573;
            box-shadow: 0 2px 16px 0 rgba(96,120,228,0.03);
            padding: 1.28rem 1.18rem;
            transition: border 0.2s, box-shadow 0.2s;
        }
        .stTextArea textarea:focus {
            border: 1.7px solid #a89df6;
            box-shadow: 0 0 0 2px #adcdf733, 0 4px 20px 0 rgba(48,204,206,0.05);
            outline: none;
        }
        /* Buttons: rounded pill, subtle gradient, hover lift */
        .stButton > button {
            background: linear-gradient(90deg, #b6daef 0%, #dacef7 100%);
            color: #4c4d6f;
            border-radius: 28px;
            font-family: 'Plus Jakarta Sans', 'Inter',sans-serif;
            font-weight: 800;
            font-size: 1.14rem;
            letter-spacing: .01em;
            box-shadow: 0 1.5px 16px 0 rgba(210,200,255,0.06);
            border: none;
            margin-top: 10px;
            transition: background 0.21s, transform 0.17s;
            padding: 0.8rem 2.7rem;
        }
        .stButton > button:hover {
            background: linear-gradient(90deg, #e6f6d7 0%, #cee6ff 100%);
            color: #6033b5;
            transform: translateY(-2px) scale(1.03);
        }
        /* Notification cards, hierarchy & radius */
        .stSuccess, .stWarning, .stError {
            border-radius: 20px !important;
            font-family: 'Inter',sans-serif;
        }
        .stDivider {
            margin-top: 24px;
            margin-bottom: 27px;
        }
        /* Audio player container: bordered card look */
        .stAudio {
            padding-top: 16px;
            background: rgba(249,251,255,0.52);
            border-radius: 18px;
            border: 1.3px solid #e5ebfa;
            box-shadow: 0 2px 8px 0 #e7eeff33;
            margin-bottom: 7px;
        }
        /* Subheader styled */
        .stSubheader {
            color: #82c7bb;
            font-family: 'Plus Jakarta Sans',sans-serif;
            font-weight: 700;
            font-size: 1.12rem;
        }
        /* Card for support message with fadein */
        .support-card {
            background: rgba(247,248,252,0.73);
            border-radius: 22px;
            border: 1.2px solid #d6e8fc;
            box-shadow: 0 2.5px 19px 0 rgba(110,221,217,0.04);
            padding: 1.06rem 1.35rem 1rem 1.35rem;
            margin-bottom: 22px;
            animation: fadein-comfort 1.6s cubic-bezier(.22,.64,.7,1.05);
        }
        /* Animated pulsing circle for feedback */
        .pulse-circle {
            width: 38px;
            height: 38px;
            margin: 0 auto 18px auto;
            background: linear-gradient(90deg, #baffeb 0%, #bda8f9 80%);
            border-radius: 50%;
            box-shadow: 0 2.5px 26px 4px #d5e1ff42;
            animation: pulse 1.4s infinite alternate;
        }
        @keyframes pulse {
            0% { box-shadow: 0 3px 26px 6px #c7f0f632; }
            100% { box-shadow: 0 2.5px 50px 8px #dadcff31;}
        }
        /* Fadein for hero */
        @keyframes fadein-hero {
            from { opacity: 0; transform: translateY(30px);}
            to   { opacity: 1; transform: translateY(0);}
        }
        /* Fadein for card */
        @keyframes fadein-comfort {
            from { opacity: 0; transform: translateY(38px);}
            to   { opacity: 1; transform: translateY(0);}
        }
        /* Decorative abstract pattern */
        .corner-art-abstract {
            position: fixed;
            bottom: 4vw;
            right: 3vw;
            width: 130px;
            opacity: 0.35;
            z-index: 0;
            pointer-events: none;
            display: none;
        }
        @media (min-width: 900px) {
            .corner-art-abstract { display: block; }
        }
        /* Typewriter animation for encouragement */
        .typewriter-text {
            overflow: hidden;
            border-right: .09em solid #7d8ee2;
            white-space: nowrap;
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
            font-size: 1.08rem;
            color: #767bc2;
            animation: typing 2.6s steps(38, end), blink-caret 0.72s step-end infinite;
        }
        @keyframes typing {
            from { width: 0 }
            to { width: 100% }
        }
        @keyframes blink-caret {
            from, to { border-color: transparent }
            50% { border-color: #7694eb; }
        }

        /* Auto dark mode support */
        @media (prefers-color-scheme: dark) {
            body {
                background:
                    radial-gradient(ellipse at 60% 18%, #1a2242 0%, #101727 75%, transparent 100%),
                    radial-gradient(ellipse at 12% 92%, #1e2f3d 0%, #0f1523 90%, transparent 100%),
                    linear-gradient(130deg, #0b1220 50%, #101629 100%);
            }
            .main > div {
                background: rgba(18, 24, 41, 0.82);
                border: 1px solid rgba(120, 145, 184, 0.25);
                box-shadow: 0 10px 38px rgba(0, 0, 0, 0.35);
            }
            html, body, [class*="css"] {
                color: #dbe6ff;
            }
            .hero-badge {
                background: linear-gradient(95deg, #31446c 10%, #4b3f7c 90%);
                color: #d9e5ff;
                border-color: rgba(178, 190, 224, 0.35);
            }
            .hero-sub {
                color: #aebde3;
            }
            .hero-divider {
                background: linear-gradient(90deg, #4f7fb3 0%, #7b66bc 80%, #5f90c8 100%);
                opacity: 0.75;
            }
            .hero-icon {
                opacity: 0.56;
                filter: drop-shadow(0 1px 3px rgba(87, 145, 209, 0.4));
            }
            .stTextArea > label {
                color: #bbc9ef;
            }
            .stTextArea textarea {
                background: rgba(20, 29, 47, 0.85);
                border: 1.5px solid rgba(122, 145, 188, 0.45);
                color: #e5ecff;
                box-shadow: 0 2px 14px rgba(0, 0, 0, 0.2);
            }
            .stTextArea textarea::placeholder {
                color: #95a6cf;
            }
            .stTextArea textarea:focus {
                border: 1.7px solid #8f9df5;
                box-shadow: 0 0 0 2px rgba(120, 151, 233, 0.2), 0 4px 18px rgba(45, 77, 148, 0.26);
            }
            .stButton > button {
                background: linear-gradient(90deg, #344f73 0%, #534985 100%);
                color: #edf2ff;
                box-shadow: 0 2px 14px rgba(0, 0, 0, 0.28);
            }
            .stButton > button:hover {
                background: linear-gradient(90deg, #456a8f 0%, #6b5ea7 100%);
                color: #ffffff;
            }
            .support-card {
                background: rgba(20, 29, 47, 0.85);
                border: 1.2px solid rgba(120, 144, 184, 0.36);
                box-shadow: 0 4px 18px rgba(0, 0, 0, 0.22);
                color: #e7efff;
            }
            .stAudio {
                background: rgba(20, 29, 47, 0.72);
                border: 1.2px solid rgba(121, 145, 189, 0.32);
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            }
            .typewriter-text {
                color: #b7c4e9;
                border-right-color: #9ab2f0;
            }
            .corner-art-abstract {
                opacity: 0.22;
            }
        }
    </style>
    <!-- Plus Jakarta Sans & Inter Fonts For Calm/Elegant UI -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# --- HERO HEADER (Pill badge, gradient title, subtitle, divider, minimal icons) ---
st.markdown("""
    <div class="hero-outer">
      <div class="hero-badge">Emotional Wellness Companion</div>
      <div class="hero-title">Calm Nest</div>
      <div class="hero-sub">
        A gentle space for reflection, clarity, and next steps.
      </div>
      <div class="hero-divider"></div>
      <div class="hero-icons">
        <span class="hero-icon">☁︎</span>
        <span class="hero-icon" style="font-size:1.22rem;">•</span>
        <span class="hero-icon">✦</span>
        <span class="hero-icon" style="font-size:1.22rem;">•</span>
        <span class="hero-icon">☾</span>
      </div>
    </div>
""", unsafe_allow_html=True)

# Decorative floating abstract pattern art in lower corner (pleasant, unobtrusive)
st.markdown(
    """
    <div class="corner-art-abstract">
      <svg width="130" height="100" viewBox="0 0 130 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="10" y="60" width="32" height="8" rx="4" fill="#bbf7d0"/>
        <rect x="75" y="25" width="22" height="7" rx="3.5" fill="#a7f3d0"/>
        <rect x="55" y="75" width="60" height="10" rx="5" fill="#fef9c3"/>
        <path d="M0,90 Q70,70 130,90" stroke="#6ee7b7" stroke-width="2.1" fill="none"/>
        <circle cx="36" cy="33" r="13" fill="#bae6fd" fill-opacity="0.7"/>
        <line x1="70" y1="10" x2="120" y2="35" stroke="#fcd34d" stroke-width="2.2" stroke-dasharray="7 8"/>
      </svg>
    </div>
    """,
    unsafe_allow_html=True,
)

user_input = st.text_area(
    "How are you feeling today?",
    placeholder="Share your thoughts, emotions, or concerns...",
    key="user_input"
)

# --- Audio input UI and transcription logic using audio_recorder_streamlit ---
def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        st.warning("Couldn't understand audio. Please try again.")
    except sr.RequestError:
        st.error("Speech service unavailable right now.")
    except Exception as e:
        st.error(f"Transcription failed: {e}")
    return ""

st.markdown("**Or speak your issue:**")
audio_bytes = audio_recorder(
    text="Click to record",
    recording_color="#e74c3c",
    neutral_color="#6aa36f",
    icon_name="microphone",
    icon_size="2x"
)

transcript = ""
if audio_bytes is not None:
    transcript = transcribe_audio_bytes(audio_bytes)
    if transcript:
        st.caption(f"Transcript: {transcript}")

# --- Input selection logic: prioritize typed, fallback to transcript ---
selected_input = user_input.strip() if user_input and user_input.strip() else transcript.strip() if transcript else ""

def remove_asterisks(text):
    """Remove asterisk characters from the text, both alone and around words (for markdown bold/italics)."""
    # Remove *      (any asterisk)
    no_asterisk = text.replace("*", "")
    return no_asterisk

def ensure_min_words(text, min_words=85):
    """If text is shorter than min_words, append calming filler until it is."""
    def count_words(t):
        return len(re.findall(r"\w+", t))
    calm_filler = (
        "Remember, it's okay to take things one breath at a time. "
        "Allow yourself to pause and notice the rhythm of your breathing. "
        "Every step you take, no matter how small, is valuable. "
        "Give yourself permission to slow down, honor your own pace, "
        "and return gently to the present moment whenever you need. "
        "Consistency over urgency will help you find steadier ground."
    )
    text_out = text
    while count_words(text_out) < min_words:
        text_out += "\n\n" + calm_filler
    return text_out

def build_voice_script(result_text: str):
    """
    Given the long, sectioned AI result, create a friendly spoken summary:
      - Remove any asterisks.
      - Parse into named sections.
      - Use Section 1 for summary, use action steps ONLY from Section 3 (not 2).
      - If Section 3 is missing, use imperative lines from the whole text.
      - End with a supportive closing.
      - Ensure minimum length for ~30s speech.
    """
    text = remove_asterisks(result_text)

    # Identify all 'Section N:' and known headings and split accordingly
    # This regex is greedy; we build all knowledge of section positions
    # Accept headings like 'Section 1: Title', 'Situation Summary:', etc.

    # First, build regular expressions for finding section positions
    section_headers_patterns = [
        (1, r"(Section\s*1[:\.\-\s]*.*|Situation Summary\s*[:\-\s]*.*)", "Section 1"),
        (2, r"(Section\s*2[:\.\-\s]*.*|What Might Be Contributing\s*[:\-\s]*.*)", "Section 2"),
        (3, r"(Section\s*3[:\.\-\s]*.*|What You Can Do Next\s*[:\-\s]*.*)", "Section 3"),
        (4, r"(Section\s*4[:\.\-\s]*.*|Support Message\s*[:\-\s]*.*)", "Section 4"),
    ]

    # Find the positions of each section in the text
    sections_found = {}
    text_lower = text.lower()
    lines = text.splitlines()
    section_indices = {}  # Section index: line number

    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        for sn, pat, _label in section_headers_patterns:
            if re.match(pat, line_lower, re.IGNORECASE):
                if sn not in section_indices:
                    section_indices[sn] = i

    # Sort by section number and get boundaries
    sorted_sections = sorted(section_indices.items())
    section_texts = {}  # Section N -> text
    for idx, (sn, start) in enumerate(sorted_sections):
        # End is the next section (or end of lines)
        end = sorted_sections[idx + 1][1] if (idx + 1) < len(sorted_sections) else len(lines)
        # Remove the heading line itself (start), get the rest as section text
        section_content = "\n".join(lines[start + 1:end]).strip()
        section_texts[sn] = section_content

    # Fallback: If the text lacked headings, treat whole text as Section 1
    if not section_texts:
        section_texts[1] = text.strip()

    # Build summary (Section 1) for opening
    summary = ""
    if 1 in section_texts:
        s = section_texts[1].strip()
        # Use the first sentence or up to the first period
        if s:
            summary = s.split('\n')[0].strip().split(".")[0] + "."
    else:
        # fallback: first nonempty paragraph
        p = [p for p in text.strip().split("\n\n") if p.strip()]
        if p:
            summary = p[0].split(".")[0] + "."

    # Build actionables -- ONLY from Section 3 (What You Can Do Next) for list.
    section3_actionables = []
    if 3 in section_texts:
        sec3 = section_texts[3]
        # Bullets: *, -, •, or '1.', '2.' etc
        bullets = re.findall(r"^(?:[\*\-\u2022]|\d+\.)\s*(.+)", sec3, flags=re.MULTILINE)
        # Imperative lines: (starts with verbs, 'You can', etc)
        imperative_lines = [
            line.strip() for line in sec3.split('\n')
            if re.match(r"^(Try|Take|Remember|Consider|Practice|Ask|Reach|Give|You can|Plan|Schedule|Allow|Permit|Notice|Set|Remind|Pause|Reflect|Go|Focus|Write|Imagine|List|Identify|Allow yourself|If possible|Choose|Engage|Talk|Speak|Rest|Step|Create|Allow|Notice)\b", line.strip(), re.IGNORECASE)
            and len(line.strip().split()) > 3
        ]
        section3_actionables = bullets + imperative_lines

    # If section3_actionables exists, use that; otherwise extract imperative lines from full text
    if section3_actionables:
        actionables = section3_actionables
    else:
        # Extract imperative lines from the whole text (not just section by section)
        actionables = [
            line.strip() for line in text.split('\n')
            if re.match(r"^(Try|Take|Remember|Consider|Practice|Ask|Reach|Give|You can|Plan|Schedule|Allow|Permit|Notice|Set|Remind|Pause|Reflect|Go|Focus|Write|Imagine|List|Identify|Allow yourself|If possible|Choose|Engage|Talk|Speak|Rest|Step|Create|Allow|Notice)\b", line.strip(), re.IGNORECASE)
            and len(line.strip().split()) > 3
        ]

    # Deduplicate/clean and limit to 5 (as before)
    seen = set()
    clean_actionables = []
    for act in actionables:
        a = act.strip()
        a = re.sub(r'^[\*\-\u2022]?\s*', '', a)
        if a and a.lower() not in seen:
            seen.add(a.lower())
            clean_actionables.append(a)
    actionable_statements = clean_actionables[:5]  # up to 5 actionables

    # Compose natural language spoken script
    voice_script = ""
    if summary:
        voice_script += summary + "\n\n"
    if actionable_statements:
        voice_script += "Here is what you can do now:\n"
        for act in actionable_statements:
            # Speak as sentences (ensure ends with a period)
            if not act.endswith(('.', '!', '?')):
                act += '.'
            voice_script += f"{act}\n"
    else:
        # fallback
        voice_script += "Take a moment to notice how you're feeling and allow yourself to pause. Small steps matter.\n\n"
    # Nice closing
    voice_script += "Remember, your progress is real, and each step is meaningful. Be gentle with yourself."

    voice_script = ensure_min_words(voice_script, min_words=85)
    return voice_script


def translate_to_bengali(text: str) -> str:
    """Translate narration text to Bengali using OpenRouter."""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    base_url = os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1").rstrip("/")
    if not api_key or not text.strip():
        return text

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Translate the user's text into natural, conversational Bengali (Bangla). "
                    "Keep meaning, tone, and structure. Output only Bengali text."
                ),
            },
            {"role": "user", "content": text},
        ],
        "temperature": 0.2,
    }

    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            translated = data["choices"][0]["message"]["content"].strip()
            return translated if translated else text
    except Exception:
        # Fallback to original text if translation fails.
        return text

# Text to audio (using ElevenLabs free voice, fallback to gTTS if fails)
def text_to_audio(text):
    # Use the ElevenLabs "Rachel" free default model voice
    rachel_voice_id = "EXAVITQu4vr4xnSDxMaL"  # Rachel's ID (free)
    text = remove_asterisks(text)
    text = translate_to_bengali(text)
    # Use up to 1200 chars (should be plenty for ~30sec audio, adjust if limit is lower at provider)
    max_chars = 1200
    text = text[:max_chars]
    try:
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=rachel_voice_id,
            model_id="eleven_multilingual_v2"
        )
        with open("output.mp3", "wb") as f:
            for chunk in audio:
                f.write(chunk)
    except Exception as e:
        # Fallback: Use gTTS if ElevenLabs free fails, or notify user
        try:
            tts = gTTS(text, lang='bn')
            tts.save("output.mp3")
            st.info("Used fallback (gTTS) for audio due to ElevenLabs error.")
        except Exception as inner_e:
            st.error(f"Audio generation failed with ElevenLabs: {e}\n"
                     f"Also failed with gTTS: {inner_e}")

# Main button for user action with animation
button = st.button(
    "Get Support and Guidance",
    help="Click to receive gentle, personalized support",
    type="primary"
)

if button:
    if not selected_input:
        st.warning("Please enter something first, or record your message.")
    else:
        # Pulse animation as feedback while processing
        placeholder = st.empty()
        with st.spinner("Analyzing and generating support for you..."):
            placeholder.markdown('<div class="pulse-circle"></div>', unsafe_allow_html=True)
            try:
                result = MentalHealthApp().crew().kickoff(
                    inputs={"user_input": selected_input}
                )
                result = str(result)
                placeholder.empty()

                # Remove asterisks for output and audio
                encouragement = (
                    "Just a gentle reminder: you're already doing better than you think."
                )
                encouragement_plain = remove_asterisks(encouragement)
                result_plain = remove_asterisks(result)

                st.markdown(
                    f'<div class="typewriter-text" style="margin-bottom:10px;">{encouragement_plain}</div>',
                    unsafe_allow_html=True
                )

                # --- Separate voice output is now a summary, not sectioned text ---
                voice_text = build_voice_script(result)

                text_to_audio(voice_text)

                # Success notification (still visual, disco icon removed for premium feel)
                st.success(
                    "Personalized AI support ready &mdash; listen below for your gentle guidance.",
                    icon="💬"
                )
                st.markdown(
                    "<style>.stAlert span {font-size: 1.03rem !important;}</style>", 
                    unsafe_allow_html=True
                )

                st.divider()

                # Support message card with fadein
                st.markdown(
                    f"""
                    <div class="support-card">
                        <span style="font-size:1.07rem;">{result_plain.strip()}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Animated sound wave icon before audio
                st.markdown(
                    """
                    <div style="display:flex;justify-content:center;align-items:center;gap:13px;margin-bottom:5px;">
                      <svg height="36" width="58" style="vertical-align:middle;">
                        <rect x="7" width="7" height="25" y="6" rx="3.5" fill="#a7f3d0">
                          <animate attributeName="height" values="15;28;15" dur="1.1s" repeatCount="indefinite" />
                          <animate attributeName="y" values="13;2;13" dur="1.1s" repeatCount="indefinite" />
                        </rect>
                        <rect x="19" width="7" height="35" y="1" rx="3.5" fill="#fcd34d">
                          <animate attributeName="height" values="22;34;22" dur="0.84s" repeatCount="indefinite" />
                          <animate attributeName="y" values="8;2;8" dur="0.84s" repeatCount="indefinite" />
                        </rect>
                        <rect x="31" width="7" height="22" y="10" rx="3.5" fill="#a5b4fc">
                          <animate attributeName="height" values="16;24;16" dur="1.05s" repeatCount="indefinite" />
                          <animate attributeName="y" values="14;8;14" dur="1.05s" repeatCount="indefinite" />
                        </rect>
                        <rect x="43" width="7" height="29" y="4" rx="3.5" fill="#f9a8d4">
                          <animate attributeName="height" values="22;29;22" dur="0.96s" repeatCount="indefinite" />
                          <animate attributeName="y" values="8;4;8" dur="0.96s" repeatCount="indefinite" />
                        </rect>
                      </svg>
                      <span style="color:#6c91ac;font-size:1.02rem;font-weight:600;">Soothing audio message</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                st.audio("output.mp3")

            except Exception as e:
                placeholder.empty()
                st.error(f"Something went wrong: {e}")