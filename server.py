import os
import sys
import datetime
from socket import *
from os.path import *
from threading import *


def read_conf():
    """Read the vhost file

    Returns:
        list: An array of vhost values
    """
    vhosts = []
    file = "vhosts.conf"

    with open(file, "r") as f:
        tmp = f.read().split('\n')

        for line in tmp:
            vhosts.append(line.split(","))

        f.close()

    return vhosts


def is_malformed(msg, http):
    """Given a message and an http protocol, check if the request is malformed 

    Args:
        msg (String): The request message
        http (String): The HTTP protocol of the request

    Returns:
        Boolean: Return true if the request is malformed, false otherwise
    """
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
        return 505

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
    """Given a request, parse it and return the status code

    Args:
        msg (String): The request message to parse
        hosts (List): The array of hosts

    Returns:
        List: An array of information about the response, including status code,
              filename, file length, and file type
    """
    method = msg.split(" ")[0].rstrip()
    url = msg.split(" ")[1].rstrip()
    http = msg.split(" ")[2].rstrip()
    code = is_malformed(msg, http)

    # TODO: Generate correct responses

    if code == 505:
        return [505]
    elif code == True:
        return [400]

    if method != "GET" and method != "PUT" \
            and method != "DELETE" and method != "NTW21INFO":
        return [405]

    if method == "GET":
        req = read_GET(msg, hosts)
        return respond_GET(req)


# Parsers

def read_GET(msg, hosts):
    """Parse the GET request and send data to the response generator function

    Args:
        msg (String): The request message to parse
        hosts (List): The array of hosts

    Returns:
        List: An array of information about the response, including status code,
              filename, file length, and file type
    """
    request_line = [i.strip() for i in msg.split("\n")[0].split(" ")]
    headers = [i.rstrip() for i in msg.split("\n")[1:]]

    if request_line[1] == "/":
        return [403, request_line[2]]

    tmp_host = ""
    tmp_file = request_line[1][1:]

    for i in headers:
        if i.split(":")[0] == "Host":
            tmp_host = i.split(": ")[1]

    for i in hosts:
        if tmp_host == "localhost:8080":
            HOST = "edoardoriggio.ch"
            break
        if i[0] == tmp_host:
            HOST = tmp_host
            break
    else:
        return [404, request_line[2]]

    files = [f for f in os.listdir(f"./{HOST}")
             if isfile(join(f"./{HOST}", f))]

    if tmp_file in files:
        length = os.stat(f"./{HOST}/{tmp_file}").st_size
        ext = os.path.splitext(f"./{HOST}/{tmp_file}")[1]

        return [200, request_line[2], f"./{HOST}/{tmp_file}", length, ext]
    else:
        return [404, request_line[2]]


# Responses

def respond_GET(req):
    """Generate a response based on the given request

    Args:
        req (String): The request

    Returns:
        List: An array containing the response, and the binary representation
              of data (if any)
    """
    code = req[0]
    protocol = req[1]

    msg = f"{protocol} {code} {STATUS_CODES[code]}\r\n"

    if code == 200:
        file = req[2]
        length = req[3]
        ext = FILE_TYPES[req[4]]

        content = ""

        if req[4] == ".png" or req[4] == ".jpg":
            with open(file, "rb") as f:
                content = f.read()
                f.close()

            msg += f"Date: {DATE}\r\nServer: {SERVER}\r\n" + \
                f"Content-Length: {length}\r\nContent-Type: {ext}\r\n\r\n"

            return [msg.encode(), content]
        else:
            with open(file, "r") as f:
                content = f.read()
                f.close()

            msg += f"Date: {DATE}\r\nServer: {SERVER}\r\n" + \
                f"Content-Length: {length}\r\nContent-Type: {ext}\r\n\r\n" + \
                content
    else:
        msg += f"Date: {DATE}\r\nServer: {SERVER}\r\n\r\n"

    return [msg.encode()]


# Global variables

hosts = read_conf()

PORT = 80
HOST = hosts[0]
STATUS_CODES = {
    200: "OK",
    201: "Created",
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    501: "Not Implemented",
    505: "HTTP Version Not Supported"
}
FILE_TYPES = {
    ".html": "text/html",
    ".png": "image/png",
    ".jpg": "image/jpg"
}
DATE = datetime.datetime.now(datetime.timezone.utc) \
    .strftime("%a, %d %b %Y %H:%M:%S GMT")
SERVER = "Roma Capoccia"


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
            resp = parse_request(msg, hosts)

            client_socket.sendall(resp[0])

            if len(resp) > 1:
                client_socket.sendall(resp[1])

            print(msg.encode())

            client_socket.close()
