from emotion_detector import EmotionDetector
from db_handler import DatabaseHandler
import uuid

def process_image(image_data):
    """
    Process an image and save results to database
    
    Args:
        image_data: Image data in bytes
    
    Returns:
        dict: Processing results
    """
    detector = EmotionDetector()
    db_handler = DatabaseHandler()
    
    # Generate unique ID for the image
    image_id = str(uuid.uuid4())
    
    # Detect emotions
    result = detector.detect_emotion(image_data)
    
    # Save to database if detection was successful
    if "status" in result and result["status"] == "success":
        db_handler.save_detection_result(image_id, result["emotions"])
    
    return result

if __name__ == "__main__":
    # This is just for testing
    import cv2
    test_image = cv2.imread("tests/images/test_face.jpg")
    if test_image is not None:
        result = process_image(test_image)
        print(result) 