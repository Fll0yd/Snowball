from interface.text_interface import TextInterface

def main():
    """Main loop for interacting with the AI."""
    print("Starting AI Assistant...")
    text_interface = TextInterface()
    text_interface.interact()

if __name__ == "__main__":
    main()
