import obd
import time
import json


status_commands = {"DTC_FUEL_STATUS", "STATUS", "STATUS_DRIVE_CYCLE", "DTC_STATUS", "DTC_STATUS_DRIVE_CYCLE"}#, "FUEL_STATUS"
tuple_commands = {"FREEZE_DTC"}

def main():
    connection = obd.OBD(portstr="/dev/ttyACM0")
    f = open('obd-data.json', 'w')
#   while True:
    line = json.dumps(read(connection))
    f.write(line + "\n")
    f.flush()
# time.sleep(10)


def read(connection):
  line = {"time": time.strftime("%m/%d/%Y %H:%M:00", time.localtime())}
  for cmd in connection.supported_commands:
    name = cmd.name
    response = connection.query(cmd)
    value = response.value
    if name in status_commands and value is not None:
      line[name+".MIL"] = value.MIL
      line[name+".DTC_count"] = value.DTC_count
      line[name+".ignition_type"] = value.ignition_type
    elif name in tuple_commands and value is not None:
      line[name+".code"] = value[0]
      line[name+".description"] = value[1]
    elif hasattr(value, 'magnitude'):
      line[name] = value.magnitude
    else:
      line[name] = str(value)
  return line


if __name__ == "__main__":
  main()
