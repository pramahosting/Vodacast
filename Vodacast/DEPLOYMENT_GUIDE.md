# 🎬 Prama Vodacast Video Pro - Deployment Guide

## ✅ Testing Results

**Basic functionality has been tested and verified:**
- ✅ Streamlit (v1.47.0) - Working
- ✅ gTTS (v2.5.4) - Working and tested with audio generation
- ✅ Requests (v2.32.4) - Working
- ✅ Virtual environment setup - Working
- ✅ Basic audio generation (35KB MP3 file created successfully)

## 🚀 Quick Start Instructions

### Option 1: Basic Audio-Only Version (Recommended for Testing)

```bash
# 1. Clone or download the project files
cd /path/to/project

# 2. Create virtual environment
python3 -m venv vodacast_env

# 3. Activate virtual environment
source vodacast_env/bin/activate  # Linux/Mac
# or
vodacast_env\Scripts\activate  # Windows

# 4. Install basic dependencies
pip install streamlit gtts requests

# 5. Run the basic application
streamlit run vodacast_enhanced.py

# 6. Open browser to http://localhost:8501
```

### Option 2: Full Video Processing Version (Advanced)

```bash
# 1. System requirements
sudo apt update && sudo apt install -y python3-venv python3-pip ffmpeg

# 2. Create and activate virtual environment
python3 -m venv vodacast_env
source vodacast_env/bin/activate

# 3. Install full dependencies
pip install -r requirements_video.txt

# 4. Run the advanced application
streamlit run vodacast_video_pro.py

# 5. Open browser to http://localhost:8501
```

## 📋 System Requirements

### Minimum Requirements (Audio Only)
- Python 3.8+ (tested with Python 3.13.3)
- 2GB RAM
- 1GB free disk space
- Internet connection (for gTTS)

### Recommended Requirements (Video Processing)
- Python 3.8+
- 8GB+ RAM
- 4GB+ free disk space
- NVIDIA GPU (optional, for faster processing)
- ffmpeg installed

### Supported Operating Systems
- ✅ Ubuntu 20.04+ (tested)
- ✅ macOS 10.15+
- ✅ Windows 10+
- ✅ Docker (via containerization)

## 🛠️ Installation Methods

### Method 1: Automated Setup Script

```bash
# Run the automated setup
python3 setup.py

# This will install all dependencies automatically
```

### Method 2: Manual Installation

```bash
# Basic packages (always required)
pip install streamlit gtts requests numpy

# Video processing (optional)
pip install moviepy opencv-python

# AI/ML packages (optional, for advanced features)
pip install torch TTS transformers

# Face processing (optional, for face swap)
pip install insightface mediapipe

# Audio enhancement (optional)
pip install soundfile librosa pydub
```

### Method 3: Using Requirements Files

```bash
# For basic version
pip install -r requirements.txt

# For full video version
pip install -r requirements_video.txt
```

## 📁 Project Structure

```
vodacast_project/
├── vodacast_enhanced.py          # Basic audio app (original enhanced)
├── vodacast_video_pro.py         # Full video processing app
├── face_swap_utils.py            # Face swapping utilities
├── requirements.txt              # Basic dependencies
├── requirements_video.txt        # Full video dependencies
├── setup.py                      # Automated setup script
├── demo.py                       # Test functionality
├── README.md                     # Project documentation
├── DEPLOYMENT_GUIDE.md           # This file
└── .streamlit/
    ├── config.toml               # Streamlit configuration
    └── secrets.toml.example      # API keys template
```

## 🔧 Configuration

### Streamlit Configuration (.streamlit/config.toml)
```toml
[global]
developmentMode = true

[server]
port = 8501
headless = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
```

### API Keys Setup (.streamlit/secrets.toml)
```toml
# Copy from secrets.toml.example and fill in your keys
elevenlabs_api_key = "your_elevenlabs_api_key_here"
openai_api_key = "your_openai_api_key_here"  # Optional
```

## 🧪 Testing the Application

### 1. Run Demo Script
```bash
source vodacast_env/bin/activate
python3 demo.py
```

### 2. Basic Functionality Test
```bash
# Test basic imports
python3 -c "import streamlit, gtts, requests; print('✅ All basic packages working')"

# Test audio generation
python3 -c "
from gtts import gTTS
import tempfile
import os

tts = gTTS(text='Hello World', lang='en')
with tempfile.NamedTemporaryFile(suffix='.mp3') as f:
    tts.save(f.name)
    print(f'✅ Audio generation working: {os.path.getsize(f.name)} bytes')
"
```

### 3. Web Application Test
```bash
# Start the application
streamlit run vodacast_enhanced.py

# Test in browser:
# 1. Go to http://localhost:8501
# 2. Enter text: "Hello, this is a test"
# 3. Click "Generate Voice"
# 4. Verify audio plays and download works
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Issue: "ModuleNotFoundError"
```bash
# Solution: Ensure virtual environment is activated
source vodacast_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Issue: "FFmpeg not found"
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows: Download from https://ffmpeg.org/
```

#### Issue: "Permission denied" on Linux
```bash
# Make scripts executable
chmod +x setup.py demo.py
```

#### Issue: gTTS network error
```bash
# Check internet connection
# Try different language: lang='es' instead of 'en'
# Check firewall settings
```

#### Issue: Streamlit won't start
```bash
# Check if port 8501 is in use
lsof -i :8501

# Use different port
streamlit run vodacast_enhanced.py --server.port 8502
```

### Performance Issues

#### High memory usage
- Reduce video resolution in advanced settings
- Use CPU instead of GPU if memory limited
- Close other applications

#### Slow processing
- Install CUDA for GPU acceleration (NVIDIA cards)
- Use smaller video files for testing
- Enable caching in settings

## 🐳 Docker Deployment (Optional)

### Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "vodacast_enhanced.py", "--server.address", "0.0.0.0"]
```

### Build and Run
```bash
docker build -t vodacast .
docker run -p 8501:8501 vodacast
```

## 🌐 Cloud Deployment

### Streamlit Cloud
1. Push code to GitHub
2. Go to https://share.streamlit.io/
3. Connect repository
4. Add secrets in dashboard
5. Deploy

### Heroku
```bash
# Create Procfile
echo "web: streamlit run vodacast_enhanced.py --server.port \$PORT --server.headless true" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

### AWS/GCP/Azure
- Use container services (ECS, Cloud Run, Container Instances)
- Set up load balancer for high traffic
- Configure auto-scaling

## 📊 Performance Monitoring

### Built-in Metrics
- Check Streamlit metrics in browser developer tools
- Monitor memory usage with `htop` or Task Manager
- Check GPU usage with `nvidia-smi` (if applicable)

### Application Logs
```bash
# View Streamlit logs
streamlit run vodacast_enhanced.py --logger.level debug

# Save logs to file
streamlit run vodacast_enhanced.py 2>&1 | tee app.log
```

## 🔒 Security Considerations

### API Keys
- Never commit API keys to version control
- Use environment variables or secrets management
- Rotate keys regularly

### Network Security
- Use HTTPS in production
- Implement rate limiting
- Add authentication if needed

### Data Privacy
- Audio files are processed locally by default
- External API calls (gTTS, ElevenLabs) send data to third parties
- Add privacy notices for users

## 📈 Scaling and Production

### For High Traffic
- Use reverse proxy (nginx)
- Implement caching (Redis)
- Use CDN for static assets
- Scale horizontally with multiple instances

### Backup and Recovery
- Regular database backups (if using one)
- Code version control with Git
- Configuration management
- Monitoring and alerting

## 🔄 Updates and Maintenance

### Regular Tasks
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Check for security vulnerabilities
pip audit

# Update system packages
sudo apt update && sudo apt upgrade
```

### Version Control
- Tag releases with semantic versioning
- Keep changelog updated
- Test before deploying updates

## 📞 Support and Resources

### Getting Help
- Check this guide first
- Review error messages carefully
- Search GitHub issues
- Check Streamlit documentation

### Useful Links
- [Streamlit Documentation](https://docs.streamlit.io/)
- [gTTS Documentation](https://gtts.readthedocs.io/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

### Contributing
- Fork the repository
- Create feature branch
- Submit pull request
- Follow code style guidelines

---

## ✨ Quick Commands Reference

```bash
# Setup
python3 -m venv vodacast_env
source vodacast_env/bin/activate
pip install streamlit gtts requests

# Run
streamlit run vodacast_enhanced.py

# Test
python3 demo.py

# Update
pip install --upgrade -r requirements.txt

# Deactivate
deactivate
```

**🎉 You're ready to go! Start with the basic version and gradually add more features as needed.**
