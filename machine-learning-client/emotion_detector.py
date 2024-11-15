import cv2
import numpy as np
from PIL import Image
import io
from deepface import DeepFace

class EmotionDetector:
    def __init__(self):
        self.emotions = ['angry', 'happy', 'neutral', 'sad', 'surprise']
        
    def detect_emotion(self, image_data):
        """
        Detect emotions in the given image
        
        Args:
            image_data: Image in bytes or numpy array format
            
        Returns:
            dict: Dictionary containing detected emotions and their probabilities
        """
        try:
            # Convert to numpy array if needed
            if isinstance(image_data, bytes):
                nparr = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.COLOR_BGR2RGB)
            else:
                img = image_data

            # First try to detect faces with enforce_detection=True
            try:
                result = DeepFace.analyze(img, 
                                        actions=['emotion'],
                                        enforce_detection=True,
                                        detector_backend='ssd')
            except ValueError:
                return {"error": "No face detected in the image"}
            
            # Get emotions from result
            emotions = result[0]['emotion']
            
            # Filter and normalize emotions to match our emotion set
            filtered_emotions = {
                emotion: float(emotions.get(emotion, 0))
                for emotion in self.emotions
            }
            # Sort emotions by probability
            sorted_emotions = dict(
                sorted(filtered_emotions.items(), key=lambda x: x[1], reverse=True)
            )
            
            return{
                "status": "success",
                "emotions": sorted_emotions
            }            
        except Exception as e:
            return {"error": f"Error processing image: {str(e)}"}