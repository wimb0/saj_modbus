import argparse
import json
import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from typing import List, Optional, Dict

# Constants
ADDRESS = 0x8F00  # First register with Inverter details
COUNT = 29  # Number of registers to read

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_inverter_data(client: ModbusTcpClient, address: int, count: int) -> Optional[List[int]]:
    try:
        inverter_data = client.read_holding_registers(slave=1, address=address, count=count)
        if inverter_data.isError():
            raise ConnectionException("Error reading registers")
        return inverter_data.registers
    except ConnectionException as ex:
        logging.error(f'Connecting to device failed: {ex}')
        return None

def parse_registers(registers: List[int]) -> Dict[str, str]:
    def parse_string(registers_slice: List[int]) -> str:
        return ''.join(chr(registers_slice[i] >> 8) + chr(registers_slice[i] & 0xFF) for i in range(len(registers_slice))).rstrip('\x00')

    return {
        "devicetype": str(registers[0]),
        "subtype": str(registers[1]),
        "commver": str(round(registers[2] * 0.001, 3)),
        "serialnumber": parse_string(registers[3:13]),
        "productcode": parse_string(registers[13:23]),
        "dispswver": str(round(registers[23] * 0.001, 3)),
        "masterctrlver": str(round(registers[24] * 0.001, 3)),
        "slavectrlver": str(round(registers[25] * 0.001, 3)),
        "disphwver": str(round(registers[26] * 0.001, 3)),
        "ctrlhwver": str(round(registers[27] * 0.001, 3)),
        "powerhwver": str(round(registers[28] * 0.001, 3))
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help="SAJ Inverter IP", type=str, required=True)
    parser.add_argument('--port', help="SAJ Inverter Port", type=int, required=True)
    args = parser.parse_args()

    client = ModbusTcpClient(host=args.host, port=args.port, timeout=3)
    if not client.connect():
        logging.error(f'Failed to connect to {args.host}:{args.port}')
        return

    registers = read_inverter_data(client, ADDRESS, COUNT)
    client.close()

    if registers is not None:
        data = parse_registers(registers)
        json_data = json.dumps(data)
        print(json_data)

if __name__ == "__main__":
    main()
