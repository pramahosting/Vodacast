#!/usr/bin/env python3
"""
Demo script for Prama Vodacast Pro
Test the installation and basic functionality
"""

import sys
import os

def test_imports():
    """Test if required packages are installed"""
    print("🧪 Testing package imports...")
    
    # Test basic packages
    try:
        import streamlit as st
        print("  ✅ Streamlit imported successfully")
    except ImportError:
        print("  ❌ Streamlit not found - run: pip install streamlit")
        return False
    
    try:
        from gtts import gTTS
        print("  ✅ gTTS imported successfully")
    except ImportError:
        print("  ❌ gTTS not found - run: pip install gtts")
        return False
    
    try:
        import requests
        print("  ✅ Requests imported successfully")
    except ImportError:
        print("  ❌ Requests not found - run: pip install requests")
        return False
    
    # Test AI packages
    try:
        from TTS.api import TTS
        import torch
        print("  ✅ Coqui TTS imported successfully")
    except ImportError:
        print("  ⚠️ Coqui TTS not found (optional) - run: pip install TTS torch")
    
    try:
        import soundfile as sf
        import librosa
        print("  ✅ Audio processing libraries imported successfully")
    except ImportError:
        print("  ⚠️ Audio libraries not found (optional) - run: pip install soundfile librosa")
    
    return True

def test_gtts():
    """Test basic gTTS functionality"""
    print("\n🎵 Testing Google TTS...")
    
    try:
        from gtts import gTTS
        import tempfile
        import os
        
        # Create a simple TTS test
        text = "Hello, this is a test of Prama Vodacast Pro!"
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tts.save(tmp_file.name)
            file_size = os.path.getsize(tmp_file.name)
            os.remove(tmp_file.name)
        
        if file_size > 0:
            print(f"  ✅ Google TTS test successful (generated {file_size} bytes)")
            return True
        else:
            print("  ❌ Google TTS test failed (empty file)")
            return False
            
    except Exception as e:
        print(f"  ❌ Google TTS test failed: {str(e)}")
        return False

def test_coqui_tts():
    """Test Coqui TTS if available"""
    print("\n🤖 Testing Coqui TTS...")
    
    try:
        from TTS.api import TTS
        import torch
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"  📱 Using device: {device}")
        
        # Try to list available models
        tts = TTS()
        models = tts.list_models()
        if models:
            print(f"  ✅ Coqui TTS available with {len(models)} models")
            return True
        else:
            print("  ⚠️ Coqui TTS installed but no models found")
            return False
            
    except ImportError:
        print("  ⚠️ Coqui TTS not installed (optional)")
        return False
    except Exception as e:
        print(f"  ⚠️ Coqui TTS test failed: {str(e)}")
        return False

def main():
    print("🎙️ Prama Vodacast Pro - Demo Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Basic package test failed!")
        print("Please install required packages:")
        print("  pip install streamlit gtts requests")
        sys.exit(1)
    
    # Test gTTS
    gtts_success = test_gtts()
    
    # Test Coqui TTS
    coqui_success = test_coqui_tts()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Basic TTS (gTTS): {'✅ Working' if gtts_success else '❌ Failed'}")
    print(f"  Advanced AI TTS: {'✅ Working' if coqui_success else '⚠️ Not available'}")
    
    if gtts_success:
        print("\n🎉 Ready to run Prama Vodacast Pro!")
        print("Run: streamlit run vodacast_enhanced.py")
    else:
        print("\n❌ Setup incomplete. Please check the installation.")
    
    print("\n💡 Tips:")
    print("  - Use Google TTS for basic functionality")
    print("  - Install Coqui TTS for voice cloning: pip install TTS torch")
    print("  - Get ElevenLabs API key for premium voices")

if __name__ == "__main__":
    main()
