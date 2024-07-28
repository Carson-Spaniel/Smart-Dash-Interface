import datetime

# Function to read and parse timestamps from the file
def read_timestamps(file_path):
    with open(file_path, "r") as file:
        times = file.readlines()

    # Filter out any empty lines
    times = [line.strip() for line in times if line.strip()]

    # Convert string timestamps to datetime objects
    timestamps = []
    for time in times:
        try:
            timestamps.append(datetime.datetime.fromisoformat(time))
        except ValueError as e:
            print(f"Error parsing time '{time}': {e}")
    
    return timestamps

# Function to calculate the average interval between timestamps
def calculate_average_interval(timestamps):
    # Calculate the time differences
    intervals = []
    for i in range(1, len(timestamps)):
        interval = (timestamps[i] - timestamps[i - 1]).total_seconds()
        intervals.append(interval)

    # Sort intervals and exclude the 5 highest and 5 lowest
    intervals.sort()
    trimmed_intervals = intervals[5:-5]

    # Calculate the average interval of the trimmed list
    if trimmed_intervals:
        average_interval = sum(trimmed_intervals) / len(trimmed_intervals)
        return average_interval
    else:
        return None

# Main function to run the program
def main():
    file_path = "Data/time.txt"
    timestamps = read_timestamps(file_path)

    if timestamps:
        average_interval = calculate_average_interval(timestamps)
        if average_interval is not None:
            print(f"Average interval between times (excluding outliers): {average_interval:.6f} seconds")
        else:
            print("Not enough timestamps to calculate intervals after removing outliers.")
    else:
        print("No valid timestamps found in the file.")

if __name__ == "__main__":
    main()
