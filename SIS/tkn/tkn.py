# Code for Essential Secret Sharing Scheme using Shamir Secret Sharing on Color Image

import shamirc as sis
import secrets, galois
from PIL import Image
from numpy import zeros,array,size,poly, matmul, shape, linalg, loadtxt, stack, concatenate, flip

order=2**8
GF = galois.GF(order, repr='int')

def multi_generate_share(secret : list[int], n : int, k : int) -> list[int]:
    no_secrets = len(secret)
    #equation=[secrets.randbelow(256) for i in range(k-no_secrets)]
    equation=[]
    #print("Equation: ", equation, "K: ", k)
    for s in secret:
        equation.append(s)
    #print("Equation: ", equation)
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
    #print("multi: ",s[0],s[1],s[2], s[3], s)
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

def multi_recon(shares : list, n : int, r : int, w : int, h : int, shareno : list[int]) -> list[list[int]]:
    #print("r/k = ",r)
    secret = zeros([h, w, r], dtype=int)
    A = GF([[sis.power(X, i) for i in range(r - 1, -1, -1)] for X in shareno])
    #print("Shape of A",shape(A))
    #print("Share no:",shareno)
    A_inv = linalg.inv(A)
    for x in range(w):
        for y in range(h):
            B = array(shares[:, x, y])
            X = sis.matrix_mul(A_inv, B)
            #print("Shape of X",shape(X))
            #print("X: ", X)
            for z in range(r):
                #secret[y][x][z] = X[-1-z]
                secret[y][x][z] = X[z]
    return secret

def multi_decrypt(n : int, k : int, shareno : list[int]) -> Image: #1st step for decryption
    l = len(shareno)
    shares_red= [[0] for _ in range(l)]
    shares_green= [[0] for _ in range(l)]
    shares_blue= [[0] for _ in range(l)]
    #print(shareno)
    for i in range(l):
        img=Image.open(r"Shares\share"+str(shareno[i])+".png") #opens non-essential shares
        w,h=img.size 
        red, green, blue = img.split()
        arr_r, arr_g, arr_b=red.load(), green.load(), blue.load()
        shares_red [i] = array([[arr_r[x, y] for y in range(h)] for x in range(w)])
        shares_green[i] = array([[arr_g[x, y] for y in range(h)] for x in range(w)])
        shares_blue[i] = array([[arr_b[x, y] for y in range(h)] for x in range(w)])
    print("n,k,w,h for muli recon",n,k,w,h)
    shareno = [x-t for x in shareno] #adjusting share numbers for t essential participants to start from 0

    #print("Multi Shareno: ", shareno)
    red = multi_recon(array(shares_red), n, k, w, h, shareno)
    green = multi_recon(array(shares_green), n, k, w, h, shareno)
    blue = multi_recon(array(shares_blue), n, k, w, h, shareno)
    #print("Red: ",red)
    secret = zeros([k, h, w, 3], dtype=int)
    for z in range(k):
        for x in range(w):
            for y in range(h):
                secret[z][y][x][0] = red[y][x][z]
                secret[z][y][x][1] = green[y][x][z]
                secret[z][y][x][2] = blue[y][x][z]
        #print("Secret: ", secret)
    #print("Multi-Shares : ",secret)
    return secret
    
def tkn_encrypt(t : int, k : int, n : int, img : Image):
    kk_shares = sis.encrypt(n = k, k = k, img = img)
    print("Multi Sharing Shares:",kk_shares[t:])
    print("KK: ", shape(kk_shares))
    kn_multi_shares = multi_encrypt(n-t, k-t, kk_shares[t:])
    print("Multi Shares before enc: ", kk_shares[t:],"\n")
    print("Essential Shares: ", kk_shares[:t],"\n")
    shares = concatenate((kk_shares[:t], kn_multi_shares), axis=0)
    #print(shape(kk_shares), shape(kn_multi_shares))
    for i in range(n): #saving images
        img=Image.fromarray(shares[i].astype('uint8'))
        img.save(r"Shares\share"+str(i+1)+".png")

def tkn_decrypt(t : int, k : int, n : int, e_shareno : list, shareno : list, path : str) -> Image:
    shares=[]
    #for i in shareno:
    #    shares.append(Image.open(path+str(i)+".png"))
    nonessential_shares = multi_decrypt(n-t, k-t, shareno) 
    print("Non-essential shares: ", nonessential_shares, "\n")
    essential_shares = [Image.open(path+str(i)+".png") for i in e_shareno]
    #print("All shares: ",array(essential_shares),"\n", nonessential_shares)
    #return
    #kn_multi_shares = [multi_decrypt(img, ) for img in shares[t:]]
    shares = concatenate((array(essential_shares), nonessential_shares), axis=0)
    print("Essential: ",array(essential_shares))
    #print("Shares: ", shares)
    kk_shareno = e_shareno + [i for i in range(e_shareno[-1]+1, k+1)]
    print(e_shareno, shareno, kk_shareno)
    #print("k ", k)
    secret = sis.reconstruct(shares, k, kk_shareno)
    return secret

file_name="face.jpg"
#file_name="test_1.png"
t=int(input("Enter no. of essential shares(t): "))
n= int(input("Enter no of shares(n): "))
k=int(input("Enter minimum shares to reveal secret(k): "))
c=int(input("Enter 1 for encryption and 0 for decryption: "))
if (c==1):
    img=Image.open(file_name)
    tkn_encrypt(t,k,n,img)
else:
    inp =int(input("Enter the number of shares:"))

    print("Enter the essential share numbers(1-n):")
    e_shareno= [0 for _ in range (t)]
    for i in range(t):
        e_shareno[i]=int(input())
    print(e_shareno)

    print("Enter the non-essential share numbers(1-n):")
    shareno= [0 for _ in range (inp-t)]
    for i in range(inp-t):
        shareno[i]=int(input())
    print(shareno)

    path = "Shares\share"
    secret = tkn_decrypt(t,k,n, e_shareno, shareno, path)
    img = Image.open(file_name)
    print(array(secret), array(img))
    if (array(img) == array(secret)).all: print("Secret is same as original image")
    else: print("Secret is not same as original image")