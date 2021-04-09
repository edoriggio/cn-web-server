import os
import sys
import datetime
from socket import *
from os.path import *
from concurrent.futures import ThreadPoolExecutor


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


def is_malformed(msg):
    """Given a message and an http protocol, check if the request is malformed

    Args:
        msg (String): The request message

    Returns:
        Boolean or Int: Return false or a status code if the request is malformed
    """
    request_line = [i.strip() for i in msg.split("\n")[0].split(" ")]
    headers = [i.rstrip() for i in msg.split("\n")[1:-2]]
    body = msg.split("\r\n\r\n")[1]

    if len(request_line) != 3:
        return 400

    if request_line[0] != "GET" and request_line[0] != "PUT" \
            and request_line[0] != "DELETE" and request_line[0] != "NTW21INFO":

        if request_line[0] == "PATCH" or request_line[0] == "POST":
            return 405

        return 501

    if request_line[1][0] != "/":
        return 400

    if request_line[2] != "HTTP/1.1" and request_line[2] != "HTTP/1.0":
        return 505

    if (request_line[0] == "GET" or request_line[0] == "DELETE"
            or request_line[0] == "NTW21INFO") and body:

        return 400

    for i in range(len(headers) - 1):
        for j in range(i + 1, len(headers)):
            if headers[i].split(": ")[0] == headers[j].split(": ")[0]:
                return 400

    if request_line[0] == "PUT":
        found = False
        found_type = False
        length_req = 0
        content = ""

        if not body:
            return 400

        for i in headers:
            if i.split(": ")[0] == "Content-Length" and i.split(": ")[1]:
                found = True
                length_req = i.split(": ")[1]
                content = body
            if i.split(": ")[0] == "Content-Type" and i.split(": ")[1]:
                found_type = True

        if not found or not found_type:
            return 400
        else:
            with open("tmp.txt", "x") as f:
                f.write(content)
                f.close()

            length = os.stat("./tmp.txt").st_size
            os.remove("tmp.txt")

            if length != int(length_req):
                return 400

    if request_line[0] != "PUT":
        for i in headers:
            if i.split(": ")[0] == "Content-Length" and i.split(": ")[1]:
                return 400

    if request_line[2] == "HTTP/1.1":
        found = False
        found_conn = False

        for i in headers:
            if i.split(": ")[0] == "Host" and i.split(": ")[1]:
                found = True

            if i.split(": ")[0] == "Connection" and \
                    (i.split(": ")[1] == "keep-alive" or i.split(": ")[1] == "close"):

                found_conn = True

        if found == False or found_conn == False:
            return 400

    return False


def parse_request(msg, hosts):
    """Given a request, parse it and return the status code

    Args:
        msg (String): The request message to parse
        hosts (List): The array of hosts

    Returns:
        List: An array of information about the response, including status code,
              filename, file length, file type and connection type
    """
    request_line = [i.strip() for i in msg.split("\n")[0].split(" ")]
    headers = [i.rstrip() for i in msg.split("\n")[1:-2]]

    print(request_line)

    method = request_line[0]
    http = request_line[2]
    connection = ""

    code = is_malformed(msg)

    if code != False:
        return respond_Error(code, http)

    if http == "HTTP/1.1":
        for i in headers:
            if i.split(": ")[0] == "Connection" and i.split(": ")[1]:
                connection = i.split(": ")[1]

    if method == "GET":
        req = read_GET(msg, hosts)
        return respond_GET(req, connection)
    elif method == "PUT":
        req = read_PUT(msg, hosts)
        return respond_PUT(req, connection)
    elif method == "DELETE":
        req = read_DELETE(msg, hosts)
        return respond_DELETE(req, connection)
    elif method == "NTW21INFO":
        req = read_NTW(msg, hosts)
        return respond_NTW(req, connection)


# Parsers

def read_GET(msg, hosts):
    """Parse the GET request and send data to the response generator function

    Args:
        msg (String): The request message to parse
        hosts (List): The array of hosts

    Returns:
        List: An array of information about the request, including status code,
              filename, file length, file type and connection type
    """
    request_line = [i.strip() for i in msg.split("\n")[0].split(" ")]
    headers = [i.rstrip() for i in msg.split("\n")[1:]]

    tmp_host = ""
    tmp_file = request_line[1][1:]

    for i in headers:
        if i.split(":")[0] == "Host":
            tmp_host = i.split(": ")[1]

    for i in hosts:
        if tmp_host == f"localhost:{PORT}":
            # CHANGE THIS LINE IN ORDER TO SEE A STUDENT'S WEBSITE IN THE BROWSER
            HOST = hosts[1][0]
            break
        if i[0] == tmp_host:
            HOST = tmp_host
            break
    else:
        return [404, request_line[2]]

    if request_line[1] == "/":
        root_file = ""

        for i in hosts:
            if i[0] == HOST:
                root_file = i[1]

        length = os.stat(f"./{HOST}/{root_file}").st_size
        ext = os.path.splitext(f"./{HOST}/{root_file}")[1]

        return [200, request_line[2], f"./{HOST}/{root_file}", length, ext]

    if os.path.exists(f"./{HOST}/{tmp_file}"):
        if os.path.isdir(f"./{HOST}/{tmp_file}"):
            return [403, request_line[2]]
        else:
            ext = os.path.splitext(f"./{HOST}/{tmp_file}")[1]

        length = os.stat(f"./{HOST}/{tmp_file}").st_size

        return [200, request_line[2], f"./{HOST}/{tmp_file}", length, ext]
    else:
        return [404, request_line[2]]


def read_NTW(msg, hosts):
    """Parse the NTW21INFO request and send data to the response generator function

    Args:
        msg (String): The request message to parse
        hosts (List): The array of hosts

    Returns:
        List: An array of information about the request, including status code,
              filename, file length, file type and connection type
    """
    request_line = [i.strip() for i in msg.split("\n")[0].split(" ")]
    headers = [i.rstrip() for i in msg.split("\n")[1:]]

    tmp_host = ""
    admin = ""
    email = ""

    for i in headers:
        if i.split(":")[0] == "Host":
            tmp_host = i.split(": ")[1]

    for i in hosts:
        if tmp_host == f"localhost:{PORT}":
            HOST = hosts[0][0]
            break
        if i[0] == tmp_host:
            HOST = tmp_host
            break
    else:
        return [404, request_line[2]]

    for i in hosts:
        if i[0] == HOST:
            admin = i[2]
            email = i[3]

    content = f"The administrator of {HOST} is {admin}.\n" + \
        f"You can contact him at {email}."

    with open("tmp.txt", "x") as f:
        f.write(content)
        f.close()

    length = os.stat("./tmp.txt").st_size
    os.remove("tmp.txt")

    return [200, request_line[2], content, length, ".txt"]


def read_DELETE(msg, hosts):
    """Parse the DELETE request and send data to the response generator function

    Args:
        msg (String): The request message to parse
        hosts (List): The array of hosts

    Returns:
        List: An array of information about the request, including status code,
              filename, file length, file type and connection type
    """
    request_line = [i.strip() for i in msg.split("\n")[0].split(" ")]
    headers = [i.rstrip() for i in msg.split("\n")[1:]]

    tmp_host = ""
    tmp_file = request_line[1][1:]

    for i in headers:
        if i.split(":")[0] == "Host":
            tmp_host = i.split(": ")[1]

    for i in hosts:
        if tmp_host == f"localhost:{PORT}":
            HOST = hosts[0][0]
            break
        if i[0] == tmp_host:
            HOST = tmp_host
            break
    else:
        return [404, request_line[2]]

    if os.path.exists(f"./{HOST}/{tmp_file}"):
        if os.path.isdir(f"./{HOST}/{tmp_file}"):
            os.rmdir(f"./{HOST}/{tmp_file}")
        else:
            os.remove(f"./{HOST}/{tmp_file}")

        return [204, request_line[2], f"./{HOST}/{tmp_file}"]
    else:
        return [404, request_line[2]]


def read_PUT(msg, hosts):
    """Parse the PUT request and send data to the response generator function

    Args:
        msg (String): The request message to parse
        hosts (List): The array of hosts

    Returns:
        List: An array of information about the request, including status code,
              filename, file length, file type and connection type
    """
    request_line = [i.strip() for i in msg.split("\n")[0].split(" ")]
    headers = [i.rstrip() for i in msg.split("\n")[1:]]

    tmp_host = ""
    tmp_file = request_line[1][1:]
    code = 201

    for i in headers:
        if i.split(":")[0] == "Host":
            tmp_host = i.split(": ")[1]

    for i in hosts:
        if tmp_host == f"localhost:{PORT}":
            HOST = hosts[0][0]
            break
        if i[0] == tmp_host:
            HOST = tmp_host
            break
    else:
        return [404, request_line[2]]

    path = tmp_file.split("/")

    for i in range(len(path)):
        if i == len(path) - 1:
            if os.path.exists(f"./{HOST}/{'/'.join(path[:(i + 1)])}"):
                code = 200

            with open(f"./{HOST}/{'/'.join(path[:(i + 1)])}", "w") as f:
                f.write(msg.split("\r\n\r\n")[1])
                f.close()
        else:
            if not os.path.exists(f"./{HOST}/{'/'.join(path[:(i + 1)])}"):
                os.mkdir(f"./{HOST}/{'/'.join(path[:(i + 1)])}")

    return [code, request_line[2], f"/{HOST}/{tmp_file}"]


# Responses

def respond_Error(code, protocol):
    """Generate a response based on the given error code

    Args:
        req (List): An array of information about the request, including status code,
              filename, file length, and file type

    Returns:
        List: An array containing the response and the connection type
    """
    msg = f"{protocol} {code} {STATUS_CODES[code]}\r\n" + \
        f"Date: {DATE}\r\nServer: {SERVER}\r\n\r\n"

    return [msg.encode(), "close"]


def respond_GET(req, connection):
    """Generate a response based on the given GET request

    Args:
        req (List): An array of information about the request, including status code,
              filename, file length, and file type

    Returns:
        List: An array containing the response, the binary representation
              of data (if any) and the connection type
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

            return [msg.encode(), connection, content]
        else:
            with open(file, "r") as f:
                content = f.read()
                f.close()

            msg += f"Date: {DATE}\r\nServer: {SERVER}\r\n" + \
                f"Content-Length: {length}\r\nContent-Type: {ext}\r\n\r\n" + \
                content
    else:
        msg += f"Date: {DATE}\r\nServer: {SERVER}\r\n\r\n"

    return [msg.encode(), connection]


def respond_NTW(req, connection):
    """Generate a response based on the given NTW21INFO request

    Args:
        req (List): An array of information about the request, including status code,
              filename, file length, and file type

    Returns:
        List: An array containing the response, the binary representation
              of data (if any) and the connection type
    """
    code = req[0]
    protocol = req[1]

    msg = f"{protocol} {code} {STATUS_CODES[code]}\r\n"

    if code == 200:
        length = req[3]
        ext = FILE_TYPES[req[4]]

        msg += f"Date: {DATE}\r\nServer: {SERVER}\r\n" + \
            f"Content-Length: {length}\r\nContent-Type: {ext}\r\n\r\n" + \
            req[2]
    else:
        msg += f"Date: {DATE}\r\nServer: {SERVER}\r\n\r\n"

    return [msg.encode(), connection]


def respond_DELETE(req, connection):
    """Generate a response based on the given DELETE request

    Args:
        req (List): An array of information about the request, including status code,
              filename, file length, and file type

    Returns:
        List: An array containing the response, the binary representation
              of data (if any) and the connection type
    """
    code = req[0]
    protocol = req[1]

    msg = f"{protocol} {code} {STATUS_CODES[code]}\r\n" + \
        f"Date: {DATE}\r\nServer: {SERVER}\r\n\r\n"

    return [msg.encode(), connection]


def respond_PUT(req, connection):
    """Generate a response based on the given PUT request

    Args:
        req (List): An array of information about the request, including status code,
              filename, file length, and file type

    Returns:
        List: An array containing the response, the binary representation
              of data (if any) and the connection type
    """
    code = req[0]
    protocol = req[1]
    destination = req[2]

    msg = f"{protocol} {code} {STATUS_CODES[code]}\r\n" + \
        f"Date: {DATE}\r\nServer: {SERVER}\r\n" + \
        f"Content-Location: {destination}\r\n\r\n"

    return [msg.encode(), connection]


# Global variables

hosts = read_conf()

PORT = 80
HOST = hosts[0]
STATUS_CODES = {
    200: "OK",
    201: "Created",
    204: "No Content",
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    501: "Not Implemented",
    505: "HTTP Version Not Supported"
}
FILE_TYPES = {
    ".html": "text/html",
    ".txt": "text/plain",
    ".png": "image/png",
    ".jpg": "image/jpg"
}
DATE = datetime.datetime.now(datetime.timezone.utc) \
    .strftime("%a, %d %b %Y %H:%M:%S GMT")
SERVER = "Roma Capoccia"


# Multithreading func

def thread_function(client_socket, addr):
    """ Function to be called everytime a new thread has been created

    Args:
        client_socket (socket): The client socket where the server needs to listen
                                for HTTP requests
        addr (Int): The client_socket address
    """
    while True:
        print(f"Connection from {addr} has been established.")

        msg = client_socket.recv(1024).decode()
        resp = parse_request(msg, hosts)

        client_socket.sendall(resp[0])

        if len(resp) > 2:
            client_socket.sendall(resp[2])

        if resp[1] == "close" or resp[0].decode().split(" ")[0] == "HTTP/1.0":
            print("closing socket")
            client_socket.close()
            break


# Driver code

if __name__ == "__main__":
    if len(sys.argv) > 1:
        PORT = int(sys.argv[1])

    s = socket(AF_INET, SOCK_STREAM)
    s.bind(("", PORT))
    s.listen(1)

    print(f"Server is up and available on port {PORT}")

    with ThreadPoolExecutor() as pool:
        while True:
            client_socket, addr = s.accept()
            pool.submit(thread_function, client_socket, addr)
