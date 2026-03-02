import asyncio
import socket
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

TCP_HOST = "127.0.0.1"      
TCP_PORT = 5050             
HEADER = 64                 
FORMAT = "utf-8"            
DISCONNECT_MESSAGE = "DISCONNECT"   

app = FastAPI()

