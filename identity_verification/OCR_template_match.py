from imutils import contours
import numpy as np
import argparse
import imutils 
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-i", r"C:\Users\oluwa\OneDrive\Desktop\credit_card_1.png", required=True, help="path to input image")
ap.add_argument("r", r"C:\Users\oluwa\Downloads\ocr-a-digits-regular (1).ttf", required=True, help="path to reference OCR-A image")
args = vars(ap.parse_args())
#now we map the first digit of a credit card number to the credit card type....all this in a dictionary
first_number = {
    "3": "American Express",
    "4": "Visa",
    "5": "Master Card",
    "6": "Discover Card"
    }
ref = cv2.imread(args[""])

