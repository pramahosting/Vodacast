import streamlit as st
from gtts import gTTS
import tempfile
import os
import time
from io import BytesIO
import requests
import json
import base64
from pathlib import Path

# Try importing voice cloning libraries (install if needed)
try:
    from TTS.api import TTS
    import torch
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import soundfile as sf
    import numpy as np
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

# --------------------------
# Configuration
# --------------------------
ELEVENLABS_API_KEY = st.secrets.get("elevenlabs_api_key", "")  # Optional, for paid tier
ELEVENLABS_FREE_URL = "https://api.elevenlabs.io/v1/text-to-speech/"

# --------------------------
# Streamlit Page Setup
# --------------------------
st.set_page_config(page_title="🎙️ Prama Vodacast Pro", layout="wide")
st.title("🎙️ Prama Vodacast Pro")
st.markdown("Convert your text into speech with **AI Voice Cloning** and **Premium TTS**")

# --------------------------
# Sidebar for Voice Options
# --------------------------
st.sidebar.header("🎚️ Voice Settings")

# Voice Engine Selection
voice_engine = st.sidebar.selectbox(
    "Select Voice Engine",
    ["Google TTS (Free)", "Coqui TTS (Free AI)", "ElevenLabs (Limited Free)", "Upload Custom Voice"],
    help="Choose your preferred text-to-speech engine"
)

# Language Selection
language_options = {
    "Hindi": "hi",
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko"
}
lang_choice = st.sidebar.selectbox("Select Language", list(language_options.keys()))

# Voice customization options
if voice_engine != "Google TTS (Free)":
    st.sidebar.subheader("🎯 Voice Customization")
    voice_speed = st.sidebar.slider("Speaking Speed", 0.5, 2.0, 1.0, 0.1)
    voice_pitch = st.sidebar.slider("Voice Pitch", 0.5, 2.0, 1.0, 0.1)
    
    if voice_engine == "ElevenLabs (Limited Free)":
        stability = st.sidebar.slider("Voice Stability", 0.0, 1.0, 0.75, 0.05)
        similarity_boost = st.sidebar.slider("Similarity Boost", 0.0, 1.0, 0.75, 0.05)

# --------------------------
# Voice Cloning Section
# --------------------------
if voice_engine == "Upload Custom Voice":
    st.sidebar.subheader("🎤 Voice Cloning")
    uploaded_audio = st.sidebar.file_uploader(
        "Upload Reference Audio (WAV/MP3)", 
        type=["wav", "mp3", "m4a"],
        help="Upload 30 seconds to 5 minutes of clear speech for voice cloning"
    )
    
    if uploaded_audio is not None:
        st.sidebar.success("✅ Reference audio uploaded!")
        # Save uploaded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_audio.name.split('.')[-1]}") as tmp_audio:
            tmp_audio.write(uploaded_audio.read())
            reference_audio_path = tmp_audio.name

# --------------------------
# Helper Functions
# --------------------------
def generate_gtts_audio(text, lang):
    """Generate audio using Google TTS"""
    tts = gTTS(text=text, lang=lang, slow=False)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_file.name)
    
    with open(tmp_file.name, "rb") as f:
        audio_bytes = f.read()
    
    os.remove(tmp_file.name)
    return audio_bytes

def generate_coqui_tts_audio(text, lang, speed=1.0, reference_audio=None):
    """Generate audio using Coqui TTS with optional voice cloning"""
    if not TTS_AVAILABLE:
        st.error("Coqui TTS not installed. Install with: pip install TTS")
        return None
    
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if reference_audio:
            # Use voice cloning model
            model_name = "tts_models/multilingual/multi-dataset/your_tts"
            tts = TTS(model_name=model_name).to(device)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_output:
                tts.tts_to_file(
                    text=text,
                    speaker_wav=reference_audio,
                    language=language_options[lang_choice],
                    file_path=tmp_output.name
                )
                
                with open(tmp_output.name, "rb") as f:
                    audio_bytes = f.read()
                
                os.remove(tmp_output.name)
                return audio_bytes
        else:
            # Use default multilingual model
            model_name = f"tts_models/{language_options[lang_choice]}/fairseq/vits"
            try:
                tts = TTS(model_name=model_name).to(device)
            except:
                # Fallback to English model
                model_name = "tts_models/en/ljspeech/tacotron2-DDC"
                tts = TTS(model_name=model_name).to(device)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_output:
                tts.tts_to_file(text=text, file_path=tmp_output.name)
                
                with open(tmp_output.name, "rb") as f:
                    audio_bytes = f.read()
                
                os.remove(tmp_output.name)
                return audio_bytes
                
    except Exception as e:
        st.error(f"Coqui TTS Error: {str(e)}")
        return None

def generate_elevenlabs_audio(text, voice_id="21m00Tcm4TlvDq8ikWAM", stability=0.75, similarity_boost=0.75):
    """Generate audio using ElevenLabs API (free tier limited)"""
    if not ELEVENLABS_API_KEY:
        st.warning("ElevenLabs API key not configured. Using demo mode with limitations.")
        # For demo purposes, fall back to gTTS
        return generate_gtts_audio(text, language_options[lang_choice])
    
    url = f"{ELEVENLABS_FREE_URL}{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"ElevenLabs API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"ElevenLabs connection error: {str(e)}")
        return None

def apply_audio_effects(audio_bytes, speed=1.0, pitch=1.0):
    """Apply speed and pitch effects to audio (requires additional libraries)"""
    if not SOUNDFILE_AVAILABLE:
        return audio_bytes
    
    try:
        # This is a simplified version - in production you'd use librosa or pydub
        # For now, just return original audio
        return audio_bytes
    except:
        return audio_bytes

# --------------------------
# Main Interface
# --------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 Enter Text Manually or Upload a `.txt` File")
    text_input = st.text_area("Manual Text Input", height=200, 
                             placeholder="Enter your text here or upload a file...")

    uploaded_file = st.file_uploader("Or Upload Text File", type=["txt"])
    if uploaded_file is not None:
        try:
            file_text = uploaded_file.read().decode("utf-8")
            text_input = file_text
            st.success("✅ File uploaded and loaded successfully.")
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")

with col2:
    st.markdown("### 🎯 Quick Stats")
    if text_input:
        word_count = len(text_input.split())
        char_count = len(text_input)
        estimated_duration = word_count * 0.5  # Rough estimate: 0.5 seconds per word
        
        st.metric("Words", word_count)
        st.metric("Characters", char_count)
        st.metric("Est. Duration", f"{estimated_duration:.1f}s")

# --------------------------
# Installation Check and Warnings
# --------------------------
if voice_engine == "Coqui TTS (Free AI)" and not TTS_AVAILABLE:
    st.error("""
    🚨 **Coqui TTS not installed!**
    
    Install with: `pip install TTS torch`
    
    For voice cloning, also install: `pip install soundfile librosa`
    """)

# --------------------------
# Generate Audio Button
# --------------------------
if st.button("🎙️ Generate Voice", type="primary"):
    if not text_input.strip():
        st.warning("⚠️ Please enter some text or upload a file.")
    else:
        with st.spinner("🎵 Generating audio..."):
            audio_bytes = None
            
            if voice_engine == "Google TTS (Free)":
                audio_bytes = generate_gtts_audio(text_input, language_options[lang_choice])
                
            elif voice_engine == "Coqui TTS (Free AI)":
                if TTS_AVAILABLE:
                    audio_bytes = generate_coqui_tts_audio(
                        text_input, 
                        lang_choice, 
                        speed=voice_speed if 'voice_speed' in locals() else 1.0
                    )
                else:
                    st.error("Coqui TTS not available. Falling back to Google TTS.")
                    audio_bytes = generate_gtts_audio(text_input, language_options[lang_choice])
                    
            elif voice_engine == "ElevenLabs (Limited Free)":
                audio_bytes = generate_elevenlabs_audio(
                    text_input,
                    stability=stability if 'stability' in locals() else 0.75,
                    similarity_boost=similarity_boost if 'similarity_boost' in locals() else 0.75
                )
                
            elif voice_engine == "Upload Custom Voice":
                if 'reference_audio_path' in locals() and TTS_AVAILABLE:
                    audio_bytes = generate_coqui_tts_audio(
                        text_input, 
                        lang_choice, 
                        speed=voice_speed if 'voice_speed' in locals() else 1.0,
                        reference_audio=reference_audio_path
                    )
                else:
                    st.error("Please upload reference audio and ensure Coqui TTS is installed.")
            
            if audio_bytes:
                # Apply effects if specified
                if 'voice_speed' in locals() or 'voice_pitch' in locals():
                    audio_bytes = apply_audio_effects(
                        audio_bytes, 
                        speed=voice_speed if 'voice_speed' in locals() else 1.0,
                        pitch=voice_pitch if 'voice_pitch' in locals() else 1.0
                    )
                
                # Display results
                st.success("🎉 Audio generated successfully!")
                
                # Play audio
                st.audio(audio_bytes, format="audio/mp3")
                
                # Download button
                st.download_button(
                    label="📥 Download MP3",
                    data=audio_bytes,
                    file_name=f"prama_vodcast_{voice_engine.lower().replace(' ', '_')}_{int(time.time())}.mp3",
                    mime="audio/mpeg"
                )
                
                # Show generation info
                with st.expander("ℹ️ Generation Info"):
                    st.write(f"**Engine**: {voice_engine}")
                    st.write(f"**Language**: {lang_choice}")
                    st.write(f"**Text Length**: {len(text_input)} characters")
                    st.write(f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# --------------------------
# Installation Instructions
# --------------------------
with st.expander("🛠️ Installation Instructions"):
    st.markdown("""
    ### Required Packages:
    
    **Basic TTS (already included):**
    ```bash
    pip install streamlit gtts requests
    ```
    
    **For Advanced Voice Cloning:**
    ```bash
    pip install TTS torch soundfile librosa
    ```
    
    **For Audio Processing:**
    ```bash
    pip install pydub
    ```
    
    ### ElevenLabs Setup (Optional):
    1. Sign up at [ElevenLabs](https://elevenlabs.io)
    2. Get your API key from Profile Settings
    3. Add to Streamlit secrets or environment variables
    
    ### Voice Cloning Tips:
    - Use 30 seconds to 5 minutes of clear, high-quality audio
    - Avoid background noise
    - Speak naturally and consistently
    - WAV format recommended for best results
    """)

# --------------------------
# Footer
# --------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🎙️ <strong>Prama Vodacast Pro</strong> - Advanced AI Voice Generation</p>
    <p>Powered by Google TTS, Coqui TTS, and ElevenLabs | Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)

# Cleanup temporary files
try:
    if 'reference_audio_path' in locals():
        time.sleep(1)
        if os.path.exists(reference_audio_path):
            os.remove(reference_audio_path)
except:
    pass
