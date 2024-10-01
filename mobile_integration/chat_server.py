import asyncio
import websockets
import json
import os

# Path to the messages.json file
messages_file_path = "S:/cloud_sync/mobile_sync/messages.json"

# Import Snowball AI core components
from core.ai_agent import SnowballAI

# Create an instance of the Snowball AI agent
snowball_ai = SnowballAI()

# Function to load existing messages from messages.json
def load_messages():
    if os.path.exists(messages_file_path):
        try:
            with open(messages_file_path, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {"messages": []}  # Initialize if JSON is invalid or corrupted
    return {"messages": []}

# Function to save messages to messages.json
def save_message(user_message, ai_response):
    # Load the current messages
    messages_data = load_messages()

    # Append the new message and AI response
    messages_data["messages"].append({
        "user_message": user_message,
        "ai_response": ai_response
    })

    # Write back to messages.json
    with open(messages_file_path, 'w') as file:
        json.dump(messages_data, file, indent=4)

# WebSocket server handler
async def handle_message(websocket, path):
    async for message in websocket:
        print(f"Received message from mobile: {message}")

        # Parse message and process it
        try:
            data = json.loads(message)
            user_message = data.get('message', '')

            # Check if it's a game command or a normal chat
            if "play" in user_message.lower():
                response = f"Starting {user_message.split('play')[-1].strip()} game."
                if "snake" in user_message.lower():
                    response = "Starting Snake AI game."
                    # Add game logic for Snake AI here (optional)
            else:
                # Process the message with Snowball AI
                response = snowball_ai.process_input(user_message)

            # Save the interaction to messages.json
            save_message(user_message, response)

            # Send back Snowball AI's response to the mobile app
            await websocket.send(json.dumps({"response": response}))

        except Exception as e:
            await websocket.send(json.dumps({"error": str(e)}))
            print(f"Error: {e}")

# Start WebSocket server
async def start_server():
    server = await websockets.serve(handle_message, "localhost", 8765)
    print("WebSocket server started on ws://localhost:8765")
    await server.wait_closed()

# Main entry point for the server
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_server())
    asyncio.get_event_loop().run_forever()
