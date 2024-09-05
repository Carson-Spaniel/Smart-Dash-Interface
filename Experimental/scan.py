import can
import logging
import time

# Set up logging to log to a file
logging.basicConfig(filename='can.log', level=logging.INFO, format='%(message)s')

CAN_INTERFACE = 'vcan0'  # Set your CAN interface here

def main():
    try:
        # Create a CAN bus instance
        bus = can.interface.Bus(channel=CAN_INTERFACE, interface='socketcan')

        # Variables for timestamp and timing calculations
        timestamps = []
        message_count = 20

        # Read CAN messages in a loop
        while len(timestamps) < message_count:
            # Wait for a message
            message = bus.recv(timeout=0.01)  # Timeout to avoid blocking indefinitely

            if message is not None:
                if message.arbitration_id > 0:
                    # Record the timestamp
                    now = time.time()
                    timestamps.append(now)

                    # Print and log the message
                    log_message = f"CAN ID: 0x{message.arbitration_id:x} DLC: {message.dlc} Data: {message.data.hex()}"
                    print(log_message)
                    logging.info(log_message)

        # Compute average time between messages
        if len(timestamps) == message_count:
            time_diffs = [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))]
            average_time = sum(time_diffs) / len(time_diffs)
            print(f"Average time between messages: {average_time:.6f} seconds")

    except KeyboardInterrupt:
        print("Program interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up on exit
        print("Exiting program")

if __name__ == "__main__":
    main()
