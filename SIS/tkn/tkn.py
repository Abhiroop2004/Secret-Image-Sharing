# Code for Essential Secret Sharing Scheme using Shamir Secret Sharing on Color Image

import shamirc as sis
import secrets
from PIL import Image
from numpy import zeros,array,size,poly, matmul, shape, linalg, loadtxt, stack, concatenate

def multi_generate_share(secret : list[int], n : int, k : int) -> list[int]:
    no_secrets = len(secret)
    equation=[secrets.randbelow(256) for i in range(k-no_secrets)]
    for s in secret:
        equation.append(s)
    shares=[]
    for i in range(1,n+1):
        share = sis.polynomial_GF(equation, i, k)
        shares.append(share)
    return shares

def multi_encrypt(n : int, k : int, multi_img : list) -> list:
    s = shape(multi_img)
    w, h = s[2], s[1]
    #arr = array([[arr[x, y] for y in range(h)] for x in range(w)])
    shares = zeros([n, h, w, 3], dtype=int) 
    print(s)
    for x in range(w): #generate the shares
        for y in range(h):
            secretr, secretg, secretb = multi_img[:, y, x,0], multi_img[:, y, x, 1], multi_img[:, y, x, 2]
            #secretr, secretg, secretb=multi_img[:][x][y]
            sharer = multi_generate_share(secretr, n, k)
            shareg = multi_generate_share(secretg, n, k)
            shareb = multi_generate_share(secretb, n, k)
            for z in range(n):
                shares[z][y][x][0] = sharer[z]
                shares[z][y][x][1] = shareg[z]
                shares[z][y][x][2] = shareb[z]
    #print(shares)
    return shares

def multi_recon(shares : list, n : int, k : int, w : int, h : int, shareno : list[int]) -> Image:
    secret = zeros([h, w], dtype=int)
    
def multi_decrypt(n : int, shareno : list[int]) -> Image:
    shares_red= [[0] for _ in range(n)]
    shares_green= [[0] for _ in range(n)]
    shares_blue= [[0] for _ in range(n)]
    for i in range(n):
        img=Image.open(r"Shares\share"+str(shareno[i])+".png") #opens ith share
        w,h=img.size 
        red, green, blue = img.split()
        arr_r, arr_g, arr_b=red.load(), green.load(), blue.load()
        shares_red [i] = array([[arr_r[x, y] for y in range(h)] for x in range(w)])
        shares_green[i] = array([[arr_g[x, y] for y in range(h)] for x in range(w)])
        shares_blue[i] = array([[arr_b[x, y] for y in range(h)] for x in range(w)])
    secret = multi_recon(array(shares_red), n, k-t, w, h, shareno)
    
def tkn_encrypt(t : int, k : int, n : int, img : Image):
    kk_shares = sis.encrypt(n = k, k = k, img = img)
    print("KK: ", shape(kk_shares))
    kn_multi_shares = multi_encrypt(n-t, k-t, kk_shares[t:])
    shares = concatenate((kk_shares[:t], kn_multi_shares), axis=0)
    print(shape(shares))
    print(shape(kk_shares), shape(kn_multi_shares))
    for i in range(n): #saving images
        img=Image.fromarray(shares[i].astype('uint8'))
        img.save(r"Shares\share"+str(i+1)+".png")

def tkn_decrypt(t : int, k : int, n : int, path : str) -> Image:
    shares=[]
    for i in range(n):
        shares.append(Image.open(path+str(i+1)+".png"))
    kk_shares = multi_decrypt(n-t,[i for i in range(t+1,n+1)]) 
    print("KK: ", shape(kk_shares))
    kn_multi_shares = [multi_decrypt(img) for img in shares[t:]]
    shares = concatenate((kk_shares, kn_multi_shares), axis=0)
    print(shape(shares))
    print(shape(kk_shares), shape(kn_multi_shares))
    secret = sis.decrypt(shares)
    return secret

file_name="face.jpg"
t=int(input("Enter no. of essential shares(t): "))
n= int(input("Enter no of shares(n): "))
k=int(input("Enter minimum shares to reveal secret(k): "))
c=int(input("Enter 1 for encryption and 0 for decryption: "))
if (c==1):
    img=Image.open(file_name)
    tkn_encrypt(t,n,k,img)
else:
    path = "Shares\share"
    secret=tkn_decrypt(t,n,k, path)
    print("Secret: ", secret)