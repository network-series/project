import numpy as np
import cv2
from ffmpy3 import FFmpeg
from PIL import Image
import datatobin as db

def encoder(bin_path,out_path,time_lim,width,highth):
    fra = 5
    pixel_size=20
    bin_in=db.dec2bin(bin_path)
    x=len(bin_in)
    row_num=int(highth/pixel_size)
    col_num=int(width/pixel_size/8)
    y=int(x//(row_num*col_num))#生成的图片数
    if (y>time_lim*fra):
        y=time_lim*fra
    for i in range(y):
        m=i*row_num*col_num
        n=(i+1)*row_num*col_num
        bin_slice=bin_in[m:n]
        img=np.zeros((highth,width),dtype=np.uint8)
        for j in range(row_num):
            img[j*pixel_size:(j+1)*pixel_size,0:width]=db.made_row(bin_slice[j*col_num:(j+1)*col_num],pixel_size,width)
        im = Image.fromarray(img)
        im.save(str(i)+".png")
        
        
    ff = FFmpeg(inputs={'': '-f image2 -r '+str(fra)+' -i %d.png'},outputs={out_path: '-vcodec mpeg4'})
    print(ff.cmd)
    ff.run()
    return y
def decoder(video_path,bin_path,graph_num):
    ff = FFmpeg(inputs={video_path: None},
            outputs={'': '%d.png'})
    print(ff.cmd)
    ff.run()
    
    for i in range(1,graph_num+1):
        image_dir = str(i)+".png"
        a=np.zeros((48,8),dtype=np.uint8)
        x=Image.open(image_dir).convert("L")
        data=np.array(x)
        for i in range(48):
            for j in range(8):
                a[i][j]= db.arr2byte(data[i*20:(1+i)*20,j*160:(j+1)*160])

        with open(bin_path,'ab') as f:
            f.write(a)
        
#encoder("i.bin","out.mp4",20,1280,960)
decoder("out.mp4","output.bin",40)

#img2 = np.fromfile("i.bin",dtype=np.uint8)
#print(img2)
#img=img2[0:480000]
#img=np.reshape(img,(400,400,3))
#print(img)
#im = Image.fromarray(img)
#im.save("0.bmp")

#a = cv2.imread("0.jpg")
#print(a)

#x=Image.open("0.bmp")
#data = np.array(x)
#print(data)

#data = np.fromfile("i.bin",np.uint8).reshape(400,400,3)
#print(data)
#cv2.imshow("a",data)
#cv2.waitKey(0)

#img =  np.array([[2,2],[2,2]])
#im=Image.fromarray(img)
#im.save("0.png")

#x=Image.open("0.png")
#data=np.array(x)
#print(data)

#a=np.zeros((960,1280),dtype=np.uint8)
#a[10:20,10:20]=255
#im = Image.fromarray(a)
#im.save("0.png")

#x=Image.open("16.png").convert("L")
#data = np.array(x)
#print(data[160][284])
#img2 = np.fromfile("b.bin",dtype=np.uint8)

#data=np.array([[55,55],[56,56]])
#with open("1.bin",'ab') as f:
#            f.write(data)
#x=Image.open("1.png").convert("L")
#data=np.array(x)
#print(data)