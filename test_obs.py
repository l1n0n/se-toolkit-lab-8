#!/usr/bin/env python3
import asyncio, json, websockets

async def main():
    uri = "ws://localhost:42002/ws/chat?access_key=my-secret-nanobot-key"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"content": "Any LMS backend errors in the last 10 minutes?"}))
        while True:
            response = await ws.recv()
            print(response)

asyncio.run(main())
