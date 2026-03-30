def send_message(sock, message: str):
    sock.sendall(message.encode("utf-8"))


def receive_message(sock, buffer_size: int = 1024) -> bytes:
    return sock.recv(buffer_size)