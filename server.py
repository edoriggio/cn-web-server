import sys
from socket import *
from threading import *


def read_conf():
    vhosts = []
    file = "vhosts.conf"

    with open(file, "r") as f:
        tmp = f.read().split('\n')

        for line in tmp:
            vhosts.append(line.split(","))

    return vhosts


def is_malformed(msg, http):
    request_line = msg.split('\n')[0].split(" ")
    headers = msg.split('\n\n')[0]

    # if request_line[0] != "GET" or request_line[0] != "PUT" \
    #     or request_line[0] != "DELETE" or request_line[0] != "NTW21INFO":

    #     return True

    if request_line[1][0] != "/":
        return False

    if request_line[2] != "HTTP/1.0" or request_line[2] != "HTTP/1.1":
        return False


def read_request(msg, hosts):
    HOST = hosts[0]

    method = msg.split(" ")[0]
    url = msg.split(" ")[1]
    http = msg.split(" ")[2]

    if is_malformed(msg, http):
        return 400
    elif method[0] != "GET" or method[0] != "PUT" \
        or method[0] != "DELETE" or method[0] != "NTW21INFO":

        return 403

    if method == "GET":
        read_GET(msg)
        

if __name__ == "__main__":
    hosts = read_conf()

    PORT = 80

    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])

    with socket(AF_INET, SOCK_STREAM) as socket:
        socket.bind(("", PORT))
        socket.listen(1)

        print(f"Server is up and available on port {PORT}")

        while True:
            client_socket, addr = socket.accept()
            print(f"Connection from {addr} has been established.")

            req = client_socket.recv(1024)

            # read_request(req, hosts)
            print(r'%s' %req)
            
            for i in req.splitlines():
                print(r'%s' %i)


            client_socket.close()
