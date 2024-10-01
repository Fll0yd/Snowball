class TextInterface:
    def __init__(self):
        pass

    def receive_input(self, text):
        """
        Receives text input from the user.
        """
        print(f"User: {text}")

    def send_response(self, response):
        """
        Sends a text response back to the user.
        """
        print(f"AI: {response}")
