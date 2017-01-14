import numpy as np
import sys
import matplotlib.pyplot as plt
import cv2
import time


# given a difference image,
# returns whether it suspects there is a human within the frame (a car also warrants our attention),
# valid within some distance when captured (has to be large enough)
def human_nearby(diff):
    diff = np.array(diff, dtype = 'u1')
    #diff = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)

    # threshold is % of the maximum value encountered in the picture
    cv2.threshold(diff, thresh= 0.1*np.max(diff), maxval=1.0, type=cv2.THRESH_BINARY, dst=diff)

    # fill in holes/ remove white noise (MORPH_OPENING is erosion then dilation)
    kernel = np.ones((5,5),np.uint8)
    diff = cv2.morphologyEx(diff, cv2.MORPH_OPEN, kernel)
    diff = cv2.dilate(diff, kernel, iterations = 5)

    # plt.imshow(diff, cmap = 'Greys')
    # plt.show()
    (cnts, _) = cv2.findContours(diff.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for contour in cnts:
        if cv2.contourArea(contour) >=  0.02*diff.size:
            return True

    return False

# returns a non-empty bounding boxes containing faces within the picture
def detect_faces(image):
    print "detecting faces... "
    image = np.array(image, dtype= 'u1')
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(image, 1.1, 5)


    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), 255, 0)
    cv2.imwrite("detected_faces.jpg", image)
    return faces

if __name__ == '__main__':

    pastPics = [None] * 10
    pastPics[0] = cv2.imread("frame2.jpg", 0)

    # test runs
    for i in range(14):
        #time.sleep(1)
        pastPics[0] = cv2.imread("frame2.jpg", 0)

        # save a string of past pictures
        for i in range(1, 10):
            pastPics[-i] = pastPics[-i-1]

        # take pic, store as current

        image1 = pastPics[0]
        image2 = pastPics[1]

        image3 = np.absolute(image1 - image2)
        image3 = image3 - np.average(image3)
        image3 = np.clip(image3, 0.0, 1.0)
        cv2.imwrite("diff_image.jpg", image3)

        # assuming that image 2 (most recent) contains the image of the person...
        # even if no faces are found, system will enter new state and may send alert signal if motion continues
        if human_nearby(image3):
            print "suspecting human presence..."
        detect_faces(image2)

    cv2.imshow("window", pastPics[8])
    time.sleep(100)
