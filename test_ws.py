#!/usr/bin/env python3
import asyncio
import json
import websockets

async def main():
    uri = "ws://localhost:42002/ws/chat?access_key=my-secret-nanobot-key"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"content": "Show me the scores"}))
        response = await ws.recv()
        print(response)

asyncio.run(main())
