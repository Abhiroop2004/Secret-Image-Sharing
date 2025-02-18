from PIL import Image
from numpy import array, zeros
def encrypt(n : int, k : int, img : Image) -> None:
    arr=img.load()
    w,h=img.size
    arr = array([[arr[x, y] for y in range(h)] for x in range(w)])
    shares = zeros([n, h, w, 3], dtype=int) 
    for x in range(w): #generate the shares
        for y in range(h):
            secretr, secretg, secretb=arr[x][y]
            print(secretr, secretg, secretb)
            #sharer=generate_share(secretr, n, k)
            #shareg=generate_share(secretg, n, k)
            #shareb=generate_share(secretb, n, k)
            #for z in range(n):
             #   shares[z][y][x][0]=sharer[z]
    #for i in range(n): #saving images
    #    img=Image.fromarray(shares[i].astype('uint8')).convert("L")
    #    img.save(r"C:\Users\Hp\OneDrive\Desktop\Code\Projects\Shares\share"+str(i+1)+".png")   
def main():
    print("Visual Cryptography (k,n) Scheme ")
    choice=int(input("Enter 1 to distribute, 2 to reveal secret: "))
    if (choice==1):
        file_name=input("Enter name of the image file with extension and path:")
        n= int(input("Enter no of shares(n): "))
        k=int(input("Enter minimum shares to reveal secret(k): "))
        img=Image.open(file_name)
        print(img)
        encrypt(n,k,img)
        print("Shares Generated!")
    elif (choice==2):
        n=int(input("Enter number of shares:"))
        print("Enter the share numbers(1-n):")
        shareno= [0 for _ in range (n)]
        for i in range(n):
          shareno[i]=int(input())
        print(shareno)
        #decrypt(n, shareno)
        print("Secret Generated")
    else:
      print("Wrong Choice!")

if __name__=="__main__":
    main()