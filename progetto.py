import socket
import os
from datetime import datetime

# MIME types di base
MIME_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".jpg": "image/jpeg",
    ".png": "image/png",
    ".js": "application/javascript"
}

HOST = '127.0.0.1'
PORT = 8080
WWW_DIR = "./www"

def logger(method, path, status):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {method} {path} -> {status}")

def get_mime_type(filepath):
    _, ext = os.path.splitext(filepath)
    return MIME_TYPES.get(ext, "application/octet-stream")

def handle_request(client_socket):
    try:
        request = client_socket.recv(1024).decode()
        lines = request.splitlines()
        if not lines:
            return

        request_line = lines[0]
        method, path, _ = request_line.split()

        if method != 'GET':
            response = "HTTP/1.1 405 Method Not Allowed\r\n\r\nMethod Not Allowed"
            client_socket.send(response.encode())
            logger(method, path, 405)
            return

        if path == '/':
            path = '/index.html'

        filepath = os.path.join(WWW_DIR, path.lstrip('/'))

        if os.path.isfile(filepath):
            with open(filepath, 'rb') as f:
                body = f.read()
            mime = get_mime_type(filepath)
            header = (
                "HTTP/1.1 200 OK\r\n"
                f"Content-Type: {mime}\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n\r\n"
            )
            client_socket.send(header.encode() + body)
            logger(method, path, 200)
        else:
            body = b"<h1>404 Not Found</h1>"
            header = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n\r\n"
            )
            client_socket.send(header.encode() + body)
            logger(method, path, 404)

    finally:
        client_socket.close()

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server avviato su http://{HOST}:{PORT}")

        while True:
            client_conn, _ = server_socket.accept()
            handle_request(client_conn)

if __name__ == "__main__":
    run_server()
