import argparse
import json

from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException
from .payload import BinaryPayloadDecoder

parser = argparse.ArgumentParser()

parser.add_argument('--host', help="SAJ Inverter IP",
                    type=str, required=True)
parser.add_argument('--port', help="SAJ Inverter Port",
                    type=int, required=True)

args = parser.parse_args()

address = 36608  # First register with Inverter details.
count = 29  # Read this amount of registers
connected = False
client = ModbusTcpClient(host=args.host, port=args.port, timeout=3)
client.connect()

try:
    inverter_data = client.read_holding_registers(
        slave=1, address=address, count=count)
    connected = True
except ConnectionException as ex:
    print(f'Connecting to device {args.host} failed!')
    connected = False

if connected:
    if not inverter_data.isError():
        decoder = BinaryPayloadDecoder.fromRegisters(
            inverter_data.registers, byteorder=Endian.Big)

        data = {}

        data["devicetype"] = str(decoder.decode_16bit_uint())
        data["subtype"] = str(decoder.decode_16bit_uint())
        data["commver"] = str(round(decoder.decode_16bit_uint() * 0.001, 3))
        data["serialnumber"] = str(decoder.decode_string(20).decode('ascii'))
        data["procuctcode"] = str(decoder.decode_string(20).decode('ascii'))
        data["dispswver"] = str(round(decoder.decode_16bit_uint() * 0.001, 3))
        data["masterctrlver"] = str(
            round(decoder.decode_16bit_uint() * 0.001, 3))
        data["slavecrtlver"] = str(
            round(decoder.decode_16bit_uint() * 0.001, 3))
        data["disphwver"] = str(round(decoder.decode_16bit_uint() * 0.001, 3))
        data["crtlhwver"] = str(round(decoder.decode_16bit_uint() * 0.001, 3))
        data["powerhwver"] = str(round(decoder.decode_16bit_uint() * 0.001, 3))

        json_data = json.dumps(data)
        print(json_data)

client.close()
