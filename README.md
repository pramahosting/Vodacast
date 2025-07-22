# 🎙️ Prama Vodacast Pro - Advanced AI Voice Generation

An enhanced vodacast application with AI voice cloning capabilities using free packages and APIs.

## 🚀 Features

- **Multiple TTS Engines**: Google TTS, Coqui TTS, ElevenLabs
- **Voice Cloning**: Upload your own voice samples for custom voice generation
- **Multi-language Support**: Support for 10+ languages
- **Voice Customization**: Control speed, pitch, stability, and similarity
- **Real-time Audio Generation**: Generate and play audio instantly
- **File Upload**: Support for text file uploads
- **Audio Download**: Download generated audio as MP3

## 🛠️ Installation

### 1. Basic Setup

```bash
pip install streamlit gtts requests
```

### 2. Advanced Voice Cloning (Recommended)

```bash
pip install TTS torch soundfile librosa transformers
```

### 3. Optional Audio Processing

```bash
pip install pydub
```

### 4. All Dependencies

```bash
pip install -r requirements.txt
```

## 🎯 Voice Engines

### 1. Google TTS (Free)
- Completely free
- Good quality for basic use
- Multiple language support
- No setup required

### 2. Coqui TTS (Free AI)
- Advanced AI models
- Voice cloning capabilities
- Multilingual support
- Requires model downloads

### 3. ElevenLabs (Limited Free)
- Premium quality voices
- Advanced customization
- Limited free tier (10,000 characters/month)
- Requires API key

### 4. Custom Voice Upload
- Upload your own voice samples
- AI voice cloning using Coqui TTS
- 30 seconds to 5 minutes of audio recommended

## 🔧 Setup Instructions

### ElevenLabs API (Optional)

1. Sign up at [ElevenLabs](https://elevenlabs.io)
2. Get your API key from Profile Settings
3. Add to Streamlit secrets:

Create `.streamlit/secrets.toml`:
```toml
elevenlabs_api_key = "your_api_key_here"
```

Or set environment variable:
```bash
export ELEVENLABS_API_KEY="your_api_key_here"
```

### Coqui TTS Setup

The first time you use Coqui TTS, it will download the required models:
- Models are cached locally for future use
- Initial download may take a few minutes
- Requires internet connection for first setup

## 🎵 Voice Cloning Guide

### Best Practices for Voice Cloning

1. **Audio Quality**:
   - Use high-quality recordings (WAV preferred)
   - Minimize background noise
   - Clear, consistent speaking

2. **Audio Length**:
   - Minimum: 30 seconds
   - Recommended: 2-5 minutes
   - Maximum: 10 minutes (for best performance)

3. **Speaking Style**:
   - Speak naturally and consistently
   - Avoid whispering or shouting
   - Include varied sentence structures

4. **Technical Requirements**:
   - Sample rate: 22050 Hz or higher
   - Format: WAV, MP3, or M4A
   - Mono or stereo audio

## 🚀 Running the Application

```bash
streamlit run vodacast_enhanced.py
```

Then open your browser and navigate to `http://localhost:8501`

## 📱 Usage

1. **Select Voice Engine**: Choose from available TTS engines
2. **Choose Language**: Select your preferred language
3. **Customize Voice**: Adjust speed, pitch, and other settings
4. **Upload Audio** (for cloning): Upload reference audio file
5. **Enter Text**: Type or upload your text content
6. **Generate**: Click the generate button to create audio
7. **Download**: Save the generated audio file

## 🔍 Troubleshooting

### Common Issues

1. **Coqui TTS not working**:
   ```bash
   pip install TTS torch
   ```

2. **Audio playback issues**:
   ```bash
   pip install soundfile librosa
   ```

3. **ElevenLabs API errors**:
   - Check your API key
   - Verify account limits
   - Ensure internet connection

4. **Model download failures**:
   - Check internet connection
   - Clear model cache: `~/.cache/tts/`
   - Retry with different model

### Performance Optimization

1. **For faster generation**:
   - Use smaller text chunks (< 500 characters)
   - Choose appropriate model for your needs
   - Use GPU if available (CUDA)

2. **For better quality**:
   - Use higher-quality reference audio
   - Experiment with voice settings
   - Use appropriate language models

## 🌟 Advanced Features

### Voice Customization Options

- **Stability**: Controls voice consistency (0.0-1.0)
- **Similarity Boost**: Enhances voice similarity (0.0-1.0)
- **Speaking Speed**: Adjusts playback speed (0.5-2.0x)
- **Voice Pitch**: Modifies voice pitch (0.5-2.0x)

### Supported Languages

- English (en)
- Hindi (hi)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)

## 📊 Model Information

### Coqui TTS Models

1. **YourTTS**: Multilingual voice cloning
2. **VITS**: High-quality single speaker
3. **Tacotron2**: Reliable English TTS
4. **Fairseq**: Multilingual support (1100+ languages)

### ElevenLabs Models

1. **Eleven Monolingual v1**: English only, high quality
2. **Eleven Multilingual v1**: Multiple languages
3. **Eleven Turbo v2**: Fast generation

## 🤝 Contributing

Feel free to contribute to this project by:
1. Reporting bugs
2. Suggesting new features
3. Submitting pull requests
4. Improving documentation

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Coqui TTS**: For open-source voice synthesis
- **ElevenLabs**: For premium voice API
- **Google TTS**: For reliable basic TTS
- **Streamlit**: For the web framework

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the documentation
3. Submit an issue on GitHub

---

**Built with ❤️ using Python and Streamlit**
