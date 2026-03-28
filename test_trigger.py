#!/usr/bin/env python3
import asyncio, json, websockets

async def main():
    uri = "ws://localhost:42002/ws/chat?access_key=my-secret-nanobot-key"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"content": "What labs are available?"}))
        await ws.recv()
    print("Request triggered")

asyncio.run(main())
