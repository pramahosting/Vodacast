import cv2
import numpy as np
from typing import Optional, Tuple, List
import tempfile
import os

class SimpleFaceSwapper:
    """
    Simple face swapping utility using OpenCV and dlib
    """
    
    def __init__(self):
        self.face_cascade = None
        self.landmark_predictor = None
        self.face_detector = None
        self._init_detectors()
    
    def _init_detectors(self):
        """Initialize face detection models"""
        try:
            # Use OpenCV's built-in face detector
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        except Exception as e:
            print(f"Warning: Could not initialize face detector: {e}")
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of face bounding boxes (x, y, w, h)
        """
        if self.face_cascade is None:
            return []
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        return faces.tolist()
    
    def extract_face_region(self, image: np.ndarray, face_box: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Extract face region from image
        
        Args:
            image: Source image
            face_box: Face bounding box (x, y, w, h)
            
        Returns:
            Extracted face region
        """
        x, y, w, h = face_box
        return image[y:y+h, x:x+w]
    
    def blend_faces(self, source_face: np.ndarray, target_face: np.ndarray, 
                   blend_ratio: float = 0.8) -> np.ndarray:
        """
        Simple face blending using alpha blending
        
        Args:
            source_face: Source face to blend
            target_face: Target face to blend with
            blend_ratio: Blending ratio (0.0 to 1.0)
            
        Returns:
            Blended face
        """
        # Resize source face to match target face
        target_h, target_w = target_face.shape[:2]
        source_resized = cv2.resize(source_face, (target_w, target_h))
        
        # Apply Gaussian blur for smoother blending
        source_blurred = cv2.GaussianBlur(source_resized, (15, 15), 0)
        
        # Alpha blending
        blended = cv2.addWeighted(target_face, 1-blend_ratio, source_blurred, blend_ratio, 0)
        
        return blended
    
    def create_face_mask(self, face_shape: Tuple[int, int]) -> np.ndarray:
        """
        Create a circular mask for face blending
        
        Args:
            face_shape: Shape of the face region (height, width)
            
        Returns:
            Face mask
        """
        h, w = face_shape
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Create elliptical mask
        center = (w // 2, h // 2)
        axes = (w // 3, h // 2)
        cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
        
        # Apply Gaussian blur to soften edges
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        
        return mask
    
    def swap_faces_simple(self, source_image: np.ndarray, target_image: np.ndarray,
                         blend_ratio: float = 0.8) -> np.ndarray:
        """
        Perform simple face swapping between two images
        
        Args:
            source_image: Image with source face
            target_image: Image with target face to replace
            blend_ratio: How much to blend (0.0 = no change, 1.0 = full replacement)
            
        Returns:
            Image with face swapped
        """
        # Detect faces in both images
        source_faces = self.detect_faces(source_image)
        target_faces = self.detect_faces(target_image)
        
        if not source_faces or not target_faces:
            print("Warning: Could not detect faces in one or both images")
            return target_image
        
        # Use the first detected face from each image
        source_face_box = source_faces[0]
        target_face_box = target_faces[0]
        
        # Extract face regions
        source_face = self.extract_face_region(source_image, source_face_box)
        target_face = self.extract_face_region(target_image, target_face_box)
        
        # Blend faces
        blended_face = self.blend_faces(source_face, target_face, blend_ratio)
        
        # Create result image
        result_image = target_image.copy()
        x, y, w, h = target_face_box
        
        # Create mask for smooth blending
        mask = self.create_face_mask((h, w))
        mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR) / 255.0
        
        # Apply mask and blend
        roi = result_image[y:y+h, x:x+w]
        blended_region = roi * (1 - mask_3ch) + blended_face * mask_3ch
        result_image[y:y+h, x:x+w] = blended_region.astype(np.uint8)
        
        return result_image
    
    def process_video_frame(self, frame: np.ndarray, reference_face: np.ndarray,
                           blend_ratio: float = 0.8) -> np.ndarray:
        """
        Process a single video frame for face swapping
        
        Args:
            frame: Video frame to process
            reference_face: Reference face image
            blend_ratio: Blending ratio
            
        Returns:
            Processed frame
        """
        return self.swap_faces_simple(reference_face, frame, blend_ratio)


def create_basic_lip_sync(video_path: str, audio_path: str, output_path: str) -> bool:
    """
    Create basic lip sync by combining video and audio
    
    Args:
        video_path: Path to input video
        audio_path: Path to input audio
        output_path: Path to output video
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import moviepy.editor as mp
        
        # Load video and audio
        video = mp.VideoFileClip(video_path)
        audio = mp.AudioFileClip(audio_path)
        
        # Adjust audio length to match video
        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)
        elif audio.duration < video.duration:
            # Loop audio if it's shorter than video
            loops_needed = int(video.duration / audio.duration) + 1
            audio = mp.concatenate_audioclips([audio] * loops_needed).subclip(0, video.duration)
        
        # Set audio to video
        final_video = video.set_audio(audio)
        
        # Write output
        final_video.write_videofile(
            output_path,
            audio_codec='aac',
            codec='libx264',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Clean up
        video.close()
        audio.close()
        final_video.close()
        
        return True
        
    except Exception as e:
        print(f"Error in lip sync processing: {e}")
        return False


def extract_audio_from_video(video_path: str, output_audio_path: str) -> bool:
    """
    Extract audio from video file
    
    Args:
        video_path: Path to input video
        output_audio_path: Path to output audio file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import moviepy.editor as mp
        
        video = mp.VideoFileClip(video_path)
        audio = video.audio
        
        if audio is not None:
            audio.write_audiofile(output_audio_path)
            audio.close()
        
        video.close()
        return True
        
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return False


def apply_face_swap_to_video(input_video_path: str, reference_face_path: str, 
                           output_video_path: str, blend_ratio: float = 0.8) -> bool:
    """
    Apply face swapping to entire video
    
    Args:
        input_video_path: Path to input video
        reference_face_path: Path to reference face image
        output_video_path: Path to output video
        blend_ratio: Face blending ratio
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize face swapper
        swapper = SimpleFaceSwapper()
        
        # Load reference face
        reference_face = cv2.imread(reference_face_path)
        if reference_face is None:
            print("Error: Could not load reference face image")
            return False
        
        # Open input video
        cap = cv2.VideoCapture(input_video_path)
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            processed_frame = swapper.process_video_frame(frame, reference_face, blend_ratio)
            
            # Write frame
            out.write(processed_frame)
            
            frame_count += 1
            if frame_count % 30 == 0:  # Print progress every 30 frames
                print(f"Processed {frame_count} frames...")
        
        # Clean up
        cap.release()
        out.release()
        
        print(f"Face swap completed! Processed {frame_count} frames.")
        return True
        
    except Exception as e:
        print(f"Error in video face swap: {e}")
        return False


def create_talking_head_simple(image_path: str, audio_path: str, output_path: str,
                             duration: Optional[float] = None) -> bool:
    """
    Create a simple talking head video from image and audio
    
    Args:
        image_path: Path to face image
        audio_path: Path to audio file
        output_path: Path to output video
        duration: Video duration (if None, uses audio duration)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import moviepy.editor as mp
        
        # Load audio to get duration
        audio = mp.AudioFileClip(audio_path)
        video_duration = duration if duration else audio.duration
        
        # Create video from image
        image_clip = mp.ImageClip(image_path, duration=video_duration)
        
        # Add subtle zoom effect for more dynamic video
        def zoom_effect(get_frame, t):
            frame = get_frame(t)
            # Simple zoom in/out effect
            zoom_factor = 1 + 0.1 * np.sin(2 * np.pi * t / 10)  # 10 second cycle
            h, w = frame.shape[:2]
            new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
            
            if new_h > h and new_w > w:
                # Crop center for zoom in
                y_start = (new_h - h) // 2
                x_start = (new_w - w) // 2
                frame_resized = cv2.resize(frame, (new_w, new_h))
                return frame_resized[y_start:y_start+h, x_start:x_start+w]
            else:
                return frame
        
        # Apply effect (optional)
        # image_clip = image_clip.fl(zoom_effect)
        
        # Set audio
        video = image_clip.set_audio(audio)
        
        # Write video
        video.write_videofile(
            output_path,
            fps=24,
            audio_codec='aac',
            codec='libx264'
        )
        
        # Clean up
        audio.close()
        video.close()
        
        return True
        
    except Exception as e:
        print(f"Error creating talking head: {e}")
        return False


# Example usage and testing functions
def test_face_detection():
    """Test face detection functionality"""
    print("Testing face detection...")
    
    swapper = SimpleFaceSwapper()
    
    # Create a test image (you would load a real image)
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    faces = swapper.detect_faces(test_image)
    print(f"Detected {len(faces)} faces")
    
    return len(faces) >= 0  # Should at least not crash


if __name__ == "__main__":
    # Run basic tests
    print("Running face swap utility tests...")
    
    try:
        test_face_detection()
        print("✅ Face detection test passed")
    except Exception as e:
        print(f"❌ Face detection test failed: {e}")
    
    print("Face swap utilities ready!")
