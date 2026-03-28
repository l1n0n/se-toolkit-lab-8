#!/usr/bin/env python3
import asyncio, json, websockets

async def main():
    uri = "ws://localhost:42002/ws/chat?access_key=my-secret-nanobot-key"
    async with websockets.connect(uri) as ws:
        # Ask about system health
        print("Asking about system health...")
        await ws.send(json.dumps({"content": "Any LMS backend errors in the last 2 minutes?"}))
        resp = await asyncio.wait_for(ws.recv(), timeout=30)
        print(f"Response: {resp}")

asyncio.run(main())
