from PIL import Image, ImageDraw, ImageFont
import cv2 as cv
import numpy as np
import os
import base64
def black(i):
    img = np.zeros([400, 400, 3], np.uint8)
    cv.imwrite(str(i)+'.jpg',img)
def white(i):
    img2 = np.zeros([400, 400, 3], np.uint8) + 255
    cv.imwrite(str(i) + '.jpg', img2)
def green():
    img_green = np.zeros([400, 400, 3], np.uint8)
    img_green[:, :, 0] = np.zeros([400, 400]) + 255
    cv.imshow("iamge_green", img_green)
def blue():
    img_blue = np.zeros([400, 400, 3], np.uint8)
    img_blue[:, :, 1] = np.zeros([400, 400]) + 255
    cv.imshow("iamge_blue", img_blue)
def red():
    img_red = np.zeros([400, 400, 3], np.uint8)
    img_red[:, :, 2] = np.zeros([400, 400])+ 255
    cv.imshow("iamge_red", img_red)
    cv.waitKey(0)


f=open('111.txt','rb')
st=f.read()
st64=base64.b64encode(st)
print(len(st64))
print(st64)
string=['00000000']*len(st64)
for i in range(1,len(st64)):
    string[i]= bin(st64[i])
    print(st64[i],string[i])
    string[i]=str(string[i])
    string[i]=string[i][2:9]
    print(string[i])
    for j in range(len(string[i])):
        if string[i][j]=='1':
            black(i*j)
            print("B")
        else:
            white(i*j)
            print("w")

path = 'F:/shanx/PROGRAMS/python/'
filelist = os.listdir(path)

fps = 4 #视频每秒24帧
size = (400, 400) #需要转为视频的图片的尺寸
#可以使用cv2.resize()进行修改

video = cv.VideoWriter("VideoTest1.avi", cv.VideoWriter_fourcc('I', '4', '2', '0'), fps, size)
#视频保存在当前目录下

for item in filelist:
    if item.endswith('.jpg'):
    #找到路径中所有后缀名为.png的文件，可以更换为.jpg或其它
        item = path + item
        img = cv.imread(item)
        video.write(img)

video.release()
cv.destroyAllWindows()