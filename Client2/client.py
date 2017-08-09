import socket
import os,sys
from datetime import datetime
import hashlib
import subprocess

def close_server():
    timel = datetime.now().strftime("%I:%M%p %B %d, %Y")
    log.write("------- Connection Closed at " + timel + " -------\n")
    log.close()
    client_socket.close()
    exit(0)


def file_download(args, filename, flag):
    client_socket.send(args)
    data = client_socket.recv(4096)
    if flag != "udp" and flag != "tcp":
        print "Invalid arguments"
        return
    if data != "recieved":
        print data
        return
    if flag == "tcp":
        with open(filename,'wb') as file:
            while(1):
                inp = client_socket.recv(4096)
                if inp == "done":
                    break
                file.write(inp)
                client_socket.send("recieved")
        file.close()
        # conn.send('send perm')
        perm=client_socket.recv(4096)
        client_socket.send("msd")
        print perm
        subprocess.call(['chmod', perm, filename])
    elif flag == "udp":
        udp_port = int(client_socket.recv(4096))
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = (host, udp_port)
        udp_socket.sendto("recieved", addr)
        f = open(filename, "wb+")
        while True:
            data, addr = udp_socket.recvfrom(4096)
            if data == "done":
                print "asdas"
                break
            f.write(data)
            udp_socket.sendto("recieved", addr)
        f.close()
        udp_socket.close()

    hash1 = client_socket.recv(4096)
    md5 = hashlib.md5()
    f = open(filename)
    for line in f:
        md5.update(line)
    f.close()
    orig_hash = md5.hexdigest()
    if hash1 != orig_hash:
        # print hash,orig_hash
        print "File Sent Failed"
    else:
        client_socket.send("sendme")
        data = client_socket.recv(4096)
        print data
        print "md5sum: ", hash1
        print "Successfulluy Downloaded"


def print_data(inp):
    client_socket.send(inp)
    while True:
        try:
            data = client_socket.recv(4096)
        except:
            print "Error in Connection"
            close_server()
            break
        if data == "done":
            break
        try:
            client_socket.send("recieved")
        except:
            print "Connection Error"
            close_server()
        print data
    return

port = 1583
host = socket.gethostname()
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# down = raw_input("Download Folder: ")
try:
    log = open("client_log.log", "a+")
except:
    print "Cannot Open Log file"
    exit(0)
try:
    client_socket.connect((host, port))
except:
    print "No available server"
    client_socket.close()
    exit(0)
cnt = 0
print "Connection Established"
time = datetime.now().strftime("%I:%M%p %B %d, %Y")
log.write("------- Connected to " + host + " at " + time + " -------\nCommands Sent:\n")
while True:
    sys.stdout.write("prompt >")
    cnt += 1
    args = raw_input()
    inp = args.split()
    log.write(str(cnt) + ". " + args + "\n")
    if inp[0] == "index" or inp[0] == "hash":
        print_data(args)
    elif inp[0] == "download":
        file_download(args, " ".join(inp[2:]), inp[1])
    else:
        print "Invalid Command"
client_socket.close()
