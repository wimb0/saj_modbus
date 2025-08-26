import argparse
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from typing import Optional

# --- Configuration ---
POWER_ADDRESS = 0x1037
SLAVE_ID = 1

def get_current_power_value(client: ModbusTcpClient) -> Optional[int]:
    """
    Silently reads the power register and returns its raw integer value (0 or 1).
    Returns None if there is an error.
    """
    try:
        response = client.read_holding_registers(address=POWER_ADDRESS, count=1, slave=SLAVE_ID)
        if response.isError():
            print(f"Error: Failed to read current state: {response}")
            return None
        return response.registers[0]
    except ConnectionException as ex:
        print(f"Error: Connection error while reading current state: {ex}")
        return None

def write_power_command(client: ModbusTcpClient, value: int):
    """
    Writes the on/off command to the inverter using Function Code 0x10.
    """
    try:
        print(f"Sending command to turn inverter {'ON' if value == 1 else 'OFF'}...")
        response = client.write_registers(address=POWER_ADDRESS, values=[value], slave=SLAVE_ID)

        if response.isError():
            print(f"Error: Write command failed. The inverter responded with: {response}")
            return

        print("Successfully sent the command.")

    except ConnectionException as ex:
        print(f"Error: A connection error or timeout occurred during write: {ex}")

def main():
    parser = argparse.ArgumentParser(
        description="A tool to read or control the power state of a SAJ R5 Inverter.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--read', action='store_true', help="Read the current on/off state of the inverter.")
    parser.add_argument('--write', type=str, choices=['on', 'off', '1', '0'], help="Set the inverter state to 'on' or 'off'.")
    parser.add_argument('--host', help="Inverter IP Address", type=str, required=True)
    parser.add_argument('--port', help="Modbus Port", type=int, required=True)
    
    args = parser.parse_args()

    if not args.read and not args.write:
        parser.print_help()
        return

    try:
        with ModbusTcpClient(host=args.host, port=args.port, timeout=5) as client:
            if not client.connect():
                print(f"Error: Could not connect to {args.host}:{args.port}")
                return

            if args.read:
                value = get_current_power_value(client)
                if value is not None:
                    state = "ON" if value == 1 else "OFF"
                    print(f"The inverter is currently {state}.")
                else:
                    print("Could not retrieve the current state of the inverter.")

            elif args.write:
                value_to_write = 1 if args.write.lower() in ['on', '1'] else 0
                action_str = "ON" if value_to_write == 1 else "OFF"

                current_value = get_current_power_value(client)
                
                if current_value is None:
                    print("Error: Could not verify current state. Aborting write operation.")
                    return
                
                if current_value == value_to_write:
                    print(f"No action needed. Inverter is already {action_str}.")
                    return

                current_state_str = "ON" if current_value == 1 else "OFF"
                print(f"\nINFO: The inverter is currently {current_state_str}.")
                print(f"WARNING: You are about to turn the inverter {action_str}.")
                confirm = input("Are you sure you want to continue? (yes/no): ")
                
                if confirm.lower() in ['yes', 'y']:
                    write_power_command(client, value_to_write)
                else:
                    print("Operation cancelled.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
