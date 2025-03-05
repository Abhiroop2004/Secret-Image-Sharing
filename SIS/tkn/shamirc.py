import secrets
from PIL import Image
from numpy import zeros,array,size,poly, matmul, shape, linalg, loadtxt, stack
import galois

order=2**8
GF = galois.GF(order, repr='int')

add_map=loadtxt('addmap.txt', dtype=int)
mul_map=loadtxt('mulmap.txt', dtype=int)

def power(x_shareholder, i):
    if i==0: return 1
    if i==1: return x_shareholder
    sol=x_shareholder
    for x in range(1,i):  sol=mul_map[sol][x_shareholder]
    return sol

def polynomial_GF(equation : list, x_shareholder : int, k: int) -> int:
     x=[]
     for i in range(k-1, -1, -1): x.append(power(x_shareholder, i))
     #print(equation)
     share=mul_map[equation[0]][x[0]]
     for i in range(1,k): share = add_map[share][mul_map[equation[i]][x[i]]]
     return share

def generate_share(secret : int, n : int, k : int) -> list[int]:
    #equation=[GF.Random() for _ in range(k-1)]
    equation=[secrets.randbelow(256) for i in range(k-1)]
    equation.append(secret)
    shares=[]
    for i in range(1,n+1):
        share=polynomial_GF(equation, i, k)
        shares.append(share)
    return shares

def encrypt(n : int, k : int, img : Image) -> None:
    arr=img.load()
    w,h=img.size
    arr = array([[arr[x, y] for y in range(h)] for x in range(w)])
    shares = zeros([n, h, w, 3], dtype=int) 
    for x in range(w): #generate the shares
        for y in range(h):
            secretr, secretg, secretb=arr[x][y]
            #print(secretr, secretg, secretb)
            sharer=generate_share(secretr, n, k)
            shareg=generate_share(secretg, n, k)
            shareb=generate_share(secretb, n, k)
            for z in range(n):
                shares[z][y][x][0]=sharer[z]
                shares[z][y][x][1]=shareg[z]
                shares[z][y][x][2]=shareb[z]
    return shares
    for i in range(n): #saving images
        img=Image.fromarray(shares[i].astype('uint8'))
        img.save(r"Shares\share"+str(i+1)+".png")

def matrix_mul(A : list, B : list) -> list:  #X= A^-1 x B
    rowA=len(A)
    rowB=len(B)
    #result=[[0 for _ in range(columnB)] for _ in range(rowA)]
    result=[0 for _ in range(rowA)] 
    for m in range(rowA):           
        for o in range(rowB): 
                result[m] = add_map[result[m]][mul_map[int(A[m][o])][B[o]]]
    return result

def solve_linear(shares, n, w, h, share_number) -> list[list[int]]:
    secret=zeros([h,w], dtype=int)
    #GF = galois.GF(2**8, repr='int')
    A = GF([[power(X, i) for i in range(n - 1, -1, -1)] for X in share_number])
    A_inv=linalg.inv(A)
    for x in range(w):
        for y in range(h):
            #print(f"x={x}, y={y}")
            B=array(shares[:, x, y])
            X=matrix_mul(A_inv, B)
            secret[y][x]=X[-1]
    return secret

def decrypt(n : int, shareno : list[int]) -> None:
    shares_red= [[0] for _ in range(n)]
    shares_green= [[0] for _ in range(n)]
    shares_blue= [[0] for _ in range(n)]
    for i in range(n):
        #img=Image.open("/content/drive/MyDrive/Shares/share"+str(shareno[i])+".png")
        img=Image.open(r"Shares\share"+str(shareno[i])+".png") #opens ith share
        w,h=img.size 
        red, green, blue = img.split()
        arr_r, arr_g, arr_b=red.load(), green.load(), blue.load()
        shares_red [i] = array([[arr_r[x, y] for y in range(h)] for x in range(w)])
        shares_green[i] = array([[arr_g[x, y] for y in range(h)] for x in range(w)])
        shares_blue[i] = array([[arr_b[x, y] for y in range(h)] for x in range(w)])
    print(len(shares_red), len(shares_red[0]), len(shares_red[0][0]), len(shares_red[0][0]))

    secret_red=solve_linear(array(shares_red), n, w, h, shareno)
    secret_green=solve_linear(array(shares_green), n, w, h, shareno)
    secret_blue=solve_linear(array(shares_blue), n, w, h, shareno)
    secret = stack((secret_red, secret_green, secret_blue), axis=-1)
    secret_img=Image.fromarray(secret.astype('uint8'))
    secret_img.save("secret.png")

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

if __name__=="__main__":
    main()