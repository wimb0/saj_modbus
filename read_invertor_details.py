import argparse
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException
from pymodbus.payload import BinaryPayloadDecoder

parser = argparse.ArgumentParser()

parser.add_argument('--host', help="SAJ Inverter IP",
                    type=str, required=True)
parser.add_argument('--port', help="SAJ Inverter Port",
                    type=int, required=True)

args = parser.parse_args()

address = 36608 # First register with Inverter details.
count = 29
connected = False
client = ModbusTcpClient(host=args.host, port=args.port, timeout=5)
client.connect()

try:
    inverter_data = client.read_holding_registers(
        unit=1, address=address, count=count)
    connected = True
except ConnectionException as ex:
    print(f'Connecting to device {host_ip} failed!')
    connected = False

if connected:
    if not inverter_data.isError():
        decoder = BinaryPayloadDecoder.fromRegisters(
            inverter_data.registers, byteorder=Endian.Big)
        print("Device Type: " + str(decoder.decode_16bit_uint()))
        print("Sub Type: " + str(decoder.decode_16bit_uint()))
        print("Comms Protocol Version: " +
              str(round(decoder.decode_16bit_uint() * 0.001, 3)))
        sn = decoder.decode_string(20).decode('ascii')
        print("Serial Number: " + str(sn))
        pc = decoder.decode_string(20).decode('ascii')
        print("Product Code: " + str(pc))
        print("Display Software Version: " +
              str(round(decoder.decode_16bit_uint() * 0.001, 3)))
        print("Master Ctrl Software Version: " +
              str(round(decoder.decode_16bit_uint() * 0.001, 3)))
        print("Slave Ctrl Software Version: " +
              str(round(decoder.decode_16bit_uint() * 0.001, 3)))
        print("Display Board Hardware Version: " +
              str(round(decoder.decode_16bit_uint() * 0.001, 3)))
        print("Control Board HW Version: " +
              str(round(decoder.decode_16bit_uint() * 0.001, 3)))
        print("Power Board Hardware Version: " +
              str(round(decoder.decode_16bit_uint() * 0.001, 3)))

client.close()
