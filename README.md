# Secret-Image-Sharing
Contains functions for secret sharing of images using Shamir's Secret Sharing and Visual Cryptography 
Note: Visual Cryptography code is incomplete

Examples:
- **(k,n) threshold**
```py
from secret_image_sharing.kn import KN
kn = KN()
kn.encrypt( n=3, k=2, file_name=r"secret_image_sharing\asset\test_img.jpg", dest="Shares") #run this line first
kn.decrypt(shareno=[2, 3]) #run this line later
```
- **(t,k,n) threshold**
```py
from secret_image_sharing.tkn import TKN
tkn = TKN()
tkn.encrypt(t = 2, k = 4, n = 6, file_name=r"secret_image_sharing\asset\test_img.jpg") #run this line first
tkn.decrypt([1, 2], [4, 5]) #run this line later
```
**This is an extension of the work done during Summer of 2024, supervised by Prof. Dr. Avishek Adhikary.**