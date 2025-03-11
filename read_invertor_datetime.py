import argparse
import json
import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help="SAJ Inverter IP", type=str, required=True)
    parser.add_argument('--port', help="SAJ Inverter Port", type=int, required=True)
    args = parser.parse_args()

    address = 0x0137  # Starting register with current time on the inverter
    count = 4  # Number of registers to read

    data = {"datetime": None}

    try:
        with ModbusTcpClient(host=args.host, port=args.port, timeout=3) as client:
            # Connect to the inverter
            if not client.connect():
                raise ConnectionException(f"Unable to connect to {args.host}:{args.port}")

            # Read holding registers
            inverter_data = client.read_holding_registers(slave=1, address=address, count=count)
            if inverter_data.isError():
                raise ConnectionException("Error reading registers")

            # Extract date and time values from registers
            registers = inverter_data.registers
            year = registers[0]  # yyyy
            month = registers[1] >> 8  # MM
            day = registers[1] & 0xFF  # dd
            hour = registers[2] >> 8  # HH
            minute = registers[2] & 0xFF  # mm
            second = registers[3] >> 8  # ss

            # Format the extracted date and time values
            timevalues = f"{year}{month:02}{day:02}{hour:02}{minute:02}{second:02}"
            data["datetime"] = timevalues

    except ConnectionException as ex:
        logger.error(f"Connecting to device {args.host} failed: {ex}")

    finally:
        # Convert data to JSON and print
        json_data = json.dumps(data)
        logger.info(json_data)
        print(json_data)

if __name__ == "__main__":
    main()
