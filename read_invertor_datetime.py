import argparse
import json
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help="SAJ Inverter IP", type=str, required=True)
    parser.add_argument('--port', help="SAJ Inverter Port", type=int, required=True)
    args = parser.parse_args()

    address = 0x0137  # Starting register with current time on the inverter
    count = 4  # Read this amount of registers

    client = ModbusTcpClient(host=args.host, port=args.port, timeout=3)
    client.connect()

    try:
        inverter_data = client.read_holding_registers(slave=1, address=address, count=count)
        if inverter_data.isError():
            raise ConnectionException("Error reading registers")
    except ConnectionException as ex:
        print(f'Connecting to device {args.host} failed: {ex}')
        return
    finally:
        client.close()

    registers = inverter_data.registers
    year = registers[0]  # yyyy
    MMdd = registers[1]
    month = MMdd >> 8  # MM
    day = MMdd & 0xFF  # dd
    HHmm = registers[2]
    hour = HHmm >> 8  # HH
    minute = HHmm & 0xFF  # mm
    second = registers[3] >> 8  # ss

    timevalues = f"{year}{month:02}{day:02}{hour:02}{minute:02}{second:02}"
    data = {"datetime": timevalues}

    json_data = json.dumps(data)
    print(json_data)

if __name__ == "__main__":
    main()
