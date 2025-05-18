import sys, os
from secret_image_sharing.tkn import TKN
from secret_image_sharing.kn import KN
from PIL import Image

#from secret-image-sharing import kn
tkn = TKN()
kn = KN()
#img =  Image.open("test_1.png")
kn.encrypt( n=3, k=2, file_name=r"secret_image_sharing\asset\test_img.jpg")
kn.decrypt(shareno=[2, 3])
#tkn.encrypt(t = 2, k = 4, n = 6, file_name=r"secret_image_sharing\asset\test_img.jpg")
tkn.decrypt([1, 2], [4, 5])