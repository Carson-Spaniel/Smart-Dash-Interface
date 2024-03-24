import can

PI = False

# Create a CAN bus interface using the python-can library
# Replace 'can0' with the actual CAN interface name for your system
if PI:
    channel = '/dev/rfcomm0' # Bluetooth port on pi
else:
    channel = 'COM5' # Bluetooth port on Laptop

bus = can.interface.Bus(bustype='serial', channel=channel, bitrate=500000)

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
