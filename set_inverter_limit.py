import argparse
import json
import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# --- Configuration ---
LIMIT_ADDRESS = 0x101C
SLAVE_ID = 1

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_limit_state(client: ModbusTcpClient):
    """
    Reads the power limit register and prints its current status as JSON.
    """
    try:
        logging.info(f"Reading limit state from register {hex(LIMIT_ADDRESS)}...")
        response = client.read_holding_registers(address=LIMIT_ADDRESS, count=1, slave=SLAVE_ID)

        if response.isError():
            logging.error(f"Failed to read register. The inverter responded with an error: {response}")
            return

        value = response.registers[0]

        status = {
            "register": hex(LIMIT_ADDRESS),
            "rawValue": value
        }

        print(json.dumps(status, indent=4))

    except ConnectionException as ex:
        logging.error(f"A connection error or timeout occurred during read: {ex}")

def write_limit_command(client: ModbusTcpClient, value: int):
    """
    Writes the limit command to the inverter using Function Code 0x10.
    """
    limitval = value * 10
    try:
        logging.info(f"Sending command '{value}' to register {hex(LIMIT_ADDRESS)} using Function Code 0x10...")

        response = client.write_registers(address=LIMIT_ADDRESS, values=[limitval], slave=SLAVE_ID)

        if response.isError():
            logging.error(f"Write command failed. The inverter responded with an error: {response}")
            return

        logging.info(f"Successfully wrote value '{limitval}' ('{value}') to address {hex(LIMIT_ADDRESS)}.")

    except ConnectionException as ex:
        logging.error(f"A connection error or timeout occurred during write: {ex}")

def main():
    parser = argparse.ArgumentParser(
        description="Read or write the power limit of a SAJ R5 Inverter.",
        epilog="To read the current state, run without --write. To change the state, use --write {percentage}."
    )
    parser.add_argument('--host', help="Inverter IP Address", type=str, required=True)
    parser.add_argument('--port', help="Modbus Port", type=int, required=True)
    parser.add_argument('--write', help="Optional: Percentage 0 - 110 to set power limit", type=int, choices=range(0,111), default=)
    args = parser.parse_args()

    try:
        with ModbusTcpClient(host=args.host, port=args.port, timeout=5) as client:
            logging.info(f"Connecting to {args.host}:{args.port}...")

            if args.write is not None:
                write_limit_command(client, args.write)
            else:
                read_limit_state(client)

    except Exception as e:
        logging.error(f"Failed to connect or execute command. Error: {e}")

if __name__ == "__main__":
    main()
