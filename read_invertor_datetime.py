import argparse
import json
import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from pymodbus.pdu import ModbusPDU
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def set_date_and_time(date_time: datetime | None = None) -> None:
    """Set the time and date on the inverter."""
    if date_time is None:
        date_time = datetime.now()

    values = [
        date_time.year,
        (date_time.month << 8) + date_time.day,
        (date_time.hour << 8) + date_time.minute,
        (date_time.second << 8),
    ]

    response = client.write_registers(address=0x8020, values=values,slave=1)
    if response.isError():
        raise ModbusException("Error setting date and time")
    return(response)

def read_date_and_time (registers: list[int]) -> str:
    """Extract date and time values from registers."""
    timedata_data = client.read_holding_registers(slave=1, address=0x0137, count=4)
    if timedata_data.isError():
        raise ConnectionException("Error reading registers")
        
    year = registers[0]  # yyyy
    month = registers[1] >> 8  # MM
    day = registers[1] & 0xFF  # dd
    hour = registers[2] >> 8  # HH
    minute = registers[2] & 0xFF  # mm
    second = registers[3] >> 8  # ss
    
    timevalues = f"{year}{month:02}{day:02}{hour:02}{minute:02}{second:02}"
    # Convert to datetime object
    date_time_obj = datetime.strptime(timevalues, '%Y%m%d%H%M%S')
    
    # Format to readable string
    readable_date_time = str(date_time_obj.strftime('%Y-%m-%d %H:%M:%S'))
    return(readable_date_time)   
     
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help="SAJ Inverter IP", type=str, required=True)
    parser.add_argument('--port', help="SAJ Inverter Port", type=int, required=True)
    args = parser.parse_args()

    data = {"datetime": None}

    try:
        with ModbusTcpClient(host=args.host, port=args.port, timeout=3) as client:
            # Connect to the inverter
            if not client.connect():
                raise ConnectionException(f"Unable to connect to {args.host}:{args.port}")

            data["datetime"] = read_date_and_time()

    except ConnectionException as ex:
        logger.error(f"Connecting to device {args.host} failed: {ex}")

    finally:
        # Convert data to JSON and print
        json_data = json.dumps(data)
        logger.info(json_data)
        print(json_data)

if __name__ == "__main__":
    main()
