from sys import argv

if len(argv) < 4:
    print ('Usage: encrypt_RCM.py [cover_img file] [watermark] [stego_img file]')
    quit()

def change_to_binary(byte):
    binary_string = "{:08b}".format(ord(byte))
    return binary_string

def check_RCM(a, b):
    a1 = 2*a - b
    b1 = 2*b - a
    if (a1 <= 255 and a1 >= 0) and (b1 >= 0 and b1 <= 255):
        return True
    else:
        return False

def getLSB(byte):
    # print (byte & 1)
    return byte & 1

def watermark(a, b, bit, msg):
    check = check_RCM(a, b)  # kiểm tra cặp điểm ảnh có thuộc vùng RCM không
    # print('\tcheck: ', check)
    aLSB = getLSB(a)
    bLSB = getLSB(b)
    a1 = a
    b1 = b # a' và b'
    if check:
        if aLSB == 0 or (aLSB == 1 and bLSB == 0): # TH: LSB(a,b) thuộc (0,1) (1,0), (0,0)
            # print("\tTH 1")
            a1 = 2*a - b
            b1 = 2*b - a
            if a1 % 2 == 0:
                a1 = a1 + 1
        elif aLSB == 1 and bLSB == 1:   # TH2: LSB(a,b) = (1,1)
            # print("\tTH 2")
            a1 = a ^ 0x1  # dat LSB của a1 = 0
        # b1 = bit thong diep
        if b1 % 2 != 0:
            b1 = b1 ^ 1
        b1 = b1 + bit
    else:
        # print("\tTH 3")
        msg += str(aLSB)
        if a % 2 != 0:
            a1 = a1 ^ 0x1
    return a1, b1, msg, check

print("\tTHUỶ VÂN LSB ẢNH ĐEN TRẮNG")
print("============================================")

cover_img_name = argv[1]
wtm = argv[2]
stego_img_name = argv[3]

print(f"Cover image: {cover_img_name}")
print(f"Stego image: {stego_img_name}")

len_wtm = len(wtm)
msg = ""

for i in range(len_wtm):
    msg += change_to_binary(wtm[i])
print(f'Watermark: {wtm} -> {msg}')

# cộng độ dài của chuỗi watermark vào trong chuỗi giấu
msg = change_to_binary(chr(len_wtm)) + msg 

# print (cover_img_name)
cover_img = open(cover_img_name, 'rb')
stego_img = open(stego_img_name, 'wb')

#header
for i in range(54):
    byte = cover_img.read(1)
    stego_img.write(byte)

count = 54
i = 0
check = False
while True:
    byte3 = cover_img.read(1)
    byte4 = cover_img.read(1)
    if byte3 == b'' or byte4 == b'':
        stego_img.write(byte3)
        quit()
    byte1 = int(byte3.hex(),16)
    byte2 = int(byte4.hex(),16)
    if i < len(msg):
        print ("[+] ", count)
        a1, b1, msg, check = watermark(byte1,byte2, int(msg[i], 10), msg)
        stego_img.write(a1.to_bytes(1,'big'))
        stego_img.write(b1.to_bytes(1,'big'))
        if check:
            # print('[+] watermark ' , i)
            print('\tisRCM: ', check)
            print(f'\ta : {byte1} va b: {byte2}')
            print(f'\ta1 : {a1} va b1: {b1}')
            i += 1
    else:
        stego_img.write(byte1.to_bytes(1,'big'))
        stego_img.write(byte2.to_bytes(1,'big'))
    count += 2

cover_img.close()
stego_img.close() 

# python encrypt_RCM.py cover.bmp linh stego.bmp