import argparse
import json

from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException
from pymodbus.payload import BinaryPayloadDecoder

DEVICE_STATUSSES = {
    0: "Not Connected",
    1: "Waiting",
    2: "Normal",
    3: "Error",
    4: "Upgrading",
}

parser = argparse.ArgumentParser()

parser.add_argument('--host', help="SAJ Inverter IP",
                    type=str, required=True)
parser.add_argument('--port', help="SAJ Inverter Port",
                    type=int, required=True)

args = parser.parse_args()

address = 256  # First register with Realtime data.
count = 60  # Read this amount of registers
connected = False
client = ModbusTcpClient(host=args.host, port=args.port, timeout=3)
client.connect()

try:
    realtime_data = client.read_holding_registers(
        slave=1, address=address, count=count)
    connected = True
except ConnectionException as ex:
    print(f'Connecting to device {args.host} failed!')
    connected = False

if connected:
    if not realtime_data.isError():
        decoder = BinaryPayloadDecoder.fromRegisters(
            realtime_data.registers, byteorder=Endian.Big
        )

        data = {}

        data["mpvmode"] = decoder.decode_16bit_uint()

        if data["mpvmode"] in DEVICE_STATUSSES:
            data["mpvstatus"] = DEVICE_STATUSSES[data["mpvmode"]]
        else:
            data["mpvstatus"] = "Unknown"

        # TODO: read fault message
        # faultmsg = decoder.decode_16bit_uint()
        # skip 6 registers
        decoder.skip_bytes(12)

        data["pv1volt"] = round(decoder.decode_16bit_uint() * 0.1, 1)
        data["pv1curr"] = round(decoder.decode_16bit_uint() * 0.01, 2)
        data["pv1power"] = round(decoder.decode_16bit_uint() * 1, 0)

        data["pv2volt"] = round(decoder.decode_16bit_uint() * 0.1, 1)
        data["pv2curr"] = round(decoder.decode_16bit_uint() * 0.01, 2)
        data["pv2power"] = round(decoder.decode_16bit_uint() * 1, 0)

        data["pv3volt"] = round(decoder.decode_16bit_uint() * 0.1, 1)
        data["pv3curr"] = round(decoder.decode_16bit_uint() * 0.01, 2)
        data["pv3power"] = round(decoder.decode_16bit_uint() * 1, 0)

        data["busvolt"] = round(decoder.decode_16bit_uint() * 0.1, 1)

        data["invtempc"] = round(decoder.decode_16bit_uint() * 0.1, 1)

        data["gfci"] = decoder.decode_16bit_uint()

        data["power"] = decoder.decode_16bit_uint()

        data["qpower"] = decoder.decode_16bit_uint()

        data["pf"] = round(decoder.decode_16bit_uint() * 0.001, 3)

        data["l1volt"] = round(decoder.decode_16bit_uint() * 0.1, 1)
        data["l1curr"] = round(decoder.decode_16bit_uint() * 0.01, 2)
        data["l1freq"] = round(decoder.decode_16bit_uint() * 0.01, 2)
        data["l1dci"] = decoder.decode_16bit_uint()
        data["l1power"] = decoder.decode_16bit_uint()
        data["l1pf"] = round(decoder.decode_16bit_uint() * 0.001, 3)

        data["l2volt"] = round(decoder.decode_16bit_uint() * 0.1, 1)
        data["l2curr"] = round(decoder.decode_16bit_uint() * 0.01, 2)
        data["l2freq"] = round(decoder.decode_16bit_uint() * 0.01, 2)
        data["l2dci"] = decoder.decode_16bit_uint()
        data["l2power"] = decoder.decode_16bit_uint()
        data["l2pf"] = round(decoder.decode_16bit_uint() * 0.001, 3)

        data["l3volt"] = round(decoder.decode_16bit_uint() * 0.1, 1)
        data["l3curr"] = round(decoder.decode_16bit_uint() * 0.01, 2)
        data["l3freq"] = round(decoder.decode_16bit_uint() * 0.01, 2)
        data["l3dci"] = decoder.decode_16bit_uint()
        data["l3power"] = decoder.decode_16bit_uint()
        data["l3pf"] = round(decoder.decode_16bit_uint() * 0.001, 3)

        data["iso1"] = decoder.decode_16bit_uint()
        data["iso2"] = decoder.decode_16bit_uint()
        data["iso3"] = decoder.decode_16bit_uint()
        data["iso4"] = decoder.decode_16bit_uint()

        data["todayenergy"] = round(decoder.decode_16bit_uint() * 0.01, 2)
        data["monthenergy"] = round(decoder.decode_32bit_uint() * 0.01, 2)
        data["yearenergy"] = round(decoder.decode_32bit_uint() * 0.01, 2)
        data["totalenergy"] = round(decoder.decode_32bit_uint() * 0.01, 2)

        data["todayhour"] = round(decoder.decode_16bit_uint() * 0.1, 1)
        data["totalhour"] = round(decoder.decode_32bit_uint() * 0.1, 1)

        data["errorcount"] = decoder.decode_16bit_uint()

        json_data = json.dumps(data)
        print(json_data)

client.close()
