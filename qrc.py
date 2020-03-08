import qrcode
from PIL import Image
import cv2 as cv
import os
import pyzbar.pyzbar as pyzbar
#编码
# f=open('in.taxt')
# st=f.read()
# for i in range(1,len(st)//8):
#     data=st[i:i+8]
#     st=st[i+8:]
#     img = qrcode.make(data=data)
#     img.save(str(i)+'.jpg')
# imgg=Image.open('1.jpg')
# print(img.size)
# fps = 4 #视频每秒24帧
# size = (290, 290) #需要转为视频的图片的尺寸
# #可以使用cv2.resize()进行修改
# video = cv.VideoWriter("VideoTest1.avi", cv.VideoWriter_fourcc('I', '4', '2', '0'), fps, size)
# #视频保存在当前目录下
# for i in range(1,11):
#         img = cv.imread(str(i)+'.jpg')
#         video.write(img)
# video.release()
# cv.destroyAllWindows()


def encoder(video_path, txt_path):
    f = open(txt_path, 'rb')
    st = f.read()
    for i in range(1,len(st)//8):
       data=st[i:i+8]
       st=st[i+8:]
       img = qrcode.make(data=data)
       img.save(str(i)+'.jpg')
    imgg=Image.open('1.jpg', 'rb')
    print(img.size)
    fps = 4 #视频每秒24帧
    size = (290, 290) #需要转为视频的图片的尺寸
    #可以使用cv2.resize()进行修改
    video = cv.VideoWriter(video_path, cv.VideoWriter_fourcc('I', '4', '2', '0'), fps, size)
    #视频保存在当前目录下
    for i in range(1,11):
        img = cv.imread(str(i)+'.jpg')
        video.write(img)
    video.release()
    cv.destroyAllWindows()

#解码

cap = cv.VideoCapture('1.mp4')
fps = 1
size = (290,290)
ret, frame = cap.read()
li=''
while ret:
    decoded= pyzbar.decode(frame)
    for obj in decoded:
        print(obj.data)
        da=str(obj.data)
        da=da[2:10]
        print(da)
        li=li+da
        print(da)

        #cv.putText(frame, str(obj.data), (50, 50), font, 2,
                    #(255, 0, 0), 3)
    ret,frame=cap.read()
print(li)
with open('out.txt', 'w',encoding='utf-8') as f:
    f.write(li)
f.close()