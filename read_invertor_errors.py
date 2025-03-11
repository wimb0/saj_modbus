import argparse
import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FAULT_MESSAGES = {
    0: {
        0x80000000: "Code 81: Lost Communication D<->C",
        0x00080000: "Code 48: Master Fan4 Error",
        0x00040000: "Code 47: Master Fan3 Error",
        0x00020000: "Code 46: Master Fan2 Error",
        0x00010000: "Code 45: Master Fan1 Error",
        0x00002000: "Code 43: Master HW Phase3 Current High",
        0x00001000: "Code 42: Master HW Phase2 Current High",
        0x00000800: "Code 41: Master HW Phase1 Current High",
        0x00000400: "Code 40: Master HWPV2 Current High",
        0x00000200: "Code 39: Master HWPV1 Current High",
        0x00000100: "Code 38: Master HWBus Voltage High",
        0x00000010: "Code 37: Master Phase3 Current High",
        0x00000008: "Code 36: Master Phase2 Current High",
        0x00000004: "Code 35: Master Phase1 Current High",
        0x00000002: "Code 34: Master Bus Voltage Low",
        0x00000001: "Code 33: Master Bus Voltage High",
    },
    1: {
        0x80000000: "Code 32: Master Bus Voltage Balance Error",
        0x40000000: "Code 31: Master ISO Error",
        0x20000000: "Code 30: Master Phase3 DCI Error",
        0x10000000: "Code 29: Master Phase2 DCI Error",
        0x08000000: "Code 28: Master Phase1 DCI Error",
        0x04000000: "Code 27: Master GFCI Error",
        0x02000000: "Code 26: Master Phase3 No Grid Error",
        0x01000000: "Code 25: Master Phase2 No Grid Error",
        0x00800000: "Code 24: Master Phase1 No Grid Error",
        0x00400000: "Code 23: Master Phase3 Frequency Low",
        0x00200000: "Code 22: Master Phase3 Frequency High",
        0x00100000: "Code 21: Master Phase2 Frequency Low",
        0x00080000: "Code 20: Master Phase2 Frequency High",
        0x00040000: "Code 19: Master Phase1 Frequency Low",
        0x00020000: "Code 18: Master Phase1 Frequency High",
        0x00010000: "Code 17: Master Phase3 Voltage 10Min High",
        0x00008000: "Code 16: Master Phase2 Voltage 10Min High",
        0x00004000: "Code 15: Master Phase1 Voltage 10Min High",
        0x00002000: "Code 14: Master Phase3 Voltage Low",
        0x00001000: "Code 13: Master Phase3 Voltage High",
        0x00000800: "Code 12: Master Phase2 Voltage Low",
        0x00000400: "Code 11: Master Phase2 Voltage High",
        0x00000200: "Code 10: Master Phase1 Voltage Low",
        0x00000100: "Code 09: Master Phase1 Voltage High",
        0x00000080: "Code 08: Master Current Sensor Error",
        0x00000040: "Code 07: Master DCI Device Error",
        0x00000020: "Code 06: Master GFCI Device Error",
        0x00000010: "Code 05: Master Lost Communication M<->S",
        0x00000008: "Code 04: Master Temperature Low Error",
        0x00000004: "Code 03: Master Temperature High Error",
        0x00000002: "Code 02: Master EEPROM Error",
        0x00000001: "Code 01: Master Relay Error",
    },
    2: {
        0x40000000: "Code 80: Slave PV Voltage High Error",
        0x20000000: "Code 79: Slave PV2 Current High Error",
        0x10000000: "Code 78: Slave PV1 Current High Error",
        0x08000000: "Code 77: Slave PV2 Voltage High Error",
        0x04000000: "Code 76: Slave PV1 Voltage High Error",
        0x02000000: "Code 75: Slave Phase3 No Grid Error",
        0x01000000: "Code 74: Slave Phase2 No Grid Error",
        0x00800000: "Code 73: Slave Phase1 No Grid Error",
        0x00400000: "Code 72: Slave Phase3 Frequency Low",
        0x00200000: "Code 71: Slave Phase3 Frequency High",
        0x00100000: "Code 70: Slave Phase2 Frequency Low",
        0x00080000: "Code 69: Slave Phase2 Frequency High",
        0x00040000: "Code 68: Slave Phase1 Frequency Low",
        0x00020000: "Code 67: Slave Phase1 Frequency High",
        0x00010000: "Code 66: Slave Phase3 Voltage Low",
        0x00008000: "Code 65: Slave Phase3 Voltage High",
        0x00004000: "Code 64: Slave Phase2 Voltage Low",
        0x00002000: "Code 63: Slave Phase2 Voltage High",
        0x00001000: "Code 62: Slave Phase1 Voltage Low",
        0x00000800: "Code 61: Slave Phase1 Voltage High",
        0x00000400: "Code 60: Slave Phase3 DCI Consis Error",
        0x00000200: "Code 59: Slave Phase2 DCI Consis Error",
        0x00000100: "Code 58: Slave Phase1 DCI Consis Error",
        0x00000080: "Code 57: Slave GFCI Consis Error",
        0x00000040: "Code 56: Slave Phase3 Frequency Consis Error",
        0x00000020: "Code 55: Slave Phase2 Frequency Consis Error",
        0x00000010: "Code 54: Slave Phase1 Frequency Consis Error",
        0x00000008: "Code 53: Slave Phase3 Voltage Consis Error",
        0x00000004: "Code 52: Slave Phase2 Voltage Consis Error",
        0x00000002: "Code 51: Slave Phase1 Voltage Consis Error",
        0x00000001: "Code 50: Slave Lost Communication between M<->S",
    },
}

def read_inverter_errors(client: ModbusTcpClient, address: int, count: int) -> list:
    """Read inverter error registers and return the fault messages."""
    try:
        inverter_data = client.read_holding_registers(slave=1, address=address, count=count)
        if inverter_data.isError():
            raise ConnectionException("Error reading registers")
    except ConnectionException as ex:
        logging.error(f'Connecting to device failed: {ex}')
        return []
    return inverter_data.registers

def parse_fault_messages(registers: list[int]) -> str:
    """Parse the fault messages from the registers."""
    faultMsg = []
    faultMsg0 = registers[0] << 16 | registers[1]
    faultMsg1 = registers[2] << 16 | registers[3]
    faultMsg2 = registers[4] << 16 | registers[5]

    logging.info(f"faultMsg {faultMsg0:#010x} {faultMsg1:#010x} {faultMsg2:#010x}")

    for i, msg in enumerate([faultMsg0, faultMsg1, faultMsg2]):
        if msg:
            for code, mesg in FAULT_MESSAGES[i].items():
                if msg & code:
                    faultMsg.append(mesg)

    return ", ".join(faultMsg)

def main() -> None:
    """Main function to read and display inverter error messages."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help="SAJ Inverter IP", type=str, required=True)
    parser.add_argument('--port', help="SAJ Inverter Port", type=int, required=True)
    args = parser.parse_args()

    client = ModbusTcpClient(host=args.host, port=args.port, timeout=3)
    client.connect()

    try:
        registers = read_inverter_errors(client, address=0x0101, count=6)
        if registers:
            error = parse_fault_messages(registers)
            if error:
                logging.info(f"Fault message: {error}")
                print(f"Fault message: {error}")
            else:
                logging.info("No faults")
                print("No faults")
        else:
            logging.error("Failed to read inverter errors")
    finally:
        client.close()

if __name__ == "__main__":
    main()
