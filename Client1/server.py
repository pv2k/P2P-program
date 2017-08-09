import socket
import os
import random
import re
from datetime import datetime
import hashlib

def regex(inp):
    reg = inp[2]
    print reg
    fl = False
    files = os.popen("find . -not -path '*/\.*' -type f").read()
    files = files.split('\n')
    if len(files) == 1:
        client_socket.send("No Files Found")
        return
    for j in files:
        if j != "" and re.search(reg, j) != None and re.search(reg, j).group(0) != '':
            j = '"' + j + '"'
            cmd = "stat --printf 'name: %n \tSize: %s bytes\t Type: %F\t Timestamp:%z\n' " + j
            res = os.popen(cmd).read()
            client_socket.send(res)
            fl = True
            if client_socket.recv(4096) != "recieved":
                break
    if not fl:
        client_socket.send("No Files Found")
    client_socket.send("done")


def longlist(args):
    files=os.popen('ls -l --full-time').read();
    # print files
    file = files.split('\n')
    lines=len(file)-2;  #two lines removed
    i = 0
    while i<len(file)-2:
        file_comp = file[i+1].split(' ')
        j = 0
        while j<len(file_comp):
            if(len(file_comp[j]))==0:
                del file_comp[j]
                j = j-1
            j = j+1
        file_data = "Name:"+file_comp[8]+"\tSize:"+ file_comp[4] +"Bytes\tModified_Time:"+file_comp[5] + " "+file_comp[6]
        if(file_comp[0][0] == 'd'):
            file_data = file_data +"\tType : Directory"
        elif(file_comp[0][0] == '-'):
            file_data = file_data +"\tType : File"
        client_socket.send(file_data)
        if client_socket.recv(4096) != "recieved":
            break
        i = i+1
    client_socket.send("done")

def shortlist(inp):
    inp = inp.split()
    time1 = inp[2] + " " + inp[3]
    time2 = inp[4] + " " + inp[5]
    files = os.popen("find %s -newermt %s ! -newermt  %s -not -path '*/\.*' -type f" % (
        ".", str('"' + time1 + '"'), str('"' + time2 + '"'))).read().split('\n')
    if len(files) == 1:
        client_socket.send("No Files Found")
        client_socket.recv(4096)
        return
    for j in files:
        if j != "":
            j = '"' + j + '"'
            cmd = "stat --printf 'Name: %n \tSize: %s bytes\t Type: %F\t Timestamp:%z\n' " + j
            res = os.popen(cmd).read()
            client_socket.send(res)
            if client_socket.recv(4096) != "recieved":
                break
    client_socket.send("done")


def verify(fname,flg):
    filename = '"' + fname + '"'
    cmd = "stat --printf '%z\n' " + filename
    t = os.popen(cmd).read().split('\n')[0]
    if t != "":
        md5 = hashlib.md5()
        f = open(fname)
        for line in f:
            md5.update(line)
        f.close()
        arr = []
        arr.append("md5sum: " + md5.hexdigest())
        arr.append("last modified: " + t)
        arr.append("file: " + fname)
        for i in arr:
            client_socket.send(i)
            if client_socket.recv(4096) != "recieved":
                break
        if flg == True:
            client_socket.send("done")
    else:
        client_socket.send("No Such File")    


def file_send(args):
    inp = args.split()
    flag = inp[1]
    filename = " ".join(inp[2:])
    err = os.popen('ls "' + filename + '"').read().split('\n')[0]
    if err == "":
        client_socket.send("No Such File or Directory")
        return
    client_socket.send("recieved")
    if flag == "tcp":
        f = open(filename, "rb")
        byte = f.read(4096)
        while byte:
            client_socket.send(byte)
            if client_socket.recv(4096) != "recieved":
                break
            byte = f.read(4096)
        f.close()
        client_socket.send("done")
        x=oct(os.stat(filename).st_mode & 0777)
        print x
        client_socket.send(str(x))
        client_socket.recv(4096)
    elif flag == "udp":
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_port = 1500
        try:
            udp_socket.bind((host, udp_port))
        except:
            udp_socket.bind((host, udp_port+8))
        client_socket.send(str(udp_port))
        data, addr = udp_socket.recvfrom(4096)
        if data == "recieved":
            f = open(filename, "rb")
            byte = f.read(4096)
            while byte:
                udp_socket.sendto(byte, addr)
                data, addr = udp_socket.recvfrom(4096)
                if data != "recieved":
                    print "asd"
                    break
                byte = f.read(4096)
            f.close()
            udp_socket.sendto("done", addr)
    else:
        print "Wrong Arguments"
        return
    md5 = hashlib.md5()
    f = open(filename)
    for line in f:
        md5.update(line)
    f.close()    
    hash = md5.hexdigest()
    client_socket.send(hash)
    cmd = "stat --printf 'name: %n \tSize: %s bytes\t Timestamp:%z\n' " + filename
    res = os.popen(cmd).read()
    if client_socket.recv(4096) == 'sendme':
        client_socket.send(res)
        print "Done"


def checkall():
    files = os.popen("find . -not -path '*/\.*' -type f").read()
    files = files.split('\n')
    for i in files:
        if i != "":
            verify(i,False)
    client_socket.send("done")

port = 1583
host = socket.gethostname()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(5)
# shared = raw_input("FullPath of Shared Folder: ")
log = open("server_log.log", "a+")
times = datetime.now().strftime("%I:%M%p %B %d, %Y")
log.write("********* Server Started at " + times + " *********\n\n")
while True:
    cnt = 0
    time = datetime.now().strftime("%I:%M%p %B %d, %Y")
    client_socket,addr=server_socket.accept()
    print("Got a connection from %s" % str(addr))
    log.write("------- Got a connection from " + str(addr) + "at " + time + " -------\n Commands Executed:\n")
    while True:
        cnt += 1
        try:
            args = client_socket.recv(4096)
            log.write(str(cnt) + ". " + args + "\n")
        except:
            print "Connection closed to client"
            timel = datetime.now().strftime("%I:%M%p %B %d, %Y")
            log.write("------- Connection Closed at " + timel + " -------\n")
            break
        p = args.split()
        if len(p) == 0 or p[0] == "close":
            client_socket.close()
            print "Connection closed to client"
            timel = datetime.now().strftime("%I:%M%p %B %d, %Y")
            log.write("------- Connection Closed at " + timel + " -------\n")
            break
        elif p[0] == "index":
            if p[1] == "longlist":
                longlist(args)
            elif p[1] == "regex":
                regex(p)
            elif p[1] == "shortlist":
                shortlist(args)
        elif p[0] == "hash":
            if p[1] == "verify":
                verify(p[2],True)
            elif p[1] == "checkall":
                checkall()
            else:
                client_socket.send("Invalid Arguments")
                client_socket.send("done")
        elif p[0] == "download":
            file_send(args)
        else:
            client_socket.send("Invalid Command")
            client_socket.send("done")
    client_socket.close()
