import base64

with open("0.jpg", "rb") as imageFile:
    str = base64.b64encode(imageFile.read())
    print(str)

fh = open("6.png", "wb")
fh.write(base64.b64decode(str))
fh.close()