import can
import time
import random

# Create a virtual CAN bus
bus = can.interface.Bus(bustype='virtual', channel='vcan0')
bus2 = can.interface.Bus(bustype='virtual', channel='vcan0')

# Start sending and receiving messages
try:
    while True:
        # Generate random data
        random_data = [random.randint(0, 255) for _ in range(8)]  # Generate 8 random bytes
        
        # Send a message with random data
        msg = can.Message(arbitration_id=random.randint(1,2e9), data=random_data)
        bus.send(msg)

        # Allow some time for the message to be sent
        time.sleep(1)

        # Check for received messages
        recv_msg = bus2.recv(timeout=0.1)
        if recv_msg:
            print("\n\n\nMessage received:", recv_msg)
            
            # Print received data as a bytearray
            print("\nReceived Data as bytearray:", recv_msg.data)
            
            # Convert received data to hex string
            hex_str = ' '.join(format(byte, '02x') for byte in recv_msg.data)
            print("Received Data as Hex String:", hex_str)
            
            # Convert received data to integer
            received_int = [int(byte) for byte in recv_msg.data]
            print("Received Data as Integer:", received_int)

except KeyboardInterrupt:
    # Stop the bus when the script is interrupted
    bus.shutdown()