import string
import random

def generate_password(length):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    upperalphabet = alphabet.upper()
    pw_len = length
    pwlist = []

    for i in range(pw_len//3):
        pwlist.append(alphabet[random.randrange(len(alphabet))])
        pwlist.append(upperalphabet[random.randrange(len(upperalphabet))])
        pwlist.append(str(random.randrange(10)))
    for i in range(pw_len-len(pwlist)):
        pwlist.append(alphabet[random.randrange(len(alphabet))])

    random.shuffle(pwlist)
    return "".join(pwlist)

