import argparse
import json
import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

logging.basicConfig(level=logging.INFO)

DEVICE_STATUSSES = {
    0: "Not Connected",
    1: "Waiting",
    2: "Normal",
    3: "Error",
    4: "Upgrading",
}

def read_modbus_data(client, address, count):
    try:
        result = client.read_holding_registers(slave=1, address=address, count=count)
        if result.isError():
            raise ConnectionException("Error reading registers")
        return result.registers
    except ConnectionException as ex:
        logging.error(f'Error reading registers: {ex}')
        return None

def parse_registers(registers):
    data = {
        "mpvmode": registers[0],
        "mpvstatus": DEVICE_STATUSSES.get(registers[0], "Unknown"),
        "pv1volt": round(registers[7] * 0.1, 1),
        "pv1curr": round(registers[8] * 0.01, 2),
        "pv1power": round(registers[9] * 1, 0),
        "pv2volt": round(registers[9] * 0.1, 1),
        "pv2curr": round(registers[10] * 0.01, 2),
        "pv2power": round(registers[11] * 1, 0),
        "pv3volt": round(registers[12] * 0.1, 1),
        "pv3curr": round(registers[13] * 0.01, 2),
        "pv3power": round(registers[14] * 1, 0),
        "busvolt": round(registers[15] * 0.1, 1),
        "invtempc": round(registers[16] * 0.1, 1),
        "gfci": registers[17],
        "power": registers[18],
        "qpower": registers[19],
        "pf": round(registers[20] * 0.001, 3),
        "l1volt": round(registers[21] * 0.1, 1),
        "l1curr": round(registers[22] * 0.01, 2),
        "l1freq": round(registers[23] * 0.01, 2),
        "l1dci": registers[24],
        "l1power": registers[25],
        "l1pf": round(registers[26] * 0.001, 3),
        "l2volt": round(registers[27] * 0.1, 1),
        "l2curr": round(registers[28] * 0.01, 2),
        "l2freq": round(registers[29] * 0.01, 2),
        "l2dci": registers[30],
        "l2power": registers[31],
        "l2pf": round(registers[32] * 0.001, 3),
        "l3volt": round(registers[33] * 0.1, 1),
        "l3curr": round(registers[34] * 0.01, 2),
        "l3freq": round(registers[35] * 0.01, 2),
        "l3dci": registers[36],
        "l3power": registers[37],
        "l3pf": round(registers[38] * 0.001, 3),
        "iso1": registers[39],
        "iso2": registers[40],
        "iso3": registers[41],
        "iso4": registers[42],
        "todayenergy": round(registers[43] * 0.01, 2),
        "monthenergy": round((registers[44] << 16 | registers[45]) * 0.01, 2),
        "yearenergy": round((registers[46] << 16 | registers[47]) * 0.01, 2),
        "totalenergy": round((registers[48] << 16 | registers[49]) * 0.01, 2),
        "todayhour": round(registers[50] * 0.1, 1),
        "totalhour": round((registers[51] << 16 | registers[52]) * 0.1, 1),
        "errorcount": registers[53]
    }
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help="SAJ Inverter IP", type=str, required=True)
    parser.add_argument('--port', help="SAJ Inverter Port", type=int, required=True)
    args = parser.parse_args()

    address = 256  # First register with Realtime data.
    count = 60  # Read this amount of registers

    client = ModbusTcpClient(host=args.host, port=args.port, timeout=3)
    if not client.connect():
        logging.error(f'Failed to connect to {args.host}:{args.port}')
        return

    registers = read_modbus_data(client, address, count)
    client.close()

    if registers:
        data = parse_registers(registers)
        json_data = json.dumps(data)
        print(json_data)

if __name__ == "__main__":
    main()
