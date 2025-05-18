#------ Pixel-Expansion Scheme ------

from PIL import Image
from itertools import combinations
import itertools
import numpy as np
from os import urandom

def compressimage(img, ratio): #compressing the user input image
  w,h=img.size
  w,h=int(w*ratio),int(h*ratio) #setting size of compressed image
  imgc=img.resize((w,h),Image.LANCZOS)
  return imgc

def generate_binary_numbers(n): #generating all possible n-bit binary numbers
    binary_numbers = []
    for combination in itertools.product([0, 1], repeat=n):
        binary_numbers.append(list(combination)) 
    return binary_numbers

def split_pairs(a): #splitting the min qualified set pair-wise to equation s1 and s0
    pairs=[]
    l=len(a)
    for i in range(l):
        if (i%2==1):  pairs.append([a[i-1],a[i]])
    if (l%2==1): pairs.append([a[l-1]])
    return pairs

def convertpixel(arr):  #converting from mathematical representation to PIL python representation
    a=[[() for _ in range(len(arr[0]))] for _ in range(len(arr))]
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            if (arr[i][j]==0): a[i][j]=(255, 0) #white represented by 0 is converted to 255 luminosity and 0 transparency
            else: a[i][j]=(0, 255)  #black represented by 1 is converted to 0 luminosity and 255 transparency
    return a

def s0(a,n,p):  #generating the complete S0 matrix 
    a=split_pairs(a)
    npairs=len(a)
    solution=[]
    for combination in p:
        for j in range(npairs):
            flag=0
            for i in a[j]:
                if ((np.dot(combination,i)%2)!=0): flag=1 #checking if one expression satisfies condition
            if (flag==0):    solution.append(combination) #add to S0 if both satisfy the condtion
    return solution

def s1(a,n,p):  #generating the complete S1 matrix
    a=split_pairs(a)
    npairs=len(a)
    solution=[]
    for combination in p:
        for j in range(npairs):
            flag=0
            for i in a[j]:
                if ((np.dot(combination,i)%2)!=1):  flag=1 #checking if one expression satisfies condition
            if (flag==0):     solution.append(combination) #add to S1 if both satisfy the condtion
    return solution

def make_symmetric(s): #making the shares Symmetric: n*n or almost Symmetric: n*(n-1)
  if (s>2):
    side = int(np.ceil(np.sqrt(s)))
    w = side
    h = side-1 if ((side*(side-1))-s>=0) else side
  else:
    w,h=2,1
  return (w,h) #expansion coefficients

def appenddummy(s_0,s_1): #appending dummy pixel to s0 and s1 matrix
  appendzero=[(255, 0) for _ in range(len(s_0))] #append dummy whites to S0
  appendone=[(0, 255) for _ in range(len(s_1))] ##append dummy blacks to S1
  for i in range(exp1+exp2-length_s):
    s_0.append(appendzero)
    s_1.append(appendone)
  return (s_0,s_1)

print("Visual Cryptography (k,n) Scheme ")
n= int(input("Enter no of shares(n): "))
m= int(input("Enter no of mandatory shares: "))
if (m!=0):
    print("Enter the mandatory share/s(0 to n-1): ")
a=[0]*m
for i in range(m):
    a[i]=int(input())
k=int(input("Enter minimum shares to reveal secret(k): "))
s=list(combinations(range(n), k))
mqps = [x for x in s if all(y in x for y in a)]
length= len(mqps)

coeff_matrix = [[0 for i in range(n)] for j in range(length)]
zerom=[[0] for i in range (length)]

for i in range(length):
    print(mqps[i])
    for j in mqps[i]:
        print(i,j)
        coeff_matrix[i][j]=1

print("Min Qualified Power Set: ",mqps)
print("Coefficient Matrix:  ",coeff_matrix)
p=generate_binary_numbers(n)
s_1=convertpixel(s1(coeff_matrix, n, p))
s_0=convertpixel(s0(coeff_matrix, n, p))

print("\nSolution:","\n S0 = ",s_0,"\n S1 = ",s_1)
length_s=len(s_0)
print("Length=",length_s)
exp1,exp2=make_symmetric(length_s)
s_0,s_1=appenddummy(s_0,s_1)
img=Image.open(r"test6.png").convert('1')
#img=Image.open("test6.PNG").convert('1')
arr=img.load()
w,h=img.size
print("Expasion:",exp1,exp2)
arr = np.array([[arr[x, y] for y in range(h)] for x in range(w)])
shares = [Image.new("LA", (w*exp1, h*exp2)) for _ in range(n)]
# Iterate over each pixel in the input array

for i in range(w):
    for j in range(h):
        #print(arr[i][j])
        if arr[i][j] == 255:
            np.random.shuffle(s_0)
            #print("\nS0=",s_0)
            for k in range(n):
                iter1=0
                for l in range(exp1):
                  for m in range(exp2):
                    shares[k].putpixel((i*exp1+l, j*exp2+m), s_0[l+m][k])
                #shares[k].putpixel((i*2+1, j), s_0[1][k])
        else:
            np.random.shuffle(s_1)
            #print("\nS1=",s_1)
            for k in range(n):
                for l in range(exp1):
                  for m in range(exp2):
                    shares[k].putpixel((i*exp1+l, j*exp2+m), s_1[l+m][k])
                #shares[k].putpixel((i*2+1, j), s_1[1][k])
i=0
for share in shares:
    share.save(r"Shares\share" + str(i+1) + ".png")
    #share.save("share"+str(i+1)+".png")
    #files.download("share"+str(i+1)+".png")
    i=i+1
