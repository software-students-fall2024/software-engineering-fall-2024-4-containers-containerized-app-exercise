# from tkinter import *
from PIL import Image
import cv2

# from tkinter import filedialog
import mediapipe as mp
from flask import Flask, request, jsonify
from pymongo import MongoClient

# import gridfs
from bson import ObjectId
from dotenv import load_dotenv
import os
import numpy as np
import base64
import io

load_dotenv()


# # Initialize the main window
# win = Tk()
# width = win.winfo_screenwidth()
# height = win.winfo_screenheight()
# win.geometry("%dx%d" % (width, height))
# win.configure(bg="#FFFFF7")
# win.title('Sign Language Converter')

# Label(win, text='Sign Language Converter', font=('Helvetica', 18, 'italic'), bd=5, bg='#199ef3', fg='white', relief=SOLID, width=200)\
#     .pack(pady=15, padx=300)

app = Flask(__name__)
client = MongoClient("mongodb://mongodb:27017/")

db = client.asl_db

# fs = gridfs.GridFS(db)


def base64ToNumpy(base64Img):
    image_data = base64.b64decode(base64Img)
    image = Image.open(io.BytesIO(image_data))
    return cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
    # return image
    
def numpyTobase64(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    # Encode the byte stream to Base64
    return base64.b64encode(buffer.read()).decode("utf-8")


def process_image(inputImage):
    global img, finalImage, finger_tips, thumb_tip, cap, image, rgb, hand, results, w, h, status, mpDraw, mpHands, hands, label1, cshow

    # Define Mediapipe hand-related variables
    finger_tips = [8, 12, 16, 20]
    thumb_tip = 4
    w, h = 500, 400
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils

    # global img, finalImage, cshow, label1, upCount, rgb, results
    cshow = ""

    # # Open file dialog to select image
    # file_path = filedialog.askopenfilename(initialdir="/", title="Select Image",
    #                                        filetypes=(("Image files", "*.jpg *.jpeg *.png"), ("all files", "*.*")))

    # if not file_path:
    #     return  # If no file is selected, return

    # Read and process the image
    img = base64ToNumpy(inputImage)  # cv2.imread(file_path)
    img = cv2.resize(img, (w, h))
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            lm_list = []
            for id, lm in enumerate(hand.landmark):
                lm_list.append(lm)
            finger_fold_status = []

            for tip in finger_tips:
                x, y = int(lm_list[tip].x * w), int(lm_list[tip].y * h)
                if lm_list[tip].x < lm_list[tip - 2].x:
                    finger_fold_status.append(True)
                else:
                    finger_fold_status.append(False)

            print(finger_fold_status)
            x, y = int(lm_list[8].x * w), int(lm_list[8].y * h)
            print(x, y)
            # stop
            if (
                lm_list[4].y < lm_list[2].y
                and lm_list[8].y < lm_list[6].y
                and lm_list[12].y < lm_list[10].y
                and lm_list[16].y < lm_list[14].y
                and lm_list[20].y < lm_list[18].y
                and lm_list[17].x < lm_list[0].x < lm_list[5].x
            ):
                cshow = "STOP ! Dont move."
            # okay
            elif (
                lm_list[4].y < lm_list[2].y
                and lm_list[8].y > lm_list[6].y
                and lm_list[12].y < lm_list[10].y
                and lm_list[16].y < lm_list[14].y
                and lm_list[20].y < lm_list[18].y
                and lm_list[17].x < lm_list[0].x < lm_list[5].x
            ):
                cshow = "Perfect , You did  a great job."

            # spidey
            elif (
                lm_list[4].y < lm_list[2].y
                and lm_list[8].y < lm_list[6].y
                and lm_list[12].y > lm_list[10].y
                and lm_list[16].y > lm_list[14].y
                and lm_list[20].y < lm_list[18].y
                and lm_list[17].x < lm_list[0].x < lm_list[5].x
            ):
                cshow = "Good to see you."

            # Point
            elif (
                lm_list[8].y < lm_list[6].y
                and lm_list[12].y > lm_list[10].y
                and lm_list[16].y > lm_list[14].y
                and lm_list[20].y > lm_list[18].y
            ):
                cshow = "You Come here."

            # Victory
            elif (
                lm_list[8].y < lm_list[6].y
                and lm_list[12].y < lm_list[10].y
                and lm_list[16].y > lm_list[14].y
                and lm_list[20].y > lm_list[18].y
            ):
                print("Yes , we won.")
                cshow = "Yes , we won."

            # Left
            elif (
                lm_list[4].y < lm_list[2].y
                and lm_list[8].x < lm_list[6].x
                and lm_list[12].x > lm_list[10].x
                and lm_list[16].x > lm_list[14].x
                and lm_list[20].x > lm_list[18].x
                and lm_list[5].x < lm_list[0].x
            ):
                cshow = "Move Left"
            # Right
            elif (
                lm_list[4].y < lm_list[2].y
                and lm_list[8].x > lm_list[6].x
                and lm_list[12].x < lm_list[10].x
                and lm_list[16].x < lm_list[14].x
                and lm_list[20].x < lm_list[18].x
            ):
                cshow = "Move Right"
            if all(finger_fold_status):
                # like
                if (
                    lm_list[thumb_tip].y
                    < lm_list[thumb_tip - 1].y
                    < lm_list[thumb_tip - 2].y
                    and lm_list[0].x < lm_list[3].y
                ):
                    cshow = "I Like it"
                # Dislike
                elif (
                    lm_list[thumb_tip].y
                    > lm_list[thumb_tip - 1].y
                    > lm_list[thumb_tip - 2].y
                    and lm_list[0].x < lm_list[3].y
                ):
                    cshow = "I dont like it."

            mpDraw.draw_landmarks(rgb, hand, mpHands.HAND_CONNECTIONS)
        cv2.putText(
            rgb, f"{cshow}", (10, 50), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0, 255, 255), 2
        )

    image = Image.fromarray(rgb)

    # Encode the byte stream to Base64
    image_base64 = numpyTobase64(image)


    # finalImage = ImageTk.PhotoImage(image)
    # label1.configure(image=finalImage)
    # label1.image = finalImage

    # save_path = filedialog.asksaveasfilename(
    #     defaultextension=".png",
    #     filetypes=[
    #         ("PNG files", "*.png"),
    #         ("JPEG files", "*.jpg"),
    #         ("All files", "*.*"),
    #     ],
    #     title="Save Processed Image",
    # )
    # if save_path:
    #     image.save(save_path)

    # # win.after(1, live)
    # crr=Label(win,text='Current Status :',font=('Helvetica',18,'bold'),bd=5,bg='gray',width=15,fg='#232224',relief=GROOVE )
    # status = Label(win,textvariable=upCount,font=('Helvetica',18,'bold'),bd=5,bg='gray',width=50,fg='#232224',relief=GROOVE )

    # status.place(x=400,y=700)
    # crr.place(x=120,y=700)

    return [image_base64, cshow]


@app.route("/processImage", methods=["POST"])
def process_image_route():
    """
    Process the image
    """
    image_id = request.json.get("image_id")
    if image_id:
        # find the image data based on given id
        image_data = db.images.find_one({"_id": ObjectId(image_id)})["image"]
        [output, label] = process_image(image_data)
        # update db with the generated label
        result = db.images.update_one(
            {"_id": ObjectId(image_id)},
            {"$set": {"output": output, "translation": label}},
        )
        
        return jsonify({"output": output, "translation": label}), 200
    return jsonify({"error": "Invalid request, image_id is required"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)


# label1 = Label(win, width=w, height=h, bg="#FFFFF7")
# label1.place(x=40, y=200)


# Button(win, text='Upload Image', padx=95, bg='#199ef3', fg='white', relief=RAISED, width=1, bd=5,
#        font=('Helvetica', 12, 'bold'), command=process_image).place(x=width - 250, y=400)
# Button(win, text='Exit', padx=95, bg='#199ef3', fg='white', relief=RAISED, width=1, bd=5,
#        font=('Helvetica', 12, 'bold'), command=win.destroy).place(x=width - 250, y=500)

# win.mainloop()
