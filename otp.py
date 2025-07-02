import random
uc=[chr(i) for i in range(ord('A'),ord('Z')+1)]
lc=[chr(i) for i in range(ord('a'),ord('z')+1)]
def genotp():
    otp=''
    for i in range(2):
        otp=otp+random.choice(uc) #otp=''+'B'--'B'
        otp=otp+random.choice(lc) #otp='B'+'c'--'Bc'
        otp=otp+str(random.randint(0,9)) #otp='Bc'+'6'--- 'Bc6'
    return otp
