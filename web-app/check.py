import cv2
index = 0
while True:
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        break
    print(f"Camera index {index} is available")
    cap.release()
    index += 1
