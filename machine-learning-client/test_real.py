import cv2
from emotion_detector import EmotionDetector

def main():
    # 初始化检测器
    detector = EmotionDetector()
    
    # 读取测试图片
    img = cv2.imread("tests/images/test_face3.jpg")
    if img is not None:
        # 检测情绪
        result = detector.detect_emotion(img)
        print("\nTest image result:")
        print("Status:", result.get("status"))
        if "emotions" in result:
            print("\nDetected emotions:")
            for emotion, score in result["emotions"].items():
                print(f"{emotion}: {score:.2f}")
    else:
        print("Failed to load image")

if __name__ == "__main__":
    main() 