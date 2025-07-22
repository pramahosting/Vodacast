#!/usr/bin/env python3
"""
Prama Vodacast - Deployment Test Script
Tests all components to ensure proper setup
"""

import sys
import os
import tempfile
import time
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def test_python_version():
    """Test Python version"""
    print_header("Python Version Check")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python version too old. Requires Python 3.8+")
        return False

def test_basic_imports():
    """Test basic package imports"""
    print_header("Basic Package Import Test")
    
    packages = {
        'streamlit': 'Streamlit web framework',
        'gtts': 'Google Text-to-Speech',
        'requests': 'HTTP requests library',
        'tempfile': 'Temporary file handling',
        'pathlib': 'Path utilities',
        'json': 'JSON handling',
        'base64': 'Base64 encoding',
        'time': 'Time utilities',
        'os': 'Operating system interface'
    }
    
    success_count = 0
    for package, description in packages.items():
        try:
            __import__(package)
            print(f"✅ {package:12} - {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {package:12} - FAILED: {e}")
    
    print(f"\nImport test: {success_count}/{len(packages)} packages successful")
    return success_count == len(packages)

def test_audio_generation():
    """Test audio generation with gTTS"""
    print_header("Audio Generation Test")
    
    try:
        from gtts import gTTS
        
        # Test text
        test_text = "Hello! This is a test of the Prama Vodacast audio generation system."
        print(f"Test text: '{test_text}'")
        
        # Generate audio
        print("Generating audio with gTTS...")
        tts = gTTS(text=test_text, lang='en', slow=False)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_path = tmp_file.name
            tts.save(temp_path)
        
        # Check file
        if os.path.exists(temp_path):
            file_size = os.path.getsize(temp_path)
            print(f"✅ Audio file generated: {file_size:,} bytes")
            
            # Clean up
            os.remove(temp_path)
            return True
        else:
            print("❌ Audio file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Audio generation failed: {str(e)}")
        return False

def test_streamlit_compatibility():
    """Test Streamlit compatibility"""
    print_header("Streamlit Compatibility Test")
    
    try:
        import streamlit as st
        print(f"✅ Streamlit version: {st.__version__}")
        
        # Test key Streamlit functions
        test_functions = [
            'st.title',
            'st.text_area', 
            'st.button',
            'st.audio',
            'st.download_button',
            'st.sidebar',
            'st.columns',
            'st.file_uploader'
        ]
        
        for func_name in test_functions:
            if hasattr(st, func_name.split('.')[1]):
                print(f"✅ {func_name} - Available")
            else:
                print(f"❌ {func_name} - Missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit test failed: {str(e)}")
        return False

def test_file_permissions():
    """Test file system permissions"""
    print_header("File System Permissions Test")
    
    try:
        # Test writing to current directory
        test_file = "test_write_permissions.tmp"
        
        with open(test_file, 'w') as f:
            f.write("test data")
        
        if os.path.exists(test_file):
            print("✅ Write permissions - OK")
            os.remove(test_file)
        else:
            print("❌ Write permissions - FAILED")
            return False
        
        # Test temp directory
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(b"test data")
            print("✅ Temporary file creation - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ File permissions test failed: {str(e)}")
        return False

def test_internet_connection():
    """Test internet connectivity for gTTS"""
    print_header("Internet Connection Test")
    
    try:
        import requests
        
        # Test Google Translate service (used by gTTS)
        response = requests.get("https://translate.google.com", timeout=10)
        
        if response.status_code == 200:
            print("✅ Internet connection - OK")
            print("✅ Google Translate accessible - OK")
            return True
        else:
            print(f"❌ Google Translate returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Internet connection test failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Connection test error: {str(e)}")
        return False

def test_optional_packages():
    """Test optional advanced packages"""
    print_header("Optional Packages Test")
    
    optional_packages = {
        'torch': 'PyTorch (for AI models)',
        'TTS': 'Coqui TTS (for voice cloning)', 
        'cv2': 'OpenCV (for video processing)',
        'moviepy.editor': 'MoviePy (for video editing)',
        'numpy': 'NumPy (for numerical computing)',
        'PIL': 'Pillow (for image processing)'
    }
    
    available_count = 0
    for package, description in optional_packages.items():
        try:
            if '.' in package:
                module_parts = package.split('.')
                module = __import__(module_parts[0])
                for part in module_parts[1:]:
                    module = getattr(module, part)
            else:
                __import__(package)
            print(f"✅ {package:15} - {description}")
            available_count += 1
        except ImportError:
            print(f"⚠️  {package:15} - Not installed (optional)")
        except Exception as e:
            print(f"❌ {package:15} - Error: {str(e)}")
    
    print(f"\nOptional packages: {available_count}/{len(optional_packages)} available")
    return True  # This test doesn't fail, just reports status

def generate_test_report(results):
    """Generate a final test report"""
    print_header("Test Summary Report")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"Total tests run: {total_tests}")
    print(f"Tests passed: {passed_tests}")
    print(f"Tests failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Your setup is ready for deployment.")
        print("\nNext steps:")
        print("1. Run: streamlit run vodacast_enhanced.py")
        print("2. Open browser to: http://localhost:8501")
        print("3. Test the application with sample text")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED. Please address the issues above before deployment.")
        print("\nCommon solutions:")
        print("- Ensure virtual environment is activated")
        print("- Install missing packages: pip install streamlit gtts requests")
        print("- Check internet connection")
        print("- Verify file permissions")
        return False

def main():
    """Main test function"""
    print("🎬 Prama Vodacast Video Pro - Deployment Test")
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    test_results = {
        'Python Version': test_python_version(),
        'Basic Imports': test_basic_imports(), 
        'Audio Generation': test_audio_generation(),
        'Streamlit Compatibility': test_streamlit_compatibility(),
        'File Permissions': test_file_permissions(),
        'Internet Connection': test_internet_connection()
    }
    
    # Test optional packages (doesn't affect overall result)
    test_optional_packages()
    
    # Generate report
    success = generate_test_report(test_results)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
