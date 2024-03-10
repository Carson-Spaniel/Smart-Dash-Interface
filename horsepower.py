import obd
import time
import csv
import matplotlib.pyplot as plt
import random

def calculate_horsepower(torque, rpm):
    return (torque * rpm) / 5252

# Connect to the OBD-II adapter
connection = obd.OBD()

# Print a message indicating connection
# if connection.is_connected():
#     print("Connected to OBD-II adapter. Ready to log data.")
# else:
#     print("Could not connect to OBD-II adapter. Exiting...")
#     exit()

# Prepare lists to store data
horsepower_data = []
rpm_data = []
torque_data = []
time_data = []
start_time = time.time()

# Prepare CSV file for writing
csv_filename = "logged_data.csv"
csv_file = open(csv_filename, mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Time (s)', 'RPM', 'Torque', 'Horsepower'])

# Wait for user to press SPACE to start logging
logging = False
print("Press ENTER to start logging data...")
while True:
    user_input = input()
    if user_input == '':
        logging = True
        start_time = time.time()  # Reset start time when logging starts
        print("Logging started...")
        break
    else:
        print("Invalid input. Press ENTER to start logging...")

rpm = 1000
torque = 100

while logging:
    # Query for RPM and Torque
    # cmd_rpm = obd.commands.RPM
    # cmd_torque = obd.commands.ENGINE_LOAD  # Torque can be estimated from ENGINE_LOAD
    # response_rpm = connection.query(cmd_rpm)
    # response_torque = connection.query(cmd_torque)

    # if not response_rpm.is_null() and not response_torque.is_null():
    rpm = random.randint(max(rpm-1000,600), min(rpm+1000,9000))  # response_rpm.value.magnitude
    torque = random.randint(max(torque-50,100), min(torque+50,450))  # response_torque.value.magnitude
    horsepower = calculate_horsepower(torque, rpm)

    # Append data to lists
    current_time = time.time() - start_time
    horsepower_data.append(horsepower)
    rpm_data.append(rpm)
    torque_data.append(torque)
    time_data.append(current_time)

    # Write data to CSV
    csv_writer.writerow([current_time, rpm, torque, horsepower])
    csv_file.flush()  # Ensure data is written to disk

    print("\n\tTime:", current_time)
    print("\tRPM:", rpm)
    print("\tTorque:", torque)
    print("\tHorsepower:", horsepower)

    # Check stop conditions
    if rpm < 1500 and current_time > 10:
        logging = False

    time.sleep(.1)  # Wait for 1 second before next iteration

print("Logging stopped.")

# Calculate and print max horsepower
max_horsepower = max(horsepower_data)
max_horsepower_index = horsepower_data.index(max_horsepower)
max_horsepower_time = time_data[max_horsepower_index]
print(f'\nMax horsepower: {round(max_horsepower,2)} at {round(max_horsepower_time,2)} seconds')

# Close CSV file
csv_file.close()

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(time_data, horsepower_data, label='Horsepower')
plt.plot(time_data, rpm_data, label='RPM')
plt.plot(time_data, torque_data, label='Torque')
plt.xlabel('Time (s)')
plt.ylabel('Value')
plt.title('Logged Data')
plt.legend()
plt.grid(True)
plt.show()

# Close the connection
connection.close()
