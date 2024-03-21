import can

# Create a CAN bus interface using the python-can library
# Replace 'can0' with the actual CAN interface name for your system
bus = can.interface.Bus(bustype='serial', channel='/dev/rfcomm0', bitrate=500000)

try:
    print("CAN Bus connected")

    # Define a message listener
    def print_message(msg):
        print("Received message:", msg)

    # Add the listener to receive messages
    notifier = can.Notifier(bus, [print_message])

    # Keep the script running
    while True:
        pass

except KeyboardInterrupt:
    # Stop the script when Ctrl+C is pressed
    print("Interrupted by user")

finally:
    bus.shutdown()
    print("CAN Bus disconnected")



# import can

# # Function to send OBD-II PID request and receive response
# def get_obd_data(bus, mode, pid):
#     request = can.Message(arbitration_id=0x7DF, data=[2, mode, pid, 0, 0, 0, 0, 0], extended_id=False)
#     bus.send(request)

#     response = bus.recv()
#     if response is not None and response.arbitration_id == 0x7E8:
#         data = response.data
#         # Formula to calculate RPM: ((A*256)+B)/4
#         rpm = ((data[3] * 256) + data[4]) / 4
#         return rpm
#     else:
#         return None

# # Create a CAN bus interface
# bus = can.interface.Bus(bustype='serial', channel='/dev/rfcomm0', bitrate=500000)

# try:
#     print("CAN Bus connected")

#     while True:
#         # Send OBD-II request for RPM (PID 0x0C)
#         rpm = get_obd_data(bus, 0x01, 0x0C)
#         if rpm is not None:
#             print("RPM:", rpm)
#         else:
#             print("RPM data not available")

# except KeyboardInterrupt:
#     # Stop the script when Ctrl+C is pressed
#     print("Interrupted by user")

# finally:
#     bus.shutdown()
#     print("CAN Bus disconnected")
