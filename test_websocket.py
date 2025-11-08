import asyncio
import websockets
import json


async def test_websocket():
    try:
        print("Connecting to WebSocket...")
        async with websockets.connect("ws://localhost:8000/ws/vehicle / 0GRMKFDE61JNT8049") as websocket:
            print("Connected successfully!")

            # Wait for a message
            message = await websocket.recv()
            print(f"Received: {message}")

            # Parse and display the message
            try:
                data = json.loads(message)
                print(f"Parsed data: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Raw message: {message}")

    except Exception as e:
        print(f"WebSocket connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_websocket())
