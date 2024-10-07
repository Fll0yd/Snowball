class SnowballHandler:
    def process_input(self, message):
        print(f"Received message from Minecraft: {message}")
        
        # Basic AI response logic for now
        if "generate grass" in message.lower():
            return "Generating grass terrain..."
        elif "build house" in message.lower():
            return "Building house..."
        else:
            return "I don't understand that command yet!"
