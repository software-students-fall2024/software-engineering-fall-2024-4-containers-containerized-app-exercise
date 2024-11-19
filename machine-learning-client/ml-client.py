# # # import yolov5


# # # # load model
# # # model = yolov5.load('uisikdag/taskagitmakas')
  
# # # # set model parameters
# # # model.conf = 0.25  # NMS confidence threshold
# # # model.iou = 0.45  # NMS IoU threshold
# # # model.agnostic = False  # NMS class-agnostic
# # # model.multi_label = False  # NMS multiple labels per box
# # # model.max_det = 1000  # maximum number of detections per image

# # # # set image
# # # img = 'https://github.com/ultralytics/yolov5/raw/master/data/images/zidane.jpg'

# # # # perform inference
# # # results = model(img, size=640)

# # # # inference with test time augmentation
# # # results = model(img, augment=True)

# # # # parse results
# # # predictions = results.pred[0]
# # # boxes = predictions[:, :4] # x1, y1, x2, y2
# # # scores = predictions[:, 4]
# # # categories = predictions[:, 5]

# # # # show detection bounding boxes on image
# # # results.show()

# # # # save results into "results/" folder
# # # results.save(save_dir='results/')

# # # print(predictions)

# # from ultralytics import YOLO
# # import cv2




# # # Function to run inference on an image
# # def predict(image_path, model_path):
# #     """
# #     Predicts rock-paper-scissors gestures in an input image using a YOLO model.

# #     Args:
# #         image_path (str): Path to the image to process.
# #         model_path (str): Path to the YOLO model weights.
# #     """
# #     # Load the YOLO model
# #     model = YOLO(model_path)

# #     # Run inference
# #     results = model(image_path)

# #     # Display results
# #     results.show()  # Opens an annotated image in a pop-up window

# #     # Save the annotated image
# #     results.save("output/")  # Annotated images are saved in the 'output/' folder

# #     print("Results saved in the 'output/' directory.")


# # # Example usage
# # if __name__ == "__main__":
# #     import os

# #     # Path to your test image
# #     image_path = r"test_images/scissors_back (417).jpg"

# #     # Load the model from the local directory
# #     model_path = "models/best.pt"

# #     # Ensure the image exists before running
# #     if not os.path.exists(image_path):
# #         print(f"Error: Image file not found at {image_path}")
# #     else:
# #         # Run prediction
# #         predict(image_path, model_path)


# import torch
# from PIL import Image
# import cv2
# import matplotlib.pyplot as plt

# # Load YOLOv10 model with custom weights
# weights_path = "models/bestw.pt"  # Path to your weights file
# model = torch.hub.load('ultralytics/yolov5', 'custom', path=weights_path, force_reload=True)

# # Define the source image
# image_path = "test_images/scissors1.jpg"  # Path to your input image

# # Run the model on the image
# results = model(image_path)

# # Display results
# results.print()  # Print results in the terminal
# results.save(save_dir='runs/detect')  # Save results in the 'runs/detect' folder

# # # Optionally, display the image with detections in a notebook
# # detected_image_path = results.files[0]  # Path to the processed image
# # detected_image = cv2.imread(detected_image_path)
# # detected_image = cv2.cvtColor(detected_image, cv2.COLOR_BGR2RGB)  # Convert to RGB for matplotlib

# # plt.figure(figsize=(10, 10))
# # plt.imshow(detected_image)
# # plt.axis("off")
# # plt.show()