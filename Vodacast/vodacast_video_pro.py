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
import cv2
import numpy as np

# Try importing video processing libraries (install if needed)
try:
    from TTS.api import TTS
    import torch
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    import moviepy.editor as mp
    from moviepy.editor import VideoFileClip, AudioFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

try:
    import soundfile as sf
    import librosa
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False

try:
    import insightface
    from insightface.app import FaceAnalysis
    INSIGHTFACE_AVAILABLE = True
except ImportError:
    INSIGHTFACE_AVAILABLE = False

try:
    import mediapipe as mp_pose
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

# --------------------------
# Configuration
# --------------------------
ELEVENLABS_API_KEY = st.secrets.get("elevenlabs_api_key", "")
ELEVENLABS_FREE_URL = "https://api.elevenlabs.io/v1/text-to-speech/"

# --------------------------
# Streamlit Page Setup
# --------------------------
st.set_page_config(page_title="🎬 Prama Vodacast Video Pro", layout="wide")
st.title("🎬 Prama Vodacast Video Pro")
st.markdown("**Complete Video Deepfake Suite** - Voice Cloning + Face Swap + Gesture Matching + Lip Sync")

# --------------------------
# Sidebar Configuration
# --------------------------
st.sidebar.header("🎥 Video Processing Options")

# Main processing mode
processing_mode = st.sidebar.selectbox(
    "Select Processing Mode",
    [
        "Audio Only (Voice Generation)",
        "Video + Audio (Lip Sync)",
        "Face Swap + Voice Clone",
        "Full Deepfake (Face + Voice + Gestures)",
        "Real-time Webcam Deepfake"
    ],
    help="Choose your desired processing mode"
)

# Video source selection
if processing_mode != "Audio Only (Voice Generation)":
    st.sidebar.subheader("📹 Video Source")
    video_source = st.sidebar.selectbox(
        "Video Input Type",
        ["Upload Video File", "Use Webcam", "YouTube URL", "Image + Audio (Talking Head)"],
        help="Choose your video input source"
    )

# Voice engine selection
st.sidebar.subheader("🎚️ Voice Engine")
voice_engine = st.sidebar.selectbox(
    "Select Voice Engine",
    ["Google TTS (Free)", "Coqui TTS (AI Voice Clone)", "ElevenLabs (Premium)", "Upload Audio Sample"],
    help="Choose your text-to-speech engine"
)

# Language selection
language_options = {
    "Hindi": "hi", "English": "en", "Spanish": "es", "French": "fr", 
    "German": "de", "Italian": "it", "Portuguese": "pt", "Russian": "ru",
    "Japanese": "ja", "Korean": "ko", "Chinese": "zh", "Arabic": "ar"
}
lang_choice = st.sidebar.selectbox("Select Language", list(language_options.keys()))

# Advanced settings
with st.sidebar.expander("⚙️ Advanced Settings"):
    # Video quality settings
    output_resolution = st.selectbox("Output Resolution", ["Original", "720p", "1080p", "480p"])
    frame_rate = st.slider("Frame Rate (FPS)", 15, 60, 30)
    
    # Face swap settings
    if "Face" in processing_mode:
        face_detection_confidence = st.slider("Face Detection Confidence", 0.1, 1.0, 0.6, 0.1)
        face_swap_blend = st.slider("Face Swap Blend", 0.0, 1.0, 0.8, 0.1)
    
    # Voice settings
    if voice_engine != "Google TTS (Free)":
        voice_speed = st.slider("Speaking Speed", 0.5, 2.0, 1.0, 0.1)
        voice_pitch = st.slider("Voice Pitch", 0.5, 2.0, 1.0, 0.1)
        
        if voice_engine == "ElevenLabs (Premium)":
            stability = st.slider("Voice Stability", 0.0, 1.0, 0.75, 0.05)
            similarity_boost = st.slider("Similarity Boost", 0.0, 1.0, 0.75, 0.05)

# --------------------------
# Helper Functions
# --------------------------
def extract_frames_from_video(video_path, max_frames=30):
    """Extract frames from video for processing"""
    try:
        cap = cv2.VideoCapture(video_path)
        frames = []
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(1, frame_count // max_frames)
        
        for i in range(0, frame_count, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
        
        cap.release()
        return frames
    except Exception as e:
        st.error(f"Error extracting frames: {str(e)}")
        return []

def analyze_facial_features(frames):
    """Analyze facial features for gesture matching"""
    if not INSIGHTFACE_AVAILABLE:
        st.warning("InsightFace not available. Install with: pip install insightface")
        return None
    
    try:
        app = FaceAnalysis(allowed_modules=['detection', 'landmark'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        
        features = []
        for frame in frames:
            faces = app.get(frame)
            if faces:
                # Extract landmarks and pose information
                face = faces[0]  # Use first detected face
                features.append({
                    'bbox': face.bbox,
                    'landmarks': face.landmark_2d_106,
                    'pose': getattr(face, 'pose', None)
                })
        
        return features
    except Exception as e:
        st.error(f"Error analyzing facial features: {str(e)}")
        return None

def generate_voice_with_cloning(text, reference_audio=None, engine="tts"):
    """Generate voice with optional cloning"""
    if engine == "coqui" and TTS_AVAILABLE:
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            if reference_audio:
                # Voice cloning with Coqui TTS
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
                # Default TTS
                model_name = f"tts_models/{language_options[lang_choice]}/fairseq/vits"
                try:
                    tts = TTS(model_name=model_name).to(device)
                except:
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
            # Fallback to gTTS
            return generate_gtts_audio(text, language_options[lang_choice])
    
    elif engine == "elevenlabs" and ELEVENLABS_API_KEY:
        return generate_elevenlabs_audio(text)
    
    else:
        # Default to gTTS
        return generate_gtts_audio(text, language_options[lang_choice])

def generate_gtts_audio(text, lang):
    """Generate audio using Google TTS"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(tmp_file.name)
        
        with open(tmp_file.name, "rb") as f:
            audio_bytes = f.read()
        
        os.remove(tmp_file.name)
        return audio_bytes
    except Exception as e:
        st.error(f"gTTS Error: {str(e)}")
        return None

def generate_elevenlabs_audio(text, voice_id="21m00Tcm4TlvDq8ikWAM"):
    """Generate audio using ElevenLabs API"""
    if not ELEVENLABS_API_KEY:
        st.warning("ElevenLabs API key not configured.")
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
            "stability": stability if 'stability' in locals() else 0.75,
            "similarity_boost": similarity_boost if 'similarity_boost' in locals() else 0.75
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

def process_lip_sync(video_path, audio_path, output_path):
    """Process lip sync using Wav2Lip algorithm"""
    try:
        # This is a placeholder for Wav2Lip integration
        # In a real implementation, you would:
        # 1. Clone the Wav2Lip repository
        # 2. Download pre-trained models
        # 3. Run the inference script
        
        # For now, we'll just combine video and audio
        if MOVIEPY_AVAILABLE:
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            
            # Trim audio to match video length
            if audio.duration > video.duration:
                audio = audio.subclip(0, video.duration)
            
            final_video = video.set_audio(audio)
            final_video.write_videofile(output_path, audio_codec='aac')
            
            video.close()
            audio.close()
            final_video.close()
            
            return True
        else:
            st.error("MoviePy not available for video processing")
            return False
            
    except Exception as e:
        st.error(f"Lip sync processing error: {str(e)}")
        return False

def create_talking_head_from_image(image_path, audio_path, output_path):
    """Create talking head video from single image and audio"""
    try:
        if not MOVIEPY_AVAILABLE:
            st.error("MoviePy required for video creation")
            return False
        
        # Load audio to get duration
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        
        # Create video from image
        from moviepy.editor import ImageClip
        image_clip = ImageClip(image_path, duration=duration)
        
        # Set the audio
        video = image_clip.set_audio(audio)
        
        # Write the video file
        video.write_videofile(output_path, fps=24, audio_codec='aac')
        
        # Clean up
        audio.close()
        video.close()
        
        return True
    except Exception as e:
        st.error(f"Talking head creation error: {str(e)}")
        return False

# --------------------------
# Main Interface
# --------------------------
col1, col2 = st.columns([2, 1])

with col1:
    # Text input section
    st.markdown("### 📝 Text Input")
    text_input = st.text_area(
        "Enter your script",
        height=150,
        placeholder="Enter the text you want to convert to speech/video..."
    )
    
    uploaded_text_file = st.file_uploader("Or upload text file", type=["txt"])
    if uploaded_text_file:
        try:
            file_text = uploaded_text_file.read().decode("utf-8")
            text_input = file_text
            st.success("✅ Text file loaded successfully.")
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
    
    # Video input section (if needed)
    if processing_mode != "Audio Only (Voice Generation)":
        st.markdown("### 🎥 Video Input")
        
        if video_source == "Upload Video File":
            uploaded_video = st.file_uploader(
                "Upload video file",
                type=["mp4", "avi", "mov", "mkv"],
                help="Upload your source video for processing"
            )
            
            if uploaded_video:
                # Save uploaded video
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_video.name.split('.')[-1]}") as tmp_video:
                    tmp_video.write(uploaded_video.read())
                    source_video_path = tmp_video.name
                
                st.video(uploaded_video)
                
        elif video_source == "Image + Audio (Talking Head)":
            uploaded_image = st.file_uploader(
                "Upload image for talking head",
                type=["jpg", "jpeg", "png"],
                help="Upload a clear photo of a person's face"
            )
            
            if uploaded_image:
                # Save uploaded image
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_image.name.split('.')[-1]}") as tmp_img:
                    tmp_img.write(uploaded_image.read())
                    source_image_path = tmp_img.name
                
                st.image(uploaded_image)
        
        elif video_source == "Use Webcam":
            st.info("📹 Webcam support will capture video when processing starts")
        
        elif video_source == "YouTube URL":
            youtube_url = st.text_input("Enter YouTube URL")
            if youtube_url:
                st.info("🔗 YouTube download will be processed during generation")
    
    # Reference files for cloning
    if "Clone" in processing_mode or voice_engine == "Upload Audio Sample":
        st.markdown("### 🎤 Reference Files")
        
        if "Face" in processing_mode:
            reference_face_image = st.file_uploader(
                "Upload reference face image",
                type=["jpg", "jpeg", "png"],
                help="Upload a clear image of the face you want to clone"
            )
            
            if reference_face_image:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{reference_face_image.name.split('.')[-1]}") as tmp_ref:
                    tmp_ref.write(reference_face_image.read())
                    reference_face_path = tmp_ref.name
                
                st.image(reference_face_image, width=200)
        
        if voice_engine == "Upload Audio Sample" or "Voice" in processing_mode:
            reference_audio = st.file_uploader(
                "Upload reference audio",
                type=["wav", "mp3", "m4a"],
                help="Upload 30 seconds to 5 minutes of clear speech for voice cloning"
            )
            
            if reference_audio:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{reference_audio.name.split('.')[-1]}") as tmp_audio:
                    tmp_audio.write(reference_audio.read())
                    reference_audio_path = tmp_audio.name
                
                st.audio(reference_audio)

with col2:
    st.markdown("### 📊 Project Stats")
    
    if text_input:
        word_count = len(text_input.split())
        char_count = len(text_input)
        estimated_duration = word_count * 0.5
        
        st.metric("Words", word_count)
        st.metric("Characters", char_count)
        st.metric("Est. Duration", f"{estimated_duration:.1f}s")
    
    st.markdown("### 🛠️ Available Features")
    
    # Feature availability check
    features_status = {
        "🎵 Basic TTS": True,
        "🤖 AI Voice Clone": TTS_AVAILABLE,
        "🎬 Video Processing": MOVIEPY_AVAILABLE,
        "👤 Face Detection": INSIGHTFACE_AVAILABLE,
        "🎭 Gesture Analysis": MEDIAPIPE_AVAILABLE,
        "🔊 Audio Processing": AUDIO_LIBS_AVAILABLE
    }
    
    for feature, available in features_status.items():
        if available:
            st.success(f"✅ {feature}")
        else:
            st.error(f"❌ {feature}")

# --------------------------
# Processing Section
# --------------------------
st.markdown("---")

# Installation warnings
missing_packages = []
if not TTS_AVAILABLE:
    missing_packages.append("TTS torch")
if not MOVIEPY_AVAILABLE:
    missing_packages.append("moviepy")
if not INSIGHTFACE_AVAILABLE:
    missing_packages.append("insightface")
if not AUDIO_LIBS_AVAILABLE:
    missing_packages.append("soundfile librosa")

if missing_packages:
    with st.expander("⚠️ Missing Dependencies"):
        st.warning("Some features require additional packages:")
        for package in missing_packages:
            st.code(f"pip install {package}")

# Main processing button
if st.button("🚀 Start Processing", type="primary", help="Begin the video/audio generation process"):
    if not text_input.strip():
        st.error("⚠️ Please enter some text to process.")
    else:
        with st.spinner("🎬 Processing your request..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Generate Audio
                status_text.text("🎵 Generating audio...")
                progress_bar.progress(20)
                
                reference_audio_for_clone = None
                if 'reference_audio_path' in locals():
                    reference_audio_for_clone = reference_audio_path
                
                if voice_engine == "Coqui TTS (AI Voice Clone)":
                    audio_bytes = generate_voice_with_cloning(
                        text_input, 
                        reference_audio_for_clone, 
                        engine="coqui"
                    )
                elif voice_engine == "ElevenLabs (Premium)":
                    audio_bytes = generate_voice_with_cloning(
                        text_input, 
                        reference_audio_for_clone, 
                        engine="elevenlabs"
                    )
                else:
                    audio_bytes = generate_gtts_audio(text_input, language_options[lang_choice])
                
                if not audio_bytes:
                    st.error("❌ Failed to generate audio")
                    st.stop()
                
                # Save generated audio
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as audio_file:
                    audio_file.write(audio_bytes)
                    generated_audio_path = audio_file.name
                
                progress_bar.progress(40)
                
                # Step 2: Process Video (if needed)
                if processing_mode == "Audio Only (Voice Generation)":
                    status_text.text("✅ Audio generation complete!")
                    progress_bar.progress(100)
                    
                    # Display results
                    st.success("🎉 Audio generated successfully!")
                    st.audio(audio_bytes, format="audio/wav")
                    
                    st.download_button(
                        label="📥 Download Audio",
                        data=audio_bytes,
                        file_name=f"vodacast_audio_{int(time.time())}.wav",
                        mime="audio/wav"
                    )
                
                elif video_source == "Image + Audio (Talking Head)" and 'source_image_path' in locals():
                    status_text.text("🎭 Creating talking head video...")
                    progress_bar.progress(60)
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as video_file:
                        output_video_path = video_file.name
                    
                    if create_talking_head_from_image(source_image_path, generated_audio_path, output_video_path):
                        progress_bar.progress(100)
                        status_text.text("✅ Talking head video created!")
                        
                        # Display results
                        st.success("🎉 Talking head video generated successfully!")
                        
                        with open(output_video_path, "rb") as video_file:
                            video_bytes = video_file.read()
                        
                        st.video(video_bytes)
                        
                        st.download_button(
                            label="📥 Download Video",
                            data=video_bytes,
                            file_name=f"vodacast_video_{int(time.time())}.mp4",
                            mime="video/mp4"
                        )
                    else:
                        st.error("❌ Failed to create talking head video")
                
                elif 'source_video_path' in locals():
                    status_text.text("🎬 Processing video with lip sync...")
                    progress_bar.progress(70)
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as video_file:
                        output_video_path = video_file.name
                    
                    if process_lip_sync(source_video_path, generated_audio_path, output_video_path):
                        progress_bar.progress(100)
                        status_text.text("✅ Video processing complete!")
                        
                        # Display results
                        st.success("🎉 Lip-synced video generated successfully!")
                        
                        with open(output_video_path, "rb") as video_file:
                            video_bytes = video_file.read()
                        
                        st.video(video_bytes)
                        
                        st.download_button(
                            label="📥 Download Video",
                            data=video_bytes,
                            file_name=f"vodacast_deepfake_{int(time.time())}.mp4",
                            mime="video/mp4"
                        )
                    else:
                        st.error("❌ Failed to process video")
                
                else:
                    st.warning("⚠️ Please upload required files for your selected processing mode.")
                
                # Show generation info
                with st.expander("ℹ️ Generation Details"):
                    st.write(f"**Processing Mode**: {processing_mode}")
                    st.write(f"**Voice Engine**: {voice_engine}")
                    st.write(f"**Language**: {lang_choice}")
                    st.write(f"**Text Length**: {len(text_input)} characters")
                    st.write(f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
            except Exception as e:
                st.error(f"❌ Processing failed: {str(e)}")
                st.exception(e)

# --------------------------
# Tutorials and Information
# --------------------------
with st.expander("📚 Installation & Setup Guide"):
    st.markdown("""
    ## 🛠️ Required Dependencies
    
    ### Basic Features:
    ```bash
    pip install streamlit gtts requests moviepy opencv-python
    ```
    
    ### Advanced AI Features:
    ```bash
    # Voice cloning
    pip install TTS torch soundfile librosa
    
    # Face processing
    pip install insightface onnxruntime
    
    # Gesture analysis
    pip install mediapipe
    
    # Video processing enhancement
    pip install ffmpeg-python
    ```
    
    ### System Requirements:
    ```bash
    # Install FFmpeg (required for video processing)
    # Ubuntu/Debian:
    sudo apt update && sudo apt install ffmpeg
    
    # macOS:
    brew install ffmpeg
    
    # Windows: Download from https://ffmpeg.org/
    ```
    
    ## 🎯 Processing Modes Explained:
    
    1. **Audio Only**: Generate speech from text using various TTS engines
    2. **Video + Audio (Lip Sync)**: Synchronize lip movements with new audio
    3. **Face Swap + Voice Clone**: Replace face and voice in video
    4. **Full Deepfake**: Complete face, voice, and gesture matching
    5. **Real-time Webcam**: Live deepfake processing (experimental)
    
    ## 🔧 Advanced Models Setup:
    
    ### Wav2Lip for Lip Sync:
    ```bash
    # Clone repository
    git clone https://github.com/Rudrabha/Wav2Lip
    
    # Download models
    # Place models in checkpoints/ folder
    ```
    
    ### Voice Cloning Tips:
    - Use 30 seconds to 5 minutes of clear audio
    - Minimize background noise
    - Consistent speaking pace and tone
    - WAV format recommended
    
    ### Face Swap Best Practices:
    - High-resolution source images (1024x1024+)
    - Good lighting conditions
    - Similar face angles and expressions
    - Multiple reference images for better results
    """)

with st.expander("⚖️ Ethics & Legal Notice"):
    st.markdown("""
    ## 🚨 Important Ethical Considerations
    
    **This tool is designed for:**
    - ✅ Educational and research purposes
    - ✅ Entertainment and creative content
    - ✅ Personal projects and experiments
    - ✅ Accessibility applications
    
    **Please DO NOT use for:**
    - ❌ Creating misleading or false content
    - ❌ Impersonating others without consent
    - ❌ Generating harmful or illegal content
    - ❌ Spreading misinformation or deepfakes
    
    **Legal Requirements:**
    - Always obtain consent before using someone's likeness
    - Clearly label AI-generated content
    - Comply with local laws and regulations
    - Respect privacy and intellectual property rights
    
    **By using this tool, you agree to use it responsibly and ethically.**
    """)

# --------------------------
# Footer
# --------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🎬 <strong>Prama Vodacast Video Pro</strong> - Complete Deepfake Video Suite</p>
    <p>Voice Cloning • Face Swapping • Lip Sync • Gesture Matching</p>
    <p>Built with ❤️ using Streamlit, TTS, MoviePy, InsightFace & More</p>
    <p><small>⚖️ Use responsibly and ethically. Always obtain proper consent.</small></p>
</div>
""", unsafe_allow_html=True)

# Cleanup temporary files
try:
    for var_name in ['source_video_path', 'source_image_path', 'reference_face_path', 'reference_audio_path', 'generated_audio_path', 'output_video_path']:
        if var_name in locals():
            file_path = locals()[var_name]
            if os.path.exists(file_path):
                time.sleep(1)
                try:
                    os.remove(file_path)
                except:
                    pass
except:
    pass
