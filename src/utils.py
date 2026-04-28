def send_message(sock, message: str):
    payload = message.encode("utf-8")
    size = len(payload).to_bytes(4, byteorder="big")
    sock.sendall(size + payload)


def _recv_exact(sock, n_bytes: int) -> bytes:
    chunks = b""
    while len(chunks) < n_bytes:
        chunk = sock.recv(n_bytes - len(chunks))
        if not chunk:
            return b""
        chunks += chunk
    return chunks


def receive_message(sock) -> bytes:
    raw_size = _recv_exact(sock, 4)
    if not raw_size:
        return b""
    size = int.from_bytes(raw_size, byteorder="big")
    return _recv_exact(sock, size)