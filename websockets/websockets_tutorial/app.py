#!/usr/bin/env python

import asyncio

import websockets
import json

import itertools
from connect4 import PLAYER1, PLAYER2, Connect4


async def handler(websocket):
    # original way
    # while True:
    #     try:
    #         message = await websocket.recv()
    #     except websockets.exceptions.ConnectionClosedOK:
    #         break
    #     print(message)

    # fancy way of waiting to print messages? Sets off a type error in the `websockets.serve(handler,...)` call below...
    # async for message in websocket:
    #     print(message)

    # Testing moves
    # for player, column, row in [
    #     (PLAYER1, 3, 0),
    #     (PLAYER2, 3, 1),
    #     (PLAYER1, 4, 0),
    #     (PLAYER2, 4, 1),
    #     (PLAYER1, 2, 0),
    #     (PLAYER2, 1, 0),
    #     (PLAYER1, 5, 0),
    # ]:
    #     event = {
    #         "type": "play",
    #         "player": player,
    #         "column": column,
    #         "row": row,
    #     }
    #     await websocket.send(json.dumps(event))
    #     await asyncio.sleep(0.5)
    # event = {
    #     "type": "win",
    #     "player": PLAYER1,
    # }
    # await websocket.send(json.dumps(event))

    # Actual game logic
    # Initialize a Connect Four game.
    game = Connect4()

    # Players take alternate turns, using the same browser.
    turns = itertools.cycle([PLAYER1, PLAYER2])
    player = next(turns)

    while True:
        try:
            message = await websocket.recv()
            message_dict = json.loads(message)
            if message_dict["type"] == "play":
                column = message_dict["column"]
                row = game.top[column]
                try:
                    game.play(player, column)
                except RuntimeError as exc:
                    # Send an "error" event if the move was illegal.
                    event = {
                        "type": "error",
                        "message": str(exc),
                    }
                    await websocket.send(json.dumps(event))
                    continue

                event = {
                    "type": "play",
                    "player": player,
                    "column": column,
                    "row": row,
                }
                await websocket.send(json.dumps(event))
            if game.last_player_won:
                event = {
                    "type": "win",
                    "player": player,
                }
                await websocket.send(json.dumps(event))

            player = next(turns)

        except websockets.exceptions.ConnectionClosedOK:
            break
        print(message)


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
