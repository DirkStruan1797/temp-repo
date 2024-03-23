import argparse
import asyncio

import aiohttp
import requests

import CONSTS


def send_request(request: str, request_type, json_args=None):
    if not json_args:
        json_args = {}
    response = request_type(request, json_args)
    return response


async def start_game(pong_time_ms: int):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=f"http://localhost:{CONSTS.SERVER1_PORT}/start",
                                   params={"pong_time_ms": pong_time_ms,
                                           "second_server_port": CONSTS.SERVER2_PORT}) as response:
                response_text = await response.text()
                print(f"{response_text=}")
                # response = requests.get(url=f"http://localhost:{CONSTS.SERVER1_PORT}/start",
                #                         params={"pong_time_ms": pong_time_ms, "second_server_port": CONSTS.SERVER2_PORT}))
                if response.status == 200:
                    print("Game started successfully")
                else:
                    print("Error starting the game")
    except requests.exceptions.RequestException as e:
        print("Error:", e)


def pause_game():
    try:
        response_server_1 = requests.get(f'http://localhost:{CONSTS.SERVER1_PORT}/pause')
        response_server_2 = requests.get(f'http://localhost:{CONSTS.SERVER2_PORT}/pause')
        if response_server_1.status_code == 200 and response_server_2.status_code == 200:
            print("Game paused")
        else:
            print("Error pausing the game")
    except requests.exceptions.RequestException as e:
        print("Error:", e)


def resume_game():
    pass

def stop_game():
    pass


async def main():
    parser = argparse.ArgumentParser(description='Pong game CLI tool')
    subparsers = parser.add_subparsers(dest='command', help='Sub-command to control the game')

    start_parser = subparsers.add_parser('start', help='Start the game with specified pong time')
    start_parser.add_argument('pong_time_ms', type=int, help='Time interval between pongs')
    # start_parser.add_argument('second_server_port', type=int, help='Port to the second server')

    subparsers.add_parser('pause', help='Pause the game')
    subparsers.add_parser('resume', help='Resume the game')
    subparsers.add_parser('stop', help='Stop the game')

    args = parser.parse_args()

    if args.command == 'start':
        await start_game(args.pong_time_ms)
    elif args.command == 'pause':
        pause_game()
    elif args.command == 'resume':
        resume_game()
    elif args.command == 'stop':
        stop_game(args.port)

if __name__ == '__main__':
    asyncio.run(main())