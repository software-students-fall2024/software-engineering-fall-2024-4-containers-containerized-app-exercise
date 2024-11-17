import cv2
import numpy as np
from PIL import Image
import io
from deepface import DeepFace


class EmotionDetector:
    def __init__(self):
        """Initialize the emotion detector with supported emotions"""
        self.emotions = ["angry", "happy", "neutral", "sad", "surprise"]

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
                result = DeepFace.analyze(
                    img,
                    actions=["emotion"],
                    enforce_detection=True,
                    detector_backend="ssd",
                )
            except ValueError:
                # If no face is detected with strict enforcement
                try:
                    # Try again with enforce_detection=False
                    result = DeepFace.analyze(
                        img,
                        actions=["emotion"],
                        enforce_detection=False,
                        detector_backend="ssd",
                    )
                except Exception as e:
                    return {"status": "error", "error": "No face detected in the image"}

            # Get emotions from result
            emotions = result[0]["emotion"]

            # Filter and normalize emotions to match our emotion set
            filtered_emotions = {
                emotion: float(emotions.get(emotion, 0)) 
                for emotion in self.emotions
            }

            # Normalize probabilities to sum to 1
            total = sum(filtered_emotions.values())
            if total > 0:
                filtered_emotions = {
                    k: v/total 
                    for k, v in filtered_emotions.items()
                }

            # Sort emotions by probability
            sorted_emotions = dict(
                sorted(
                    filtered_emotions.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
            )

            return {
                "status": "success", 
                "emotions": sorted_emotions
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Error processing image: {str(e)}"
            }

    def preprocess_image(self, image_data):
        """
        Preprocess image data for detection

        Args:
            image_data: Image in bytes or numpy array format

        Returns:
            numpy.ndarray: Preprocessed image
        """
        try:
            if isinstance(image_data, bytes):
                # Convert bytes to numpy array
                nparr = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                img = image_data

            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            return img_rgb
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
