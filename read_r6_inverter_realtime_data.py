import argparse
import json
import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DEVICE_STATUSSES = {
    0: "Not Connected",
    1: "Waiting",
    2: "Normal",
    3: "Error",
    4: "Upgrading",
}

def parse_datetime (registers: list[int]) -> str:
    """Extract date and time values from registers."""

    year = registers[0]  # yyyy
    month = registers[1] >> 8  # MM
    day = registers[1] & 0xFF  # dd
    hour = registers[2] >> 8  # HH
    minute = registers[2] & 0xFF  # mm
    second = registers[3] >> 8  # ss
    
    timevalues = f"{year}{month:02}{day:02}{hour:02}{minute:02}{second:02}"
    # Convert to datetime object
    date_time_obj = datetime.astimezone(datetime.strptime(timevalues, '%Y%m%d%H%M%S'))

    logging.debug(f'DatetimeObj: {date_time_obj}')
    # Format to readable string
    readable_date_time = str(date_time_obj.strftime('%Y-%m-%d %H:%M:%S'))
    return(readable_date_time)
    
def read_modbus_data(client, address, count):
    try:
        result = client.read_holding_registers(slave=1, address=address, count=count)
        if result.isError():
            raise ConnectionException("Error reading registers")
        return result.registers
    except ConnectionException as ex:
        logging.error(f'Error reading registers: {ex}')
        return None
        
def convert_to_signed(value):
    """Convert unsigned integers to signed integers."""
    if value >= 0x8000:
        return value - 0x10000
    else:
        return value
            
def parse_registers(registers):
    data = {
        "mpvmode": registers[0],
        "mpvstatus": DEVICE_STATUSSES.get(registers[0], "Unknown"),
        "pv1volt": round(registers[7] * 0.1, 1),
        "pv1curr": round(registers[8] * 0.01, 2),
        "pv1power": round(registers[9] * 1, 0),
        "pv2volt": round(registers[10] * 0.1, 1),
        "pv2curr": round(registers[11] * 0.01, 2),
        "pv2power": round(registers[12] * 1, 0),
        "pv3volt": round(registers[13] * 0.1, 1),
        "pv3curr": round(registers[14] * 0.01, 2),
        "pv3power": round(registers[15] * 1, 0),
        "busvolt": round(registers[16] * 0.1, 1),
        "invtempc": round(registers[17] * 0.1, 1),
        "gfci": convert_to_signed(registers[18]),
        "power": registers[19],
        "qpower": convert_to_signed(registers[20]),
        "pf": round(convert_to_signed(registers[21]) * 0.001, 3),
        "l1volt": round(registers[22] * 0.1, 1),
        "l1curr": round(registers[23] * 0.01, 2),
        "l1freq": round(registers[24] * 0.01, 2),
        "l1dci": convert_to_signed(registers[25]),
        "l1power": registers[26],
        "l1pf": round(convert_to_signed(registers[27]) * 0.001, 3),
        "l2volt": round(registers[28] * 0.1, 1),
        "l2curr": round(registers[29] * 0.01, 2),
        "l2freq": round(registers[30] * 0.01, 2),
        "l2dci": convert_to_signed(registers[31]),
        "l2power": registers[32],
        "l2pf": round(convert_to_signed(registers[33]) * 0.001, 3),
        "l3volt": round(registers[34] * 0.1, 1),
        "l3curr": round(registers[35] * 0.01, 2),
        "l3freq": round(registers[36] * 0.01, 2),
        "l3dci": convert_to_signed(registers[37]),
        "l3power": registers[38],
        "l3pf": round(convert_to_signed(registers[39]) * 0.001, 3),
        "iso1": registers[40],
        "iso2": registers[41],
        "iso3": registers[42],
        "iso4": registers[43],
        "todayenergy": round(registers[44] * 0.01, 2),
        "monthenergy": round((registers[45] << 16 | registers[46]) * 0.01, 2),
        "yearenergy": round((registers[47] << 16 | registers[48]) * 0.01, 2),
        "totalenergy": round((registers[49] << 16 | registers[50]) * 0.01, 2),
        "todayhour": round(registers[51] * 0.1, 1),
        "totalhour": round((registers[52] << 16 | registers[53]) * 0.1, 1),
        "errorcount": registers[54],
        "datetime": parse_datetime(registers[55:60])
    }
    return data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help="SAJ Inverter IP", type=str, required=True)
    parser.add_argument('--port', help="SAJ Inverter Port", type=int, required=True)
    args = parser.parse_args()

    address = 0x100  # First register with Realtime data.
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
