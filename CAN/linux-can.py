import can

# Create a CAN bus interface using the python-can library
# Replace 'can0' with the actual CAN interface name for your system
channel = 'can0'

bus = can.interface.Bus(channel=channel, bustype='socketcan')

try:
    print("CAN Bus connected")

    while True:
        recv_msg = bus.recv(timeout=0.1)
        if recv_msg:
            print("\n\n\nMessage received:", recv_msg)

except KeyboardInterrupt:
    # Stop the script when Ctrl+C is pressed
    print("Interrupted by user")

finally:
    bus.shutdown()
    print("CAN Bus disconnected")
