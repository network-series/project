import numpy as np
from PIL import Image

#将每一个二进制都填补成8bit
def padstring(s):
    s_len=len(s)
    return (10-s_len)*"0"+s[2:]
    
#每一个十进制进来编码成对应二进制形成一个总列表
def dec2bin(bin_str):
    img2 = np.fromfile(bin_str, dtype=np.uint8)
    x=img2.size
    sum_list=list()
    for i in range(x):
        sum_list.append(padstring(bin(img2[i])))
    return sum_list

def made_row(s,r_len,c_len):
    a=np.zeros((r_len,c_len),dtype=np.uint8)
    strg=""
    for j in range(len(s)):
        strg=strg+s[j]
    for i in range(8*len(s)):
        if strg[i]=="0":
            a[0:20,20*i:20*(i+1)]=0
        else:
            a[0:20,20*i:20*(i+1)]=255
    return a

def arr2byte(s):
    strg=""
    for i in range(8):
        if s[10,i*20+10]<128:
            strg=strg+"0"
        else:
            strg=strg+"1"
    return int(strg,2)






    




