from fastapi import FastAPI
from multiprocessing import Process
import aiohttp
import uvicorn
import asyncio
import CONSTS


# TODO: All messages should be saved in a consts file
class Server:
    def __init__(self, port: int):
        self.app = None
        self.port = port
        self.is_running = False

    def run(self):
        self.app = FastAPI()
        self.define_routes()
        uvicorn.run(self.app, host=CONSTS.HOST, port=self.port)  # TODO: Put host and port numbers in const files

    async def start_game(self, pong_time_ms: int, second_server_port: int):
        if self.is_running:
            pass
        self.is_running = True
        print(
            f"Server at port {self.port} started pong game with server at port {second_server_port}, and pong time {pong_time_ms} ms")
        await self.send_ping_to_second_server(second_server_port, pong_time_ms)
        # return {"message": "Game Started"}

    async def send_ping_to_second_server(self, second_server_port, pong_time_ms):
        print(f"Sending ping to other server (from {self.port} to {second_server_port})")
        async with aiohttp.ClientSession() as session:
            async with session.get(url=f"http://localhost:{second_server_port}/ping",
                                   params={"sender_port": self.port, "pong_time_ms": pong_time_ms}) as response:
                response_text = await response.text()
                print(
                    f"Server {self.port} sent ping to server {second_server_port}, received response: {response_text}")
        # return response.text()

    async def handle_ping_request(self, sender_port, pong_time_ms):
        print(f"Server {self.port} has received ping from server {sender_port}")

        sleep_time = pong_time_ms / 1000
        await asyncio.sleep(sleep_time)

        answer = await self.send_ping_to_second_server(second_server_port=sender_port, pong_time_ms=pong_time_ms)
        return answer

    async def pause_game(self):
        print(f"{self.is_running=}")
        if not self.is_running:
            return {"message": "Game isn't currently running"}
        self.is_running = False
        return {"message": "Game Paused"}

    async def resume_game(self):
        if self.is_running:
            return {"message": "Game already running"}
        if not self.pong_time_ms:
            return {"message": "Game not started yet"}

        self.is_running = True
        return {"message": "Game resumed"}

    async def stop_game(self):
        self.is_running = False
        return {"message": "Game stopped"}

    # TODO: Change all endpoints to return the value from the server methods
    def define_routes(self):
        @self.app.get("/start")
        async def start_endpoint(pong_time_ms: int, second_server_port: int):
            await self.start_game(pong_time_ms=pong_time_ms, second_server_port=second_server_port)
            return {"message": "Game Started"}

        @self.app.get("/pause")
        async def pause_endpoint():
            print("PAUSING")
            return self.pause_game()

        @self.app.get("/resume")
        async def resume_endpoint():
            return self.resume_game()

        @self.app.get("/stop")
        async def stop_endpoint():
            return self.stop_game()

        @self.app.get("/ping")
        async def handle_ping(sender_port: int, pong_time_ms: int):
            return await self.handle_ping_request(sender_port, pong_time_ms)


def start_servers():
    server1 = Server(CONSTS.SERVER1_PORT)
    server2 = Server(CONSTS.SERVER2_PORT)

    server1_process = Process(target=server1.run)
    server2_process = Process(target=server2.run)

    server1_process.start()
    server2_process.start()

    server1_process.join()
    server2_process.join()


if __name__ == "__main__":
    start_servers()

