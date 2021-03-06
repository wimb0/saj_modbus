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

address = 256 # First register with Realtime data.
count = 60
connected = False
client = ModbusTcpClient(host=args.host, port=args.port, timeout=5)
client.connect()

try:
    inverter_data = client.read_holding_registers(
        unit=1, address=address, count=count)
    connected = True
except ConnectionException as ex:
    print(f'Connecting to device {args.host} failed!')
    connected = False

def read_modbus_realtime_data(self):
    realtime_data = self.read_holding_registers(
        unit=1, address=256, count=60)
    if not realtime_data.isError():
        decoder = BinaryPayloadDecoder.fromRegisters(
            realtime_data.registers, byteorder=Endian.Big
        )

        mpvmode = decoder.decode_16bit_uint()
        self.data["mpvmode"] = mpvmode

        #if mpvmode in DEVICE_STATUSSES:
        #    self.data["mpvstatus"] = DEVICE_STATUSSES[mpvmode]
        #else:
        #    self.data["mpvstatus"] = "Unknown"

        # TODO: read fault message
        # faultmsg = decoder.decode_16bit_uint()
        # skip 6 registers
        decoder.skip_bytes(12)

        pv1volt = decoder.decode_16bit_uint()
        pv1curr = decoder.decode_16bit_uint()
        pv1power = decoder.decode_16bit_uint()
        self.data["pv1volt"] = round(pv1volt * 0.1, 1)
        self.data["pv1curr"] = round(pv1curr * 0.01, 2)
        self.data["pv1power"] = round(pv1power * 1, 0)

        pv2volt = decoder.decode_16bit_uint()
        pv2curr = decoder.decode_16bit_uint()
        pv2power = decoder.decode_16bit_uint()
        self.data["pv2volt"] = round(pv2volt * 0.1, 1)
        self.data["pv2curr"] = round(pv2curr * 0.01, 2)
        self.data["pv2power"] = round(pv2power * 1, 0)

        pv3volt = decoder.decode_16bit_uint()
        pv3curr = decoder.decode_16bit_uint()
        pv3power = decoder.decode_16bit_uint()
        self.data["pv3volt"] = round(pv3volt * 0.1, 1)
        self.data["pv3curr"] = round(pv3curr * 0.01, 2)
        self.data["pv3power"] = round(pv3power * 1, 0)

        busvolt = decoder.decode_16bit_uint()
        self.data["busvolt"] = round(busvolt * 0.1, 1)

        invtempc = decoder.decode_16bit_int()
        self.data["invtempc"] = round(invtempc * 0.1, 1)

        gfci = decoder.decode_16bit_int()
        self.data["gfci"] = gfci

        power = decoder.decode_16bit_uint()
        self.data["power"] = power

        qpower = decoder.decode_16bit_int()
        self.data["qpower"] = qpower

        pf = decoder.decode_16bit_int()
        self.data["pf"] = round(pf * 0.001, 3)

        l1volt = decoder.decode_16bit_uint()
        l1curr = decoder.decode_16bit_uint()
        l1freq = decoder.decode_16bit_uint()
        l1dci = decoder.decode_16bit_int()
        l1power = decoder.decode_16bit_uint()
        l1pf = decoder.decode_16bit_int()
        self.data["l1volt"] = round(l1volt * 0.1, 1)
        self.data["l1curr"] = round(l1curr * 0.01, 2)
        self.data["l1freq"] = round(l1freq * 0.01, 2)
        self.data["l1dci"] = l1dci
        self.data["l1power"] = l1power
        self.data["l1pf"] = round(l1pf * 0.001, 3)

        l2volt = decoder.decode_16bit_uint()
        l2curr = decoder.decode_16bit_uint()
        l2freq = decoder.decode_16bit_uint()
        l2dci = decoder.decode_16bit_int()
        l2power = decoder.decode_16bit_uint()
        l2pf = decoder.decode_16bit_int()
        self.data["l2volt"] = round(l2volt * 0.1, 1)
        self.data["l2curr"] = round(l2curr * 0.01, 2)
        self.data["l2freq"] = round(l2freq * 0.01, 2)
        self.data["l2dci"] = l2dci
        self.data["l2power"] = l2power
        self.data["l2pf"] = round(l2pf * 0.001, 3)

        l3volt = decoder.decode_16bit_uint()
        l3curr = decoder.decode_16bit_uint()
        l3freq = decoder.decode_16bit_uint()
        l3dci = decoder.decode_16bit_int()
        l3power = decoder.decode_16bit_uint()
        l3pf = decoder.decode_16bit_int()
        self.data["l3volt"] = round(l3volt * 0.1, 1)
        self.data["l3curr"] = round(l3curr * 0.01, 2)
        self.data["l3freq"] = round(l3freq * 0.01, 2)
        self.data["l3dci"] = l3dci
        self.data["l3power"] = l3power
        self.data["l3pf"] = round(l3pf * 0.001, 3)

        iso1 = decoder.decode_16bit_uint()
        iso2 = decoder.decode_16bit_uint()
        iso3 = decoder.decode_16bit_uint()
        iso4 = decoder.decode_16bit_uint()
        self.data["iso1"] = iso1
        self.data["iso2"] = iso2
        self.data["iso3"] = iso3
        self.data["iso4"] = iso4

        todayenergy = decoder.decode_16bit_uint()
        monthenergy = decoder.decode_32bit_uint()
        yearenergy = decoder.decode_32bit_uint()
        totalenergy = decoder.decode_32bit_uint()
        self.data["todayenergy"] = round(todayenergy * 0.01, 2)
        self.data["monthenergy"] = round(monthenergy * 0.01, 2)
        self.data["yearenergy"] = round(yearenergy * 0.01, 2)
        self.data["totalenergy"] = round(totalenergy * 0.01, 2)

        todayhour = decoder.decode_16bit_uint()
        self.data["todayhour"] = round(todayhour * 0.1, 1)
        totalhour = decoder.decode_32bit_uint()
        self.data["totalhour"] = round(totalhour * 0.1, 1)

        errorcount = decoder.decode_16bit_uint()
        self.data["errorcount"] = errorcount

        return True
    else:
        return False


read_modbus_realtime_data()