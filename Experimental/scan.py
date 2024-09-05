import can
import logging

# Set up logging to log to a file
logging.basicConfig(filename='can.log', level=logging.INFO, format='%(message)s')

CAN_INTERFACE = 'vcan0'  # Set your CAN interface here

def decode_can_frame(frame):
    can_id = frame.arbitration_id
    data = frame.data

    if can_id == 0x123:  # Example CAN ID
        # Assuming data format: [speed (2 bytes), rpm (2 bytes)]
        speed = (data[0] << 8) | data[1]
        rpm = (data[2] << 8) | data[3]
        print(f"Speed: {speed} km/h, RPM: {rpm}")
        return f"Speed: {speed} km/h, RPM: {rpm}"
    elif can_id == 0x456:  # Another CAN ID
        # Decode another type of message
        temperature = data[0]  # Assuming temperature in first byte
        print(f"Temperature: {temperature} °C")
        return f"Temperature: {temperature} °C"
    else:
        # Handle other CAN IDs
        return None

def main():
    try:
        # Create a CAN bus instance
        bus = can.interface.Bus(channel=CAN_INTERFACE, interface='socketcan')

        # Read CAN messages in a loop
        while True:
            # Wait for a message
            message = bus.recv()

            if message is not None:
                if message.arbitration_id > 0:
                    # Print and log the message
                    log_message = f"CAN ID: 0x{message.arbitration_id:x} DLC: {message.dlc} Data: {message.data.hex()}"
                    print(log_message)
                    logging.info(log_message)

    except KeyboardInterrupt:
        print("Program interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up on exit
        print("Exiting program")

if __name__ == "__main__":
    main()
