import string
import random

def generate_password(length):
    chars = string.letters + string.digits
    return ''.join((random.choice(chars)) for x in range(length))

