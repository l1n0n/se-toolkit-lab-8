#!/usr/bin/env python3
import asyncio, json, websockets

async def main():
    uri = "ws://localhost:42002/ws/chat?access_key=my-secret-nanobot-key"
    async with websockets.connect(uri) as ws:
        # First trigger a request that will fail
        print("Triggering request...")
        await ws.send(json.dumps({"content": "What labs are available?"}))
        resp = await ws.recv()
        print(f"Response 1: {resp[:200]}...")
        
        # Then ask what went wrong
        print("\nAsking 'What went wrong?'...")
        await ws.send(json.dumps({"content": "What went wrong?"}))
        
        # Get responses
        for i in range(5):
            try:
                resp = await asyncio.wait_for(ws.recv(), timeout=30)
                print(f"Response: {resp[:500]}...")
            except asyncio.TimeoutError:
                break

asyncio.run(main())
