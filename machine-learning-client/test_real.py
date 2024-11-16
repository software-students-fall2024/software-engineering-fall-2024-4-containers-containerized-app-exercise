import cv2
from emotion_detector import EmotionDetector
from db_handler import DatabaseHandler
import uuid


def main():
    # 初始化检测器和数据库处理器
    detector = EmotionDetector()
    db_handler = DatabaseHandler()

    # 读取测试图片
    img = cv2.imread("tests/images/test_face3.jpg")
    if img is not None:
        # 生成唯一ID
        image_id = str(uuid.uuid4())

        # 检测情绪
        result = detector.detect_emotion(img)
        print("\nTest image result:")
        print("Status:", result.get("status"))
        if "status" in result and result["status"] == "success":
            # 保存到数据库
            db_handler.save_detection_result(image_id, result["emotions"])
            print("\nSaved to database with ID:", image_id)

            print("\nDetected emotions:")
            for emotion, score in result["emotions"].items():
                print(f"{emotion}: {score:.2f}")
    else:
        print("Failed to load image")


if __name__ == "__main__":
    main()
