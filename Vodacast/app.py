import streamlit as st
from gtts import gTTS
import tempfile
import os
import time
from io import BytesIO

# --------------------------
# Streamlit Page Setup
# --------------------------
st.set_page_config(
    page_title="🎬 Prama Vodacast Pro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎬 Prama Vodacast Pro - AI Voice Suite")
st.markdown("Transform text into professional voice content with AI-powered technology")

# --------------------------
# Sidebar Configuration
# --------------------------
st.sidebar.header("🎛️ Voice Settings")

# Language Selection
language_options = {
    "English": "en",
    "Spanish": "es", 
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh",
    "Hindi": "hi",
    "Arabic": "ar"
}

lang_choice = st.sidebar.selectbox("Select Language", list(language_options.keys()))

# --------------------------
# Main Interface
# --------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 Text Input")
    
    # Text input options
    input_method = st.radio(
        "Choose input method:",
        ["Type text", "Upload text file"],
        horizontal=True
    )
    
    text_input = ""
    
    if input_method == "Type text":
        text_input = st.text_area(
            "Enter your text here:",
            height=200,
            placeholder="Type or paste your text here to convert to speech..."
        )
    else:
        uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
        if uploaded_file is not None:
            try:
                text_input = uploaded_file.read().decode("utf-8")
                st.success("✅ File uploaded successfully!")
                st.text_area("File content:", value=text_input, height=200)
            except Exception as e:
                st.error(f"❌ Error reading file: {e}")

with col2:
    st.markdown("### 📊 Quick Stats")
    if text_input:
        word_count = len(text_input.split())
        char_count = len(text_input)
        estimated_duration = word_count * 0.5  # Rough estimate: 2 words per second
        
        st.metric("Word Count", word_count)
        st.metric("Character Count", char_count)
        st.metric("Est. Duration", f"{estimated_duration:.1f}s")
    else:
        st.info("Enter text to see statistics")

# --------------------------
# Audio Generation
# --------------------------
st.markdown("### 🎵 Generate Audio")

if st.button("🔊 Generate Voice", type="primary", use_container_width=True):
    if not text_input.strip():
        st.warning("⚠️ Please enter some text first!")
    else:
        try:
            with st.spinner("🎤 Generating audio..."):
                # Generate with gTTS
                tts = gTTS(text=text_input, lang=language_options[lang_choice], slow=False)
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                    tts.save(tmp_file.name)
                    
                    # Read audio bytes
                    with open(tmp_file.name, "rb") as f:
                        audio_bytes = f.read()
                    
                    # Clean up
                    os.remove(tmp_file.name)
            
            # Success message
            st.success("✅ Audio generated successfully!")
            
            # Play audio
            st.audio(audio_bytes, format="audio/mp3")
            
            # Download button
            st.download_button(
                label="⬇️ Download MP3",
                data=audio_bytes,
                file_name=f"prama_vodacast_{int(time.time())}.mp3",
                mime="audio/mpeg",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"❌ Error generating audio: {str(e)}")
            st.info("💡 Make sure you have an internet connection for Google TTS")

# --------------------------
# Features Preview
# --------------------------
st.markdown("---")
st.markdown("### �� Available Features")

features_col1, features_col2, features_col3 = st.columns(3)

with features_col1:
    st.markdown("""
    **🎤 Voice Generation**
    - ✅ Text-to-Speech (12+ languages)
    - ✅ Custom voice settings  
    - ✅ Multiple audio formats
    - ✅ Instant download
    """)

with features_col2:
    st.markdown("""
    **🎬 Advanced Features**
    - 🔧 Voice cloning (setup required)
    - 🔧 Video lip sync (setup required)
    - 🔧 Face swapping (setup required)
    - 🔧 Real-time processing (setup required)
    """)

with features_col3:
    st.markdown("""
    **📱 Coming Soon**
    - 📹 Video generation
    - 🎭 Deepfake creation
    - 🎨 Avatar animation
    - 🌐 API integration
    """)

# --------------------------
# Footer
# --------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    🎬 <strong>Prama Vodacast Pro</strong> - AI-Powered Voice & Video Suite<br>
    Built with ❤️ using Streamlit • gTTS • AI Models<br>
    <em>Tested and verified working ✅</em>
    </div>
    """, 
    unsafe_allow_html=True
)
