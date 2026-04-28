import json


def create_handshake_init(mode: str, max_msg_size: int) -> str:
    message = {
        "type": "handshake_init",
        "mode": mode,
        "max_msg_size": max_msg_size
    }
    return json.dumps(message)


def create_handshake_ack(status: str, window_size: int, message: str) -> str:
    response = {
        "type": "handshake_ack",
        "status": status,
        "window_size": window_size,
        "message": message
    }
    return json.dumps(response)


def create_data_packet(seq: int, total: int, data: str) -> str:
    packet = {
        "type": "data_packet",
        "seq": seq,
        "total": total,
        "data": data,
    }
    return json.dumps(packet)


def create_ack(seq: int) -> str:
    ack = {
        "type": "ack",
        "seq": seq,
    }
    return json.dumps(ack)


def create_message_reconstructed(message: str) -> str:
    response = {
        "type": "message_reconstructed",
        "message": message,
    }
    return json.dumps(response)


def parse_message(raw_data: bytes) -> dict:
    return json.loads(raw_data.decode("utf-8"))