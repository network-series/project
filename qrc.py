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

def arr2byte(s):
    strg = ""
    for i in range(8):
        if s[10, i * 20 + 10] < 128:
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
    fra = 5
    pixel_size = 20
    bin_in = dec2bin(bin_path)
    x = len(bin_in)
    print(x)
    row_num = int(highth / pixel_size)
    col_num = int(width / pixel_size / 8)
    print(row_num)
    print(col_num)
    y = int(x // (row_num * col_num))  # 生成的图片数
    print(y)
    if (y > time_lim * fra):
        y = time_lim * fra
    for i in range(y):
        m = i * row_num * col_num
        n = (i + 1) * row_num * col_num
        bin_slice = bin_in[m:n]
        extra=7*pixel_size
        img = np.zeros((highth+6*pixel_size, width+6*pixel_size), dtype=np.uint8)

        for j in range(row_num):

            img[j* pixel_size+60:(j + 1) * pixel_size+60, 60:width+60] = made_row(bin_slice[j * col_num:(j + 1) * col_num],
                                                                            pixel_size, width)

#         left=(row_num+1)*pixel_size
#         print(left)
#         right=(row_num+8)*pixel_size
#         print(right)
#         img[0:right,left-pixel_size:right]=255
#         img[left-pixel_size:right,0:right] = 255
#         img[0:7*pixel_size,left:right]=draw_detection_pattern()
#         img[left:right,0:7*pixel_size]=draw_detection_pattern()
#         img[left:right,left:right]=draw_detection_pattern()
        img[50:1030,50:55]=255
        img[50:1030,1025:1030] = 255
        img[1025:1030,50:1030]=255
        img[50:55,50:1030]=255


        im = Image.fromarray(img)
        im.save(str(i) + ".png")

    # ff = FFmpeg(inputs={'': '-f image2 -r ' + str(fra) + ' -i %d.png'}, outputs={out_path: '-vcodec mpeg4'})
    # print(ff.cmd)
    # ff.run()
    return y

def cut(img):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    draw_img0 = cv2.drawContours(img.copy(), contours, 0, (0, 255, 255), 1)
    x, y, w, h = cv2.boundingRect(contours[0])
    pixel = int((h - 2) * 1 / 50)
    pix = int((w - 2) * 1 / 50)
    print(pixel)
    print(pix)
    new = img[y + 2 :y + h - 2 , x + 2 :x + w  - 2]
    cv2.imshow('new', new)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return new
def threshold_demo(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  #把输入图像灰度化
    #直接阈值化是对输入的单通道矩阵逐像素进行阈值分割。
    ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_TRIANGLE)
    print("threshold value %s"%ret)
    cv2.namedWindow("binary0", cv2.WINDOW_NORMAL)
    cv2.imshow("binary0", binary)
    cv2.waitKey(0)
    return binary

#解码前先运行裁剪，以下三行
def cut(path)
    origin=cv2.imread(path)
    binary=threshold_demo(origin)
    processed_imge=cut(binary)
    return processed_image



def decoder(video_path, bin_path, graph_num):
    ff = FFmpeg(inputs={video_path: None},
                outputs={'': '%d.png'})
    print(ff.cmd)
    ff.run()

    for i in range(1, graph_num + 1):
        image_dir = str(i) + ".png"
        a = np.zeros((48, 8), dtype=np.uint8)
        x = Image.open(image_dir).convert("L")

        #
        # imgpath=''
        # cut(imgpath)


        data = np.array(x)
        for i in range(48):
            for j in range(8):
                a[i][j] = arr2byte(data[i * 20:(1 + i) * 20, j * 160:(j + 1) * 160])

        with open(bin_path, 'ab') as f:
            f.write(a)

encoder("in.txt","out.mp4",20,960,960)
# decoder("out.mp4","output.bin",40)
