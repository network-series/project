import cv2
import numpy as np
def reshape_image(image):
    '''归一化图片尺寸：短边400，长边不超过800，短边400，长边超过800以长边800为主'''
    width, height = image.shape[1], image.shape[0]
    min_len = width
    scale = width * 1.0 / 400
    new_width = 400
    new_height = int(height / scale)
    if new_height > 800:
        new_height = 800
        scale = height * 1.0 / 800
        new_width = int(width / scale)
    out = cv2.resize(image, (new_width, new_height))
    return out

def cut(imgpath):
    img = cv2.imread(imgpath)
    img = reshape_image(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # ret, binary = cv2.threshold(gray, 170, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(gray, 50, 150)
    cv2.imshow('11', edges)
    cv2.waitKey(0)
    contour_info = []
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    largest_area = 0
    for i in range(len(contours)):

        area = cv2.contourArea(contours[i])
        if area > largest_area:
            largest_area = area
            largest_coutour_index = i

    print(contours[largest_coutour_index])
    cv2.imshow('1', img)
    cv2.waitKey(0)
    x, y, w, h = cv2.boundingRect(contours[largest_coutour_index])
    pixel = 0
    pix = 0
    new = img[y + 2 + pixel:y + h - 2 - pixel, x + 2 + pix:x + w - pix - 2]
    cv2.imshow('new', new)
    cv2.waitKey(0)
cut('12.png')
