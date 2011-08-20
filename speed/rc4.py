
# original c source: http://www.mathematik.uni-erlangen.de/~ruppert/

import sys

def umw(cc):
    c = ord(cc)
    if ord('0') <= c and c <= ord('9'):
        return c - ord('0')
    if ord('a') <= c and c <= ord('f'):
        return c - ord('a') + 10
    if ord('A') <= c and c <= ord('F'):
        return c - ord('A') + 10

def main():
    i = 0
    j = 0
    t = 0
    az = 0
    l = 0
    k = 0
    c = 0
    K = [0 for x in range(256)]
    S = [0 for x in range(256)]
    if len(sys.argv) != 2:
        print "Usage: 'python rc4.py file'"
        exit()

    try:
        ein = open(sys.argv[1], 'rb')
    except:
        print "File %s doesn't exist!" % sys.argv[1]
        exit()

    aus = open(sys.argv[1] + '.rc4', 'wb')

    key = raw_input("Key: ")
    az = (len(key)+1)/2

    # key
    for l in range(len(key)):
        if l % 2 == 0:
            K[l/2] = 16 * umw(key[l])
        else:
            K[l/2] += umw(key[l])

    for l in range(az, 256):
        K[l] = K[l-az]

    # init
    for l in range(256):
        S[l] = l

    j = 0
    for i in range(256):
        j = (j + S[i] + K[i]) % 256
        l = S[i]
        S[i] = S[j]
        S[j] = l

    i += 1
    while True:
        m = ein.read(1)
        if not m:
            break
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        l = S[i]
        S[i] = S[j]
        S[j] = l
        t = (S[i]+S[j]) % 256
        k = S[t]
        c = ord(m) ^ k
        aus.write(chr(c))

    ein.close()
    aus.close()
    
    print "Output file: %s" % sys.argv[1]+'.rc4'

if __name__ == '__main__':
    main()

