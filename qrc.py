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
        img[100:1100,100:120]=255
        img[100:1100,1080:1100] = 255
        img[1080:1100,100:1100]=255
        img[100:120,100:1100]=255


        im = Image.fromarray(img)
        im.save(str(i) + ".png")

    # ff = FFmpeg(inputs={'': '-f image2 -r ' + str(fra) + ' -i %d.png'}, outputs={out_path: '-vcodec mpeg4'})
    # print(ff.cmd)
    # ff.run()
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

def find(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # ret, binary = cv2.threshold(gray, 170, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(gray, 100, 150)
    contour_info = []
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    largest_area = 0
    for i in range(len(contours)):
        area = cv2.contourArea(contours[i])
        if area > largest_area:
            largest_area = area
            largest_coutour_index = i
    x, y, w, h = cv2.boundingRect(contours[largest_coutour_index])
    c=sorted(contours,key=cv2.contourArea, reverse=True)[1]
    rect = cv2.minAreaRect(c)  # 获取包围盒（中心点，宽高，旋转角度）
    box = np.int0(cv2.boxPoints(rect))
    draw_img = cv2.drawContours(img.copy(), [box], -1, (0, 0, 255), 3)
    pixel = int(h/50)
    pix=int(w/50)

    new = img[y + 2 + pixel:y + h - 2 - pixel, x + 2 + pix:x + w - pix - 2]
    # cv2.imshow('new', new)
    # cv2.waitKey(0)
    # print("box[0]:", box[0])
    # print("box[1]:", box[1])
    # print("box[2]:", box[2])
    # print("box[3]:", box[3])
    return box, draw_img

def Perspective_transform(box, original_img):
    x_aver=int(box[0][0]+box[1][0]+box[1][0]+box[3][0])/4
    #[box[1], box[2], box[0], box[3]]
    pts1=np.float32([[box[1][0],box[1][1]], box[2], box[0], box[3]])
    pts2 = np.float32([[0, 0], [300, 0], [0, 300], [300, 300]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(original_img, M, (300, 300))
    dst=dst[6:294,6:294]
    return dst

def cut(imgpath):
    ori_img = cv2.imread(imgpath)
    img = reshape_image(ori_img)
    box, draw_img = find(img)
    result = Perspective_transform(box, img)
    cv2.imwrite('result.png', result)


def decoder(video_path, bin_path, graph_num):
    ff = FFmpeg(inputs={video_path: None},
                outputs={'': '%d.png'})
    print(ff.cmd)
    ff.run()

    for i in range(1, graph_num + 1):
        image_dir = str(i) + ".png"
        #在这里加剪裁
        cut(img_dir)
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
