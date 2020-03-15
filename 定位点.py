import numpy as np
import cv2
from ffmpy3 import FFmpeg
from PIL import Image
import copy
# 将每一个二进制都填补成8bit
def padstring(s):
    s_len = len(s)
    return (10 - s_len) * "0" + s[2:]

# 每一个十进制进来编码成对应二进制形成一个总列表
def dec2bin(bin_str):
    img2 = np.fromfile(bin_str, dtype=np.uint8)
    x = img2.size
    sum_list = list()
    for i in range(x):
        sum_list.append(padstring(bin(img2[i])))
    return sum_list

def made_row(s, r_len, c_len):
    a = np.zeros((r_len, c_len), dtype=np.uint8)
    strg = ""
    for j in range(len(s)):
        strg = strg + s[j]
    for i in range(8 * len(s)):
        if strg[i] == "0":
            a[0:20, 20 * i:20 * (i + 1)] = 0
        else:
            a[0:20, 20 * i:20 * (i + 1)] = 255
    return a


def arr2byte(s,v_pixel_size,h_pixel_size):
    strg = ""
    for i in range(8):
        if s[15,20*i+15] < 128:
            strg = strg + "0"
        else:
            strg = strg + "1"
    return int(strg, 2)

def draw_detection_pattern():
    a = np.zeros((140, 140), dtype=np.uint8)
    a[0:140,0:140]=0
    a[20:120,20:120]=255
    a[40:100,40:100]=0
    return a


def encoder(bin_path, out_path, time_lim, width, highth):
    fra = 10
    pixel_size = 20
    bin_in = dec2bin(bin_path)
    x = len(bin_in)
    row_num = int(highth / pixel_size)
    col_num = int(width / pixel_size / 8)
    y = int(x // (row_num * col_num))  # 生成的图片数
    if (y > time_lim * fra):
        y = time_lim * fra
    for i in range(y):
        m = i * row_num * col_num
        n = (i + 1) * row_num * col_num
        bin_slice = bin_in[m:n]
        extra=7*pixel_size
        img = np.zeros((highth+10*pixel_size, width+10*pixel_size), dtype=np.uint8)

        for j in range(row_num):

            img[j* pixel_size:(j + 1) * pixel_size, 0:width] = made_row(bin_slice[j * col_num:(j + 1) * col_num],
                                                                            pixel_size, width)

        
        img[highth:highth+8*pixel_size,0:width+8*pixel_size]=255
        img[0:highth,width:width+8*pixel_size] = 255
        img[0:7*pixel_size,width+pixel_size:width+8*pixel_size]=draw_detection_pattern()
        img[highth+pixel_size:highth+8*pixel_size,0:7*pixel_size]=draw_detection_pattern()
        img[highth+pixel_size:highth+8*pixel_size,width+pixel_size:width+8*pixel_size]=draw_detection_pattern()

        img[20:highth+9*pixel_size,20:width+9*pixel_size]=img[0:highth+8*pixel_size,0:width+8*pixel_size]
        img[0:20,0:width+9*pixel_size]=255
        img[0:highth+9*pixel_size,0:20]=255
        img[0:highth+10*pixel_size,width+9*pixel_size:width+10*pixel_size]=255
        img[highth+9*pixel_size:highth+10*pixel_size,0:width+10*pixel_size]=255

        im = Image.fromarray(img)
        im.save(str(i) + ".png")

    ff = FFmpeg(inputs={'': '-f image2 -r ' + str(fra) + ' -i %d.png'}, outputs={out_path: '-vcodec mpeg4'})
    print(ff.cmd)
    ff.run()
    return y
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
def detecte(image):
    '''提取所有轮廓'''
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)#灰度图
    _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours, hierarchy

def compute_1(contours, i, j):
    '''最外面的轮廓和子轮廓的比例'''
    area1 = cv2.contourArea(contours[i])
    area2 = cv2.contourArea(contours[j])
    if area2 == 0:
        return False
    ratio = area1 * 1.0 / area2
    if abs(ratio - 49.0 / 25):
        return True
    return False
def compute_2(contours, i, j):
    '''子轮廓和子子轮廓的比例'''
    area1 = cv2.contourArea(contours[i])
    area2 = cv2.contourArea(contours[j])
    if area2 == 0:
        return False
    ratio = area1 * 1.0 / area2
    if abs(ratio - 25.0 / 9):
        return True
    return False
def compute_center(contours, i):
    '''计算轮廓中心点'''
    M = cv2.moments(contours[i])
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    return cx, cy
def detect_contours(vec):
    '''判断这个轮廓和它的子轮廓以及子子轮廓的中心的间距是否足够小'''
    distance_1 = np.sqrt((vec[0] - vec[2]) ** 2 + (vec[1] - vec[3]) ** 2)
    distance_2 = np.sqrt((vec[0] - vec[4]) ** 2 + (vec[1] - vec[5]) ** 2)
    distance_3 = np.sqrt((vec[2] - vec[4]) ** 2 + (vec[3] - vec[5]) ** 2)
    if sum((distance_1, distance_2, distance_3)) / 3 < 3:
        return True
    return False
def juge_angle(rec):
    '''判断寻找是否有三个点可以围成等腰直角三角形'''
    if len(rec) < 3:
        return -1, -1, -1
    for i in range(len(rec)):
        for j in range(i + 1, len(rec)):
            for k in range(j + 1, len(rec)):
                distance_1 = np.sqrt((rec[i][0] - rec[j][0]) ** 2 + (rec[i][1] - rec[j][1]) ** 2)
                distance_2 = np.sqrt((rec[i][0] - rec[k][0]) ** 2 + (rec[i][1] - rec[k][1]) ** 2)
                distance_3 = np.sqrt((rec[j][0] - rec[k][0]) ** 2 + (rec[j][1] - rec[k][1]) ** 2)
                if abs(distance_1 - distance_2) < 5:
                    if abs(np.sqrt(np.square(distance_1) + np.square(distance_2)) - distance_3) < 5:
                        return i, j, k
                elif abs(distance_1 - distance_3) < 5:
                    if abs(np.sqrt(np.square(distance_1) + np.square(distance_3)) - distance_2) < 5:
                        return i, j, k
                elif abs(distance_2 - distance_3) < 5:
                    if abs(np.sqrt(np.square(distance_2) + np.square(distance_3)) - distance_1) < 5:
                        return i, j, k
    return -1, -1, -1


def find(path,image, contours, hierachy, root=0):
     '''找到符合要求的轮廓'''
     rec=[]
     for i in range(len(hierachy)):
        child = hierachy[i][2]
        child_child = hierachy[child][2]
        if child != -1 and hierachy[child][2] != -1:
            if compute_1(contours, i, child) and compute_2(contours, child, child_child):
                cx1, cy1 = compute_center(contours, i)
                cx2, cy2 = compute_center(contours, child)
                cx3, cy3 = compute_center(contours, child_child)
                if detect_contours([cx1, cy1, cx2, cy2, cx3, cy3]):
                    rec.append([cx1, cy1, cx2, cy2, cx3, cy3, i, child, child_child])
     '''计算得到所有在比例上符合要求的轮廓中心点'''
     i, j, k = juge_angle(rec)
     if i == -1 or j == -1 or k == -1:
        return
     ts = np.concatenate((contours[rec[i][6]], contours[rec[j][6]], contours[rec[k][6]]))
     rect = cv2.minAreaRect(ts)
     box = cv2.boxPoints(rect)
     box = np.int0(box)
     result = copy.deepcopy(image)
    # cv2.drawContours(result, [box], 0, (0, 0, 255), 2)
    # cv2.drawContours(image, contours, rec[i][6], (255, 0, 0), 2)
    # cv2.drawContours(image, contours, rec[j][6], (255, 0, 0), 2)
    # cv2.drawContours(image, contours, rec[k][6], (255, 0, 0), 2)
     #print(ts)
     #print(box)
     left=box[0][0]
     up=box[0][1]
     right=box[2][0]
     down=box[2][1]
     up=int(down+(up-down)*960/1120)
     right=int(left+(right-left)*960/1120)
     #print(down,up,left,right)
     result=result[down:up,left:right]
     #cv2.imshow('img', result)
     cv2.imwrite(path,result)
     #cv2.waitKey(0)

     return


def cut(path):
    image = cv2.imread(path)
    image = reshape_image(image)
    contours, hierarchy = detecte(image)
    find(path,image, contours, np.squeeze(hierarchy))

def decoder(video_path, bin_path,highth,width,row_num,col_num, graph_num):
#    ff = FFmpeg(inputs={video_path: None},
#                outputs={'': '%d.png'})
 #   print(ff.cmd)
 #   ff.run()

#    k=162
#    while (1==1):
#        image_dire=str(k)+".png"
#        if cut(image_dire)==0:
##            k=k+1
 #       else:
 #           a = np.zeros((col_num, row_num), dtype=np.uint8)
 #           image = cv2.imread(image_dir,0)
 #           v_pixel_size=image.shape[0]//col_num
 #           h_pixel_size=image.shape[1]//(row_num*8)
 #           re_image=cv2.resize(image, (highth,width))
        #
        # imgpath=''
        # cut(imgpath)

   #         for i in range(col_num):
 ##               for j in range(row_num):
     #               a[i][j] = arr2byte(re_image[i*20:(i+1)*20,j*160:(j+1)*160],20,20)
            #print(a)
   #         with open(bin_path, 'ab') as f:
   #             f.write(a)
   #         break

    for i in range(0,graph_num):
        image_dir = str(1+i*6) + ".png"
        cut(image_dir)
        a = np.zeros((col_num, row_num), dtype=np.uint8)
        image = cv2.imread(image_dir,0)
        v_pixel_size=image.shape[0]//col_num
        h_pixel_size=image.shape[1]//(row_num*8)
        re_image=cv2.resize(image, (highth,width))
        #
        # imgpath=''
        # cut(imgpath)

        for i in range(col_num):
            for j in range(row_num):
                a[i][j] = arr2byte(re_image[i*20:(i+1)*20,j*160:(j+1)*160],20,20)
        print(a)
        with open(bin_path, 'ab') as f:
            f.write(a)

#encoder("i.bin","out.mp4",20,960,960)
decoder("out.mp4","output.bin",960,960,6,48,40)
#cut("b.png")

#image = cv2.imread("0.png",0)
#print(image.shape[0])
#out=cv2.resize(image, (192, 192))
#print(out)
#x=Image.open("7.png").convert("L")
#data = np.array(x)
#print(data[:,8])
#for i in range(205):
 #   print(data[1][i])
#image_dir =  "a.png"
#image = cv2.imread(image_dir,0)
#re_image=cv2.resize(image, (960,960))
        #
        # imgpath=''
        # cut(imgpath)

#for i in range(48):
 #   for j in range(6):
 #       a[i][j] = arr2byte(re_image[i*20:(i+1)*20,j*160:(j+1)*160],20,20)
#print(a)

#ff = FFmpeg(inputs={"out1.mp4": None},
    #            outputs={'': '%d.png'})
#print(ff.cmd)
#ff.run()