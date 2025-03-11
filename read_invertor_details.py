import argparse
import json
import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Constants
ADDRESS = 36608  # First register with Inverter details
COUNT = 29  # Number of registers to read

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_inverter_data(client, address, count):
    try:
        inverter_data = client.read_holding_registers(slave=1, address=address, count=count)
        if inverter_data.isError():
            raise ConnectionException("Error reading registers")
        return inverter_data.registers
    except ConnectionException as ex:
        logging.error(f'Connecting to device failed: {ex}')
        return None

def parse_registers(registers):
    return {
        "devicetype": str(registers[0]),
        "subtype": str(registers[1]),
        "commver": str(round(registers[2] * 0.001, 3)),
        "serialnumber": ''.join(chr(registers[i] >> 8) + chr(registers[i] & 0xFF) for i in range(3, 13)).rstrip('\x00'),
        "productcode": ''.join(chr(registers[i] >> 8) + chr(registers[i] & 0xFF) for i in range(13, 23)).rstrip('\x00'),
        "dispswver": str(round(registers[23] * 0.001, 3)),
        "masterctrlver": str(round(registers[24] * 0.001, 3)),
        "slavectrlver": str(round(registers[25] * 0.001, 3)),
        "disphwver": str(round(registers[26] * 0.001, 3)),
        "ctrlhwver": str(round(registers[27] * 0.001, 3)),
        "powerhwver": str(round(registers[28] * 0.001, 3))
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help="SAJ Inverter IP", type=str, required=True)
    parser.add_argument('--port', help="SAJ Inverter Port", type=int, required=True)
    args = parser.parse_args()

    client = ModbusTcpClient(host=args.host, port=args.port, timeout=3)
    client.connect()

    registers = read_inverter_data(client, ADDRESS, COUNT)
    client.close()

    if registers is not None:
        data = parse_registers(registers)
        json_data = json.dumps(data)
        print(json_data)

if __name__ == "__main__":
    main()
