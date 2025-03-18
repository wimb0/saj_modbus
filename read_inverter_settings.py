import argparse
import json
import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from typing import List, Optional, Dict

# Constants
ADDRESS = 0x1008  # First register with Inverter details
COUNT = 64  # Number of registers to read

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_to_signed(value):
    """Convert unsigned integers to signed integers."""
    if value >= 0x8000:
        return value - 0x10000
    else:
        return value
        
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

    return {
        "SafetyType": registers[0],
        "FunMask": registers[1],
        "ISOLimit": registers[11],
        "PowerLimited": round(convert_to_signed(registers[20]) * 0.001, 3),
        "ReactiveMode": registers[21],
        "ReactiveValue": round(convert_to_signed(registers[22]) * 0.001, 3),
        "PowerAdjCoff3": registers[41],
        "PVInputMode": registers[56]
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
