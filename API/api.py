import asyncio
import socket

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

HEADER: int = 64
CHAT_PORT: int = 5050
CHAT_SERVER = "192.168.100.102"
CHAT_ADDR = (CHAT_SERVER, CHAT_PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "DISCONNECT"
API_PORT = 8080

app = FastAPI()


def build_msg(text: str) -> bytes:
    msg = text.encode(FORMAT)
    header = str(len(msg)).encode(FORMAT).ljust(HEADER)
    return header + msg


async def recv_all(reader: asyncio.StreamReader, length: int) -> bytes | None:
    data = b""
    while len(data) < length:
        packet = await reader.read(length - len(data))
        if not packet:
            return None
        data += packet
    return data


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()

    try:
        reader, writer = await asyncio.open_connection(CHAT_ADDR)
    except ConnectionRefusedError:
        await ws.close(code=1011, reason="Chat server unreachable")
        return

    async def tcp_to_ws():
        try:
            while True:
                header = await recv_all(reader, HEADER)
                if not header:
                    break

                msg_length = int(header.decode(FORMAT).strip())

                msg = await recv_all(reader, msg_length)
                if not msg:
                    break

                await ws.send_text(msg.decode(FORMAT))

        except Exception:
            pass
        finally:
            await ws.close()

    tcp_task = asyncio.create_task(tcp_to_ws())

    try:
        while True:
            text = await ws.receive_text()
            writer.write(build_msg(text))
            await writer.drain()
    except WebSocketDisconnect:
        pass
    finally:
        tcp_task.cancel

        try:
            writer.write(build_msg(DISCONNECT_MESSAGE))
            await writer.drain()
            writer.close()
            await writer.wait_closed()

        except Exception:
            pass


if __name__ == "__main__":
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    print(f"[BRIDGE] Chat server expected at {CHAT_SERVER}:{CHAT_PORT}")
    print(f"[BRIDGE] Listening on http://{hostname}:{API_PORT}  ({ip})")

    uvicorn.run(app, host=ip, port=API_PORT)
