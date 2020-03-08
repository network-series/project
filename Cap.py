from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import os


def Gen_Video(imagesPath, name_path, fps=10):
    # 包含图片的文件夹
    # imagesPath = os.path.abspath(imagesPath)
    # print(imagesPath)
    imagesList = os.listdir(imagesPath)
    imagesList.sort()
    if imagesList == []:
        print("The entered address has no content!")
    print(imagesPath  + imagesList[0])
    size = cv2.imread(imagesPath +  imagesList[0]).shape[:2]
    # size = cv2.imread('E:\上学\大二下\计算机网络\代码\MY\Picture\ 1.png').shape[:2]
    #size = (size[1], size[0])
    print(size)
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    video = cv2.VideoWriter(name_path, fourcc, fps, size)  # 调节视频大小帧率名字啥的
    frame = 0
    for imageName in imagesList:
        if imageName.endswith('.png'):
            frame = frame + 1

        # path = os.path.abspath(os.path.join(imagesPath, imageName))
            path = imagesPath + '/' + imageName
            img = cv2.imread(path)

            video.write(img)

            print("The %d frame has been added" % frame)
    video.release()
    return 0

def encoder(bin_path, out_path, time_lim, width, highth):
    fra = 5
    img2 = np.fromfile(bin_path, dtype=np.uint8)
    x = img2.size
    y = x // (width * highth) // 3
    if (y > time_lim * fra):
        y = time_lim * fra
    for i in range(y):
        m = i * width * highth * 3
        n = (i + 1) * width * highth * 3
        img = img2[m:n]
        img = np.reshape(img, (highth, width, 3))
        print(img)
        im = Image.fromarray(img).convert('RGB')  # 把每一个三维矩阵当作RGB三通道来处理成彩色图即RGB
        im.save(str(i) + ".png")

    Gen_Video('F:/shanx/PROGRAMS/python/rgb/','out.avi')
    return y

def decoder(video_path, bin_path):
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    #size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    ret, frame = cap.read()
    i = 0
    while ret:
        cv2.imwrite(str(i) + '.png', frame)
        cv2.waitKey(fps)
        i = i + 1
        ret, frame = cap.read()
    cap.release()
    cv2.destroyAllWindows()
    for i in range(0, i):
        image_dir = str(i) + ".png"
        x = Image.open(image_dir)  # 打开图片
        data = np.array(x)
        print(data)
        with open(bin_path, 'ab') as f:
            f.write(data)


result=encoder("in.bin","out.avi",20,100,100)

decoder("out.avi", "output.bin")