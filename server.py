import sys
from socket import *
from os.path import *
from os import listdir
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
    request_line = [i.strip() for i in msg.split("\n")[0].split(" ")]
    headers = [i.rstrip() for i in msg.split("\n")[1:]]
    body = msg.split("\r\n\r\n")[1]

    # TODO: Add remaining cases (for PUT, and connection for HTTP/1.1) and
    # check if GET has body. Check for duplicate headers

    # if request_line[0] != "GET" or request_line[0] != "PUT" \
    #     or request_line[0] != "DELETE" or request_line[0] != "NTW21INFO":

    #     return True

    if len(request_line) != 3:
        return True

    if request_line[1][0] != "/":
        return True

    if request_line[2] != "HTTP/1.1" and request_line[2] != "HTTP/1.0":
        return True

    if request_line[0] == "GET" and body:
        return True


    if request_line[2] == "HTTP/1.1":
        found = False

        for i in headers:
            if i.split(":")[0] == "Host" and i.split(":")[1]:
                found = True

        if not found:
            return True

    return False


def parse_request(msg, hosts):
    method = msg.split(" ")[0].rstrip()
    url = msg.split(" ")[1].rstrip()
    http = msg.split(" ")[2].rstrip()

    if is_malformed(msg, http):
        return 400

    if method != "GET" and method != "PUT" \
            and method != "DELETE" and method != "NTW21INFO":
        return 405

    if method == "GET":
        res = read_GET(msg, hosts)
        return res


# Parsers

def read_GET(msg, hosts):
    request_line = [i.strip() for i in msg.split("\n")[0].split(" ")]
    headers = [i.rstrip() for i in msg.split("\n")[1:]]

    if request_line[1] == "/":
        return 403

    tmp_host = ""
    tmp_file = request_line[1][1:]

    for i in headers:
        if i.split(":")[0] == "Host":
            tmp_host = i.split(": ")[1]

    for i in hosts:
        if i[0] == tmp_host:
            HOST = tmp_host
            break
    else:
        return 404

    files = [f for f in listdir(f"./{HOST}") if isfile(join(f"./{HOST}", f))]

    if tmp_file in files:
        return 200
    else:
        return 404


# Global variables

hosts = read_conf()

PORT = 80
HOST = hosts[0]


# Driver code

if __name__ == "__main__":
    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])

    with socket(AF_INET, SOCK_STREAM) as socket:
        socket.bind(("", PORT))
        socket.listen(1)

        print(f"Server is up and available on port {PORT}")

        while True:
            client_socket, addr = socket.accept()
            print(f"Connection from {addr} has been established.")

            msg = client_socket.recv(1024).decode()

            print(parse_request(msg, hosts))
            print(msg)

            client_socket.close()
