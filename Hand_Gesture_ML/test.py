import cv2
import numpy as np
import math
import time
import tensorflow
from cvzone.ClassificationModule import Classifier

from cvzone.HandTrackingModule import HandDetector
cap=cv2.VideoCapture(0)
detector =HandDetector(maxHands=2)
offset=20
imgsize=int(300)
classifier=Classifier("Model/Keras_model.h5","Model/labels.txt")
labels=["A","B","C"]
folder="data/C"
counter=0
while True:
    success,img=cap.read()
    hands,img=detector.findHands(img)
    imgotp=img.copy()
    if hands:
        
        hand=hands[0]
        x,y,w,h=hand['bbox']
        # a selfmade image
        imgwhite=np.ones((imgsize,imgsize,3),np.uint8)*255#0 to 255 coloured image 
        imgcrop=img[y-offset:y+h+offset,x-offset:x+w+offset]
#trafer cropimage to image white like matlab practical
        imgcropshape=imgcrop.shape
        #height.width,channel image apppreas on top of white image going beyond size gives us an error
        #imgwhite[0:imgcropshape[0],0:imgcropshape[1]]=imgcrop

        aspectratio=h/w # if value greater than 1 height is more else width

        if aspectratio>1:
             k=imgsize/h
             wcal=int(math.ceil(k*w))
             imgresize=cv2.resize(imgcrop,(wcal,imgsize))
             imgresizeshape=imgresize.shape
             wgap=int(math.ceil(imgsize-wcal)/2)
             imgwhite[:,wgap:wcal+wgap]=imgresize
             prediction,index=classifier.getPrediction(imgwhite,draw=False) #gives prediction and index
             print(prediction,index)
        else:
            
             k=imgsize/w
             hcal=int(math.ceil(k*h))
             imgresize=cv2.resize(imgcrop,(imgsize,hcal))
             imgresizeshape=imgresize.shape
             hgap=int(math.ceil(imgsize-hcal)/2)
             imgwhite[hgap:hcal+hgap,:]=imgresize
             prediction,index=classifier.getPrediction(imgwhite,draw=False) #gives prediction and index
             print(prediction,index)
        cv2.rectangle(imgotp, (x - offset, y - offset-50),
                      (x - offset+90, y - offset-50+50), (255, 0, 255), cv2.FILLED)
        cv2.putText(imgotp, labels[index], (x, y -26), cv2.FONT_HERSHEY_COMPLEX, 1.7, (255, 255, 255), 2)
        cv2.rectangle(imgotp, (x-offset, y-offset),
                      (x + w+offset, y + h+offset), (255, 0, 255), 4)
        cv2.imshow("ImageCrop",imgcrop)
        cv2.imshow("ImageWhite",imgwhite)
    cv2.imshow("Image",imgotp)
    key=cv2.waitKey(1)
    
#cropping the image try not to reach out use try catch condition keep hand in between problem is rectangle ,square?? counter probelm craete animage by ourselves imagewhite    
