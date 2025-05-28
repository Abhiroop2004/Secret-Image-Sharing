# Code for Essential Secret Sharing Scheme using Shamir Secret Sharing on Color Image

#from kn import KN
#import kn
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import galois
from PIL import Image
from numpy import zeros,array,size,poly, matmul, shape, linalg, loadtxt, stack, concatenate, flip
from kn import KN
sis = KN()

class TKN:
    def __init__(self):
        order=2**8
        self.GF = galois.GF(order, repr='int')

    def multi_generate_share(self, secret : list[int], n : int, k : int) -> list[int]:
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

    def multi_encrypt(self, n : int, k : int, multi_img : list) -> list:
        s = shape(multi_img)
        w, h = s[2], s[1] 
        #arr = array([[arr[x, y] for y in range(h)] for x in range(w)])
        shares = zeros([n, h, w, 3], dtype=int) 
        #print("multi: ",s[0],s[1],s[2], s[3], s)
        for x in range(w): #generate the shares
            for y in range(h):
                secretr, secretg, secretb = multi_img[:, y, x,0], multi_img[:, y, x, 1], multi_img[:, y, x, 2]
                #secretr, secretg, secretb=multi_img[:][x][y]
                sharer = self.multi_generate_share(secretr, n, k)
                shareg = self.multi_generate_share(secretg, n, k)
                shareb = self.multi_generate_share(secretb, n, k)
                for z in range(n):
                    shares[z][y][x][0] = sharer[z]
                    shares[z][y][x][1] = shareg[z]
                    shares[z][y][x][2] = shareb[z]
        #print(shares)
        return shares

    def multi_recon(self, shares : list, r : int, w : int, h : int, shareno : list[int]) -> list[list[int]]:
        #print("r/k = ",r)
        secret = zeros([h, w, r], dtype=int)
        A = self.GF([[sis.power(X, i) for i in range(r - 1, -1, -1)] for X in shareno])
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

    def multi_decrypt(self, t: int, k : int, shareno : list[int], path : str) -> Image: #1st step for decryption
        l = len(shareno)
        shares_red= [[0] for _ in range(l)]
        shares_green= [[0] for _ in range(l)]
        shares_blue= [[0] for _ in range(l)]
        #print(shareno)
        for i in range(l):
            img=Image.open(path+str(shareno[i])+".png") #opens non-essential shares
            w,h=img.size 
            red, green, blue = img.split()
            arr_r, arr_g, arr_b=red.load(), green.load(), blue.load()
            shares_red [i] = array([[arr_r[x, y] for y in range(h)] for x in range(w)])
            shares_green[i] = array([[arr_g[x, y] for y in range(h)] for x in range(w)])
            shares_blue[i] = array([[arr_b[x, y] for y in range(h)] for x in range(w)])
        #print("n,k,w,h for muli recon",n,k,w,h)
        shareno = [x-t for x in shareno] #adjusting share numbers for t essential participants to start from 0

        #print("Multi Shareno: ", shareno)
        red = self.multi_recon(array(shares_red), k, w, h, shareno)
        green = self.multi_recon(array(shares_green), k, w, h, shareno)
        blue = self.multi_recon(array(shares_blue), k, w, h, shareno)
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
        
    def tkn_encrypt(self, t : int, k : int, n : int, file : str, dest : str):
        #img = Image.open(file_name)
        kk_shares = sis.encrypt(n = k, k = k, file_name = file, dest = dest, save = 0)
        #print("Multi Sharing Shares:",kk_shares[t:])
        #print("KK: ", shape(kk_shares))
        kn_multi_shares = self.multi_encrypt(n-t, k-t, kk_shares[t:])
        #print("Multi Shares before enc: ", kk_shares[t:],"\n")
        #print("Essential Shares: ", kk_shares[:t],"\n")
        shares = concatenate((kk_shares[:t], kn_multi_shares), axis=0)
        for i in range(n): # saving images
            img=Image.fromarray(shares[i].astype('uint8'))
            img.save(dest+r"\share"+str(i+1)+".png")

    def tkn_decrypt(self, t : int, k : int, e_shareno : list, shareno : list, path : str ) -> None:
        shares=[]
        #for i in shareno:
        #    shares.append(Image.open(path+str(i)+".png"))
        nonessential_shares = self.multi_decrypt(t, k-t, shareno, path) 
        #print("Non-essential shares: ", nonessential_shares, "\n")
        essential_shares = [Image.open(path+str(i)+".png") for i in e_shareno]
        #print("All shares: ",array(essential_shares),"\n", nonessential_shares)
        #return
        #kn_multi_shares = [multi_decrypt(img, ) for img in shares[t:]]
        shares = concatenate((array(essential_shares), nonessential_shares), axis=0)
        #print("Essential: ",array(essential_shares))
        #print("Shares: ", shares)
        kk_shareno = e_shareno + [i for i in range(e_shareno[-1]+1, k+1)]
        #print(e_shareno, shareno, kk_shareno)
        #print("k ", k)
        secret = sis.reconstruct(shares, k, kk_shareno)
        secret.save("secret.png")
        #return secret

    def encrypt(self, t : int, k : int, n :int, file_name : str, dest : str = "Shares") -> None:
        #img=Image.open(file_path)
        return self.tkn_encrypt(t , k, n , file_name, dest)

    def decrypt(self, e_shareno : list[int], shareno : list[int], share_path : str = "Shares"):
        t = len(e_shareno)
        k = len(shareno) + t
        self.tkn_decrypt(t = t, k = k, e_shareno = e_shareno, shareno = shareno, path = share_path+r"\share")
