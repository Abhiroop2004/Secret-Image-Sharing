import secrets
from PIL import Image
from numpy import zeros,array,size,poly, matmul, shape, linalg, loadtxt, stack
import galois
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

class KN:
    def __init__(self):

        order=2**8
        self.add_map=loadtxt(r'secret_image_sharing\asset\addmap.txt', dtype=int)
        self.mul_map=loadtxt(r'secret_image_sharing\asset\mulmap.txt', dtype=int)
        self.GF = galois.GF(order, repr='int')

    def power(self, x_shareholder, i):
        if i==0: return 1
        if i==1: return x_shareholder
        sol=x_shareholder
        for x in range(1,i):  sol = self.mul_map[sol][x_shareholder]
        return sol

    def polynomial_GF(self, equation : list, x_shareholder : int, k: int) -> int:
        x=[]
        for i in range(k-1, -1, -1): x.append(self.power(x_shareholder, i))
        share = self.mul_map[equation[0]][x[0]]
        for i in range(1,k): share = self.add_map[share][self.mul_map[equation[i]][x[i]]]
        return share

    def generate_share(self, secret : int, n : int, k : int) -> list[int]:
        #equation=[GF.Random() for _ in range(k-1)]
        equation=[secrets.randbelow(256) for i in range(k-1)]
        equation.append(secret)
        shares=[]
        for i in range(1,n+1):
            share = self.polynomial_GF(equation, i, k)
            shares.append(share)
        return shares

    def encrypt(self , n : int, k : int, file_name : str, dest : str = "Shares", save : int = 1) -> any:
        os.makedirs(dest, exist_ok=True)
        #print(current_dir.removesuffix("secret_image_sharing"))
        img  = Image.open(current_dir.removesuffix("secret_image_sharing")+file_name)
        arr=img.load()
        w,h=img.size
        arr = array([[arr[x, y] for y in range(h)] for x in range(w)])
        shares = zeros([n, h, w, 3], dtype=int) 
        for x in range(w): #generate the shares
            for y in range(h):
                secretr, secretg, secretb=arr[x][y]
                #print(secretr, secretg, secretb)
                sharer = self.generate_share(secretr, n, k)
                shareg = self.generate_share(secretg, n, k)
                shareb = self.generate_share(secretb, n, k)
                for z in range(n):
                    shares[z][y][x][0]=sharer[z]
                    shares[z][y][x][1]=shareg[z]
                    shares[z][y][x][2]=shareb[z]
        if save==1:
            for i in range(n): #saving images
                img=Image.fromarray(shares[i].astype('uint8'))
                img.save(dest+r"\share"+str(i+1)+".png")
        else: return shares

    def matrix_mul(self, A : list, B : list) -> list:  #X= A^-1 x B
        rowA=len(A)
        rowB=len(B)
        #result=[[0 for _ in range(columnB)] for _ in range(rowA)]
        result=[0 for _ in range(rowA)] 
        for m in range(rowA):           
            for o in range(rowB): 
                    result[m] = self.add_map[result[m]][self.mul_map[int(A[m][o])][B[o]]]
        return result

    def solve_linear(self, shares, n, w, h, share_number) -> list[list[int]]:
        secret=zeros([h,w], dtype=int)
        #GF = galois.GF(2**8, repr='int')
        A = self.GF([[self.power(X, i) for i in range(n - 1, -1, -1)] for X in share_number])
        A_inv=linalg.inv(A)
        for x in range(w):
            for y in range(h):
                #print(f"x={x}, y={y}")
                B=array(shares[:, x, y])
                X= self.matrix_mul(A_inv, B)
                secret[y][x]=X[-1]
        return secret

    def decrypt(self, shareno : list[int], share_path : str = "Shares") -> None:
        shares = []
        k = len(shareno)
        for i in range(k):
            img=Image.open(share_path+r"\share"+str(shareno[i])+".png") #opens ith share
            shares.append(array(img))
        secret = self.reconstruct(shares = shares, n = k, shareno = shareno)
        secret.save("secret.png")

    def reconstruct(self, shares, n, shareno) -> None:
        shares_red= [[0] for _ in range(n)]
        shares_green= [[0] for _ in range(n)]
        shares_blue= [[0] for _ in range(n)]
        for i in range(n):  
            #print(shares)
            #print(len(shares[i]), len(shares[i][0]), len(shares[i][0][0]))
            #return
            w,h=len(shares[i][0]), len(shares[i])
            arr_r, arr_g, arr_b = shares[i][:, :, 0], shares[i][:, :, 1], shares[i][:, :, 2]
            #arr_r, arr_g, arr_b=red.load(), green.load(), blue.load()
            shares_red [i] = array([[arr_r[y, x] for y in range(h)] for x in range(w)])
            shares_green[i] = array([[arr_g[y, x] for y in range(h)] for x in range(w)])
            shares_blue[i] = array([[arr_b[y, x] for y in range(h)] for x in range(w)])

        secret_red = self.solve_linear(array(shares_red), n, w, h, shareno)
        secret_green = self.solve_linear(array(shares_green), n, w, h, shareno)
        secret_blue = self.solve_linear(array(shares_blue), n, w, h, shareno)
        secret = stack((secret_red, secret_green, secret_blue), axis=-1)
        secret_img=Image.fromarray(secret.astype('uint8'))
        return secret_img

"""
def main():
    print("Visual Cryptography (k,n) Scheme ")
    choice=int(input("Enter 1 to distribute, 2 to reveal secret: "))
    if (choice==1):
        file_name=input("Enter name of the image file with extension and path:")
        n= int(input("Enter no of shares(n): "))
        k=int(input("Enter minimum shares to reveal secret(k): "))
        img=Image.open(file_name)
        encrypt(n,k,img)
        print("Shares Generated!")
    elif (choice==2):
        n=int(input("Enter number of shares:"))
        print("Enter the share numbers(1-n):")
        shareno= [0 for _ in range (n)]
        for i in range(n):
          shareno[i]=int(input())
        print(shareno)
        decrypt(n, shareno)
        print("Secret Generated")
    else:
      print("Wrong Choice!")

#if __name__=="__main__":
#    main()
"""