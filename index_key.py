# Key initialization
def key(in_key):
    # Convert to binary with length 65 for ease
    in_key = bin(int(in_key, 16))[2:]
    lead_zeros = 65 - len(in_key)
    for z in range(lead_zeros):
        in_key = '0' + in_key

    # Permute the key through PC-1
    new_key = ''
    for j in [57,49,41,33,25,17,9,1,58,50,42,34,26,18,10,2,59,51,43,35,27,19,11,3,60,52,44,36,63,55,47,39,31,23,15,7,62,54,46,38,30,22,14,6,61,53,45,37,29,21,13,5,28,20,12,4]:
        new_key = new_key + in_key[j]

    # Initialize lists c and d
    c = []
    d = []

    # Rotating each half
    c.append(new_key[:28])
    d.append(new_key[28:])

    for j in range(16):
        if j in [0,1,8,15]:
            c.append(c[j][1:] + c[j][0])
            d.append(d[j][1:] + d[j][0])
        else:
            c.append(c[j][2:] + c[j][:2])
            d.append(d[j][2:] + d[j][:2])

    # Concatenation
    cd = []
    for j in range(17):
        cd.append('0' + c[j] + d[j])

    # Permute the key through PC-2
    k = 16 * ['0']
    for j in range(16):
        for o in [14,17,11,24,1,5,3,28,15,6,21,10,23,19,12,4,26,8,16,7,27,20,13,2,41,52,31,37,47,55,30,40,51,45,33,48,44,49,39,56,34,53,46,42,50,36,29,32]:
            k[j] = k[j] + cd[j+1][o]

    return k

def encrypt(message, key):
    enc_message = ""
    for i in range(0, len(message), 16):
        chunk = message[i:i+16].ljust(16, '0')
        enc_chunk = des(chunk, key)
        enc_message += enc_chunk
    return enc_message

def decrypt(message, key):
    dec_message = ""
    for i in range(0, len(message), 16):
        chunk = message[i:i+16].ljust(16, '0')
        dec_chunk = des(chunk, key[::-1])
        dec_message += dec_chunk
    return dec_message

def des(message, k):
    # Convert to binary with length 65 for ease
    message = bin(int(message, 16))[2:]
    lead_zeros = 65 - len(message)
    for z in range(lead_zeros):
        message = '0' + message

    # Permute the key message through IP
    new_message = ''
    for j in [58,50,42,34,26,18,10,2,60,52,44,36,28,20,12,4,62,54,46,38,30,22,14,6,64,56,48,40,32,24,16,8,57,49,41,33,25,17,9,1,59,51,43,35,27,19,11,3,61,53,45,37,29,21,13,5,63,55,47,39,31,23,15,7]:
        new_message = new_message + message[j]

    # Initialize lists l and r
    l = []
    r = []

    # Encode the data & compute ROUND 1-16
    l.append('0' + new_message[:32])
    r.append('0' + new_message[32:])

    for j in range(16):
        e = '0'
        for o in [32,1,2,3,4,5,4,5,6,7,8,9,8,9,10,11,12,13,12,13,14,15,16,17,16,17,18,19,20,21,20,21,22,23,24,25,24,25,26,27,28,29,28,29,30,31,32,1]:
            e = e + r[j][o]
        
        kxore = ''
        for o in range(1,49):
            kxore = kxore + str(int(k[j][o]) ^ int(e[o]))
        
        s = '0'
        arr = [[[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],[0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],[4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],[15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]],[[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],[3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],[0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],[13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]],[[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],[13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],[13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],[1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]],[[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],[13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],[10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],[3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]],[[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],[14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],[4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],[11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]],[[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],[10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],[9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],[4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]],[[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],[13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],[1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],[6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]],[[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7],[1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2],[7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8],[2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]]]
        for o in range(8):
            af = 2 * int(kxore[6*o]) + int(kxore[6*o+5])
            bcde = 8 * int(kxore[6*o+1]) + 4 * int(kxore[6*o+2]) + 2 * int(kxore[6*o+3]) + int(kxore[6*o+4])
            x = bin(arr[o][af][bcde])[2:]
            lead_zeros = 4 - len(x)
            for z in range(lead_zeros):
                x = '0' + x
            s = s + x
        
        p = '0'
        for o in [16,7,20,21,29,12,28,17,1,15,23,26,5,18,31,10,2,8,24,14,32,27,3,9,19,13,30,6,22,11,4,25]:
            p = p + s[o]
        
        lxorf = '0'
        for o in range(1,33):
            lxorf = lxorf + str(int(l[j][o]) ^ int(p[o]))
        
        l.append(r[j])
        r.append(lxorf)

    # Permute the encoded data through IP^(-1)
    r16l16 = '0' + r[16][1:] + l[16][1:]
    ciptxt = ''
    for j in [40,8,48,16,56,24,64,32,39,7,47,15,55,23,63,31,38,6,46,14,54,22,62,30,37,5,45,13,53,21,61,29,36,4,44,12,52,20,60,28,35,3,43,11,51,19,59,27,34,2,42,10,50,18,58,26,33,1,41,9,49,17,57,25]:
        ciptxt = ciptxt + r16l16[j]

    #Convert back into hexadecimal
    ciptxt = hex(int(ciptxt, 2))[2:]
    lead_zeros = 16 - len(ciptxt)
    for z in range(lead_zeros):
        ciptxt = '0' + ciptxt
    return ciptxt
