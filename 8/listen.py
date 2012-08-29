#!/usr/bin/env python 

import socket 

def listen(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    client, address = s.accept()
    client.close()
    return address[1]

print listen('localhost', 5050)