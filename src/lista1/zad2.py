import sys


def encrypt(text, key):
    res = ""
    for c in text:
        res += chr(ord(c) ^ key)

    return res


def decrypt(encrypted, s_key):
    return encrypt(encrypted, s_key)


t = 'Python'
k = 7

# t = sys.argv[1]
# k = int(sys.argv[2])

r = encrypt(t, k)
print(r)
print(decrypt(r, k))
