from py4j.java_gateway import JavaGateway
from SnowballHandler import SnowballHandler

if __name__ == "__main__":
    gateway = JavaGateway()  # Connect to the Java side (Minecraft mod)
    snowball_handler = SnowballHandler()

    gateway.entry_point = snowball_handler  # Expose Snowball to Java
    print("Snowball AI is ready and listening for commands...")
