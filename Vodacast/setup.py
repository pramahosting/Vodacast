#!/usr/bin/env python3
"""
Setup script for Prama Vodacast Pro
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🎙️ Setting up Prama Vodacast Pro...")
    print("=" * 50)
    
    # Basic packages
    basic_packages = [
        "streamlit>=1.28.0",
        "gtts>=2.3.2", 
        "requests>=2.31.0"
    ]
    
    # Advanced packages for voice cloning
    advanced_packages = [
        "torch>=2.0.0",
        "TTS>=0.22.0",
        "soundfile>=0.12.1",
        "librosa>=0.10.1",
        "transformers>=4.30.0"
    ]
    
    # Optional packages
    optional_packages = [
        "pydub>=0.25.1",
        "elevenlabs>=0.2.25"
    ]
    
    print("📦 Installing basic packages...")
    for package in basic_packages:
        print(f"  Installing {package}...")
        if install_package(package):
            print(f"  ✅ {package} installed successfully")
        else:
            print(f"  ❌ Failed to install {package}")
    
    print("\n🤖 Installing AI packages...")
    for package in advanced_packages:
        print(f"  Installing {package}...")
        if install_package(package):
            print(f"  ✅ {package} installed successfully")
        else:
            print(f"  ⚠️ Failed to install {package} (optional)")
    
    print("\n🔧 Installing optional packages...")
    for package in optional_packages:
        print(f"  Installing {package}...")
        if install_package(package):
            print(f"  ✅ {package} installed successfully")
        else:
            print(f"  ⚠️ Failed to install {package} (optional)")
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("\n📚 Next steps:")
    print("1. Run: streamlit run vodacast_enhanced.py")
    print("2. Open browser: http://localhost:8501")
    print("3. Start creating amazing voices!")
    print("\n💡 For ElevenLabs API:")
    print("   - Sign up at https://elevenlabs.io")
    print("   - Get your API key")
    print("   - Add to .streamlit/secrets.toml")

if __name__ == "__main__":
    main()
