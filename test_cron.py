#!/usr/bin/env python3
import asyncio, json, websockets

async def main():
    uri = "ws://localhost:42002/ws/chat?access_key=my-secret-nanobot-key"
    async with websockets.connect(uri) as ws:
        # Create health check
        print("Creating health check...")
        await ws.send(json.dumps({
            "content": "Create a health check for this chat that runs every 2 minutes using your cron tool. Each run should check for LMS/backend errors in the last 2 minutes, inspect a trace if needed, and post a short summary here. If there are no recent errors, say the system looks healthy."
        }))
        for i in range(3):
            resp = await asyncio.wait_for(ws.recv(), timeout=30)
            print(f"Response: {resp[:300]}...")
        
        # List jobs
        print("\n\nListing scheduled jobs...")
        await ws.send(json.dumps({"content": "List scheduled jobs."}))
        for i in range(2):
            resp = await asyncio.wait_for(ws.recv(), timeout=30)
            print(f"Response: {resp[:300]}...")

asyncio.run(main())

''''''